#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\standingsvc.py
import types
import blue
import uthread
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.standings import standingsUIUtil
from eve.common.lib import appConst
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.util.standingUtil import ApplyBonusToStanding, CalculateNewStandings, CalculateStandingsByRawChange
from localization import GetByLabel

class Standing(Service):
    __notifyevents__ = ['OnStandingSet', 'OnStandingsModified', 'ProcessSessionChange']
    __guid__ = 'svc.standing'
    __servicename__ = 'standing'
    __displayname__ = 'Standing Service'

    def Run(self, memStream = None):
        self.npccorpstandings = {}
        self.npccharstandings = {}
        self.npcnpcstandingsto = {}
        self.npcnpcstandingsfrom = {}
        self.unreadStandingEntries = {}
        self.standingTransactionCache = {}
        self.fromStandingHeader = blue.DBRowDescriptor((('fromID', appConst.DBTYPE_I4), ('standing', appConst.DBTYPE_R5)))
        self.__RefreshStandings()

    def Stop(self, memStream = None):
        pass

    def OnStandingSet(self, fromID, toID, standing):
        self.CheckInvalidateTransactionCache(fromID, toID)
        if idCheckers.IsNPC(fromID):
            if toID == session.charid:
                if not standing:
                    if fromID in self.npccharstandings:
                        if session.warfactionid:
                            sm.ScatterEvent('OnNPCStandingChange', fromID, 0.0, self.npccharstandings[fromID].standing)
                        del self.npccharstandings[fromID]
                else:
                    oldStanding = 0.0
                    if fromID in self.npccharstandings:
                        oldStanding = self.npccharstandings[fromID].standing
                    if session.warfactionid:
                        sm.ScatterEvent('OnNPCStandingChange', fromID, standing, oldStanding)
                    self._AppendNPCCharStanding(fromID, standing)
            elif toID == session.corpid:
                if not standing:
                    if fromID in self.npccorpstandings:
                        del self.npccorpstandings[fromID]
                else:
                    self.npccorpstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, standing])

    def OnStandingsModified(self, modifications):
        for modification in modifications:
            fromID, toID, rawChange, minAbs, maxAbs = modification
            self.CheckInvalidateTransactionCache(fromID, toID)
            if toID == session.charid:
                self._ModifyCharacterStandings(fromID, rawChange)
                self.AddToUnreadEntries(fromID, rawChange)
            elif toID == session.corpid:
                self._ModifyCorporationStandings(fromID, rawChange)

    def _ModifyCharacterStandings(self, fromID, rawChange):
        if fromID in self.npccharstandings:
            new_standings_value = CalculateStandingsByRawChange(currentStanding=self.npccharstandings[fromID].standing, rawChange=rawChange)
            sm.ScatterEvent('OnNPCStandingChange', fromID, new_standings_value, self.npccharstandings[fromID].standing)
            self.npccharstandings[fromID].standing = new_standings_value
        else:
            new_standings_value = CalculateNewStandings(rawChange)
            self._AppendNPCCharStanding(fromID, new_standings_value)

    def _AppendNPCCharStanding(self, fromID, standing):
        self.npccharstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, standing])

    def _ModifyCorporationStandings(self, fromID, rawChange):
        if fromID in self.npccorpstandings:
            new_standings_value = CalculateStandingsByRawChange(currentStanding=self.npccharstandings[fromID].standing, rawChange=rawChange)
            self.npccorpstandings[fromID].standing = new_standings_value
        else:
            new_standings_value = CalculateNewStandings(rawChange)
            self.npccorpstandings[fromID] = blue.DBRow(self.fromStandingHeader, [fromID, new_standings_value])

    def CanUseAgent(self, factionID, corporationID, agentID, level, agentTypeID):
        faction_standing = self.npccharstandings[factionID].standing if factionID in self.npccharstandings else 0.0
        corporation_standing = self.npccharstandings[corporationID].standing if corporationID in self.npccharstandings else 0.0
        character_standing = self.npccharstandings[agentID].standing if agentID in self.npccharstandings else 0.0
        return eveCfg.CanUseAgent(level, agentTypeID, faction_standing, corporation_standing, character_standing, corporationID, factionID, {})

    def ProcessSessionChange(self, isRemote, session, change):
        if 'charid' in change and change['charid'][1] or 'corpid' in change and change['corpid'][1]:
            self.__RefreshStandings()

    def __RefreshStandings(self):
        if not session.charid:
            return
        standingsMgr = sm.RemoteSvc('standingMgr')
        tmp = standingsMgr.GetNPCNPCStandings()
        self.npcnpcstandingsto = tmp.Filter('toID')
        self.npcnpcstandingsfrom = tmp.Filter('fromID')
        if idCheckers.IsNPC(session.corpid):
            self.npccharstandings = standingsMgr.GetCharStandings()
            self.npccorpstandings = {}
        else:
            ret = uthread.parallel([(standingsMgr.GetCharStandings, ()), (standingsMgr.GetCorpStandings, ())])
            self.npccharstandings = ret[0]
            self.npccorpstandings = ret[1]
        if not isinstance(self.npccorpstandings, types.DictType):
            self.npccorpstandings = self.npccorpstandings.Index('fromID')
        if not isinstance(self.npccharstandings, types.DictType):
            self.npccharstandings = self.npccharstandings.Index('fromID')
        for factionID in appConst.factions:
            if factionID not in self.npccharstandings and factionID == appConst.factionByRace[session.raceID]:
                self._AppendNPCCharStanding(factionID, 0.0)

    def AppendZeroStandingIfNeeded(self, ownerID):
        if ownerID not in self.npccharstandings:
            self._AppendNPCCharStanding(ownerID, 0.0)
            return True
        return False

    def GetStanding(self, fromID, toID):
        relationship = None
        standing = None
        if fromID == session.charid:
            relationship = sm.GetService('addressbook').GetContacts().contacts.get(toID, None)
        elif fromID == session.corpid and not idCheckers.IsNPC(session.corpid):
            relationship = sm.GetService('addressbook').GetContacts().corpContacts.get(toID, None)
        elif fromID == session.allianceid:
            relationship = sm.GetService('addressbook').GetContacts().allianceContacts.get(toID, None)
        elif toID == session.charid:
            if idCheckers.IsNPC(fromID) and fromID in self.npccharstandings:
                standing = self.npccharstandings[fromID]
        elif toID == session.corpid and not idCheckers.IsNPC(session.corpid):
            if idCheckers.IsNPC(fromID) and fromID in self.npccorpstandings:
                standing = self.npccorpstandings[fromID]
        elif idCheckers.IsNPC(fromID) and idCheckers.IsNPC(toID) and fromID in self.npcnpcstandingsfrom:
            for each in self.npcnpcstandingsfrom[fromID]:
                if each.toID == toID:
                    standing = each
                    break

        if standing is not None:
            ret = standing.standing
        elif relationship is not None:
            ret = relationship.relationshipID
        else:
            ret = appConst.contactNeutralStanding
        return ret

    def GetStandingTransactions(self, fromID, toID):
        key = (fromID, toID)
        if key not in self.standingTransactionCache:
            transactions = sm.RemoteSvc('standingMgr').GetStandingTransactions(fromID, toID)
            for each in transactions:
                each.modification = float(each.modification * 10.0)

            self.standingTransactionCache[key] = transactions
        return self.standingTransactionCache[key][:]

    def CheckInvalidateTransactionCache(self, fromID, toID):
        if (fromID, toID) in self.standingTransactionCache:
            self.standingTransactionCache.pop((fromID, toID))

    def GetStandingWithSkillBonus(self, fromID, toID):
        standing = self.GetStanding(fromID, toID) or 0.0
        bonus = standingsUIUtil.GetStandingSkillBonus(standing, fromID, toID)
        return ApplyBonusToStanding(bonus, standing)

    def GetStandingWithSkillBonusFromValue(self, standingValue, fromID, toID):
        bonus = standingsUIUtil.GetStandingSkillBonus(standingValue, fromID, toID)
        return ApplyBonusToStanding(bonus, standingValue)

    def GetEffectiveStandingWithAgent(self, agentID, getLabel = True):
        characterID = session.charid
        agentInfo = sm.GetService('agents').GetAgentByID(agentID)
        standings = [self.GetStandingWithSkillBonus(agentInfo.factionID, characterID), self.GetStandingWithSkillBonus(agentInfo.corporationID, characterID), self.GetStandingWithSkillBonus(agentInfo.agentID, characterID)]
        if min(*standings) <= -2.0:
            value = min(*standings)
            label_path = 'UI/Agents/Dialogue/EffectiveStandingLow'
        else:
            value = max(*standings) or 0.0
            label_path = 'UI/Agents/Dialogue/EffectiveStanding'
        label = GetByLabel(label_path, effectiveStanding=value)
        return (float(value), label)

    def AddToEffectiveStandingWithAgent(self, standingGains, agentID):
        newStandingsWithBonus, _ = self.GetNewAndCurrentStandings(standingGains, agentID)
        standing_values = newStandingsWithBonus.values()
        min_standing = min(standing_values)
        if min_standing <= -2.0:
            return min_standing
        else:
            max_standing = max(standing_values)
            return max_standing or 0.0

    def GetNewAndCurrentStandings(self, standingGains, agentID):
        characterID = session.charid
        agentInfo = sm.GetService('agents').GetAgentByID(agentID)
        factionID = agentInfo.factionID
        corporationID = agentInfo.corporationID
        currentStandings = {factionID: self.GetStanding(factionID, characterID) or 0.0,
         corporationID: self.GetStanding(corporationID, characterID) or 0.0,
         agentID: self.GetStanding(agentID, characterID) or 0.0}
        rawStandings = currentStandings.copy()
        for fromID, standingGain in standingGains.iteritems():
            rawStandings[fromID] += standingGain

        standingsWithBonus = {factionID: self.GetStandingWithSkillBonusFromValue(rawStandings[factionID], factionID, characterID),
         corporationID: self.GetStandingWithSkillBonusFromValue(rawStandings[corporationID], corporationID, characterID),
         agentID: self.GetStandingWithSkillBonusFromValue(rawStandings[agentID], agentID, characterID)}
        return (standingsWithBonus, currentStandings)

    def GetStandingsDataNPCsToMyCharacter(self):
        standings = []
        for npcID in self.npccharstandings:
            standings.append((npcID, self.npccharstandings[npcID].standing))

        cfg.eveowners.Prime([ standing[0] for standing in standings ])
        return standings

    def GetStandingsDataNPCsToMyCorp(self):
        standings = []
        corpIDs = []
        for npcID in self.npccorpstandings:
            if idCheckers.IsCorporation(npcID):
                corpIDs.append(npcID)
            standings.append((npcID, self.npccorpstandings[npcID].standing))

        cfg.corptickernames.Prime(corpIDs)
        cfg.eveowners.Prime([ standing[0] for standing in standings ])
        return standings

    def AddToUnreadEntries(self, ownerID, standingsChange):
        self.unreadStandingEntries[ownerID] = standingsChange

    def RemoveFromUnreadEntries(self, ownerID):
        if ownerID in self.unreadStandingEntries:
            del self.unreadStandingEntries[ownerID]

    def FlushUnreadEntries(self):
        self.unreadStandingEntries.clear()

    def GetUnreadEntries(self):
        return self.unreadStandingEntries

    def GetStandingCompositions(self, fromID, toID):
        return sm.RemoteSvc('standingMgr').GetStandingCompositions(fromID, toID)
