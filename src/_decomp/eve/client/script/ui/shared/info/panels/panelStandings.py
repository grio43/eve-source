#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelStandings.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from characterdata.factions import iter_faction_ids
from eve.client.script.ui.shared.standings.standingData import StandingData
from eve.client.script.ui.shared.standings.standingsSection import StandingsSection
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from localization import GetByLabel
from npcs.npccorporations import get_corporation_faction_id

class PanelStandings(Container):
    default_name = 'PanelStandings'
    default_padLeft = 4
    default_padRight = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ownerID = attributes.ownerID
        self.isInitialized = False
        self.scrollContainer = ScrollContainer(parent=self)

    def Load(self):
        if self.isInitialized:
            return
        self.ConstructPanel()
        self.isInitialized = True

    def ConstructPanel(self):
        for captionText, ownerID, standingsData in self.GetStandingsDataSections():
            self.AddStandingsSection(captionText, ownerID, standingsData)

    def AddStandingsSection(self, captionText, ownerID, standingsData):
        StandingsSection(parent=self.scrollContainer, align=uiconst.TOTOP, text=captionText, ownerID=ownerID, padBottom=4, standingsData=standingsData)

    def GetStandingsDataSections(self):
        if idCheckers.IsNPC(self.ownerID):
            return self.GetStandingsDataSectionsNPC(self.ownerID)
        else:
            return self.GetStandingsDataSectionsPlayerOwner(self.ownerID)

    def GetStandingsDataSectionsNPC(self, ownerID):
        fromIDs = self.GetFromIDsForNPCOwner(ownerID)
        standingsTowardsMe = self.GetStandingsFromManyToOneRightToLeft(fromIDs, session.charid)
        ret = [(GetByLabel('UI/Standings/StandingsTowardsMe'), session.charid, standingsTowardsMe)]
        if idCheckers.IsFaction(ownerID):
            fromIDs = self.GetNPCFactionIDs()
            standingsToOtherFactions = self.GetStandingsFromManyToOneMutual(fromIDs, ownerID)
            ret.append((GetByLabel('UI/Standings/StandingsTowardsOtherFactions'), ownerID, standingsToOtherFactions))
        return ret

    def GetStandingsDataSectionsPlayerOwner(self, ownerID):
        fromIDs = [session.charid]
        if session.corpid and not idCheckers.IsNPC(session.corpid):
            fromIDs.append(session.corpid)
        if session.allianceid and not idCheckers.IsNPC(session.allianceid):
            fromIDs.append(session.allianceid)
        toIDs = self.GetToIDsForPlayerOwner(ownerID)
        return [ self._GetDataSection(fromIDs, toID) for toID in toIDs ]

    def _GetDataSection(self, fromIDs, toID):
        standingsTowards = self.GetStandingsFromManyToOneLeftToRight(fromIDs, toID)
        towards = ('My Standings Towards %s' % cfg.eveowners.Get(toID).ownerName, toID, standingsTowards)
        return towards

    def GetNPCFactionIDs(self):
        return [ factionID for factionID in iter_faction_ids() if factionID != appConst.factionUnknown ]

    def GetStandingsFromManyToOneMutual(self, fromIDs, ownerID1):
        return [ StandingData(ownerID1=ownerID1, ownerID2=ownerID2, standing1to2=self._GetStanding(ownerID1, ownerID2), standing2to1=self._GetStanding(ownerID2, ownerID1)) for ownerID2 in fromIDs if ownerID1 != ownerID2 ]

    def GetStandingsFromManyToOneRightToLeft(self, fromIDs, ownerID1):
        return [ StandingData(ownerID1=ownerID1, ownerID2=ownerID2, standing2to1=self._GetStanding(ownerID2, ownerID1)) for ownerID2 in fromIDs ]

    def GetStandingsFromManyToOneLeftToRight(self, fromIDs, ownerID2):
        return [ StandingData(ownerID1=ownerID1, ownerID2=ownerID2, standing1to2=self._GetStanding(ownerID1, ownerID2)) for ownerID1 in fromIDs ]

    def _GetStanding(self, fromID, toID):
        return sm.GetService('standing').GetStanding(fromID, toID)

    def GetFromIDsForNPCOwner(self, ownerID):
        if idCheckers.IsFaction(ownerID):
            fromIDs = (self.ownerID,)
        elif idCheckers.IsCorporation(ownerID):
            factionID = get_corporation_faction_id(ownerID)
            if factionID:
                fromIDs = (ownerID, factionID)
            else:
                fromIDs = (ownerID,)
        elif sm.GetService('agents').GetAgentByID(ownerID):
            agent = sm.GetService('agents').GetAgentByID(ownerID)
            agentFactionID = agent.factionID
            agentCorpID = agent.corporationID
            fromIDs = (ownerID, agentCorpID, agentFactionID)
        else:
            fromIDs = (ownerID,)
        return fromIDs

    def GetToIDsForPlayerOwner(self, ownerID):
        ret = [ownerID]
        if idCheckers.IsCharacter(ownerID):
            publicInfo = sm.RemoteSvc('charMgr').GetPublicInfo(ownerID)
            ownerCorpID = publicInfo.corporationID
            if not idCheckers.IsNPC(ownerCorpID):
                ret.append(ownerCorpID)
            ownerAllianceID = self._GetOwnerAllianceID(ownerCorpID)
            if ownerAllianceID:
                ret.append(ownerAllianceID)
        elif idCheckers.IsCorporation(ownerID):
            ownerAllianceID = self._GetOwnerAllianceID(ownerID)
            if ownerAllianceID:
                ret.append(ownerAllianceID)
        return ret

    def _GetOwnerAllianceID(self, ownerCorpID):
        if not idCheckers.IsNPC(ownerCorpID):
            return sm.GetService('corp').GetCorporation(ownerCorpID).allianceID
