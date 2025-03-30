#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\facWarSvc.py
import sys
import gametime
import carbonui.const as uiconst
import localization
import utillib
from carbon.common.script.sys.service import Service
from eve.client.script.ui.util.uix import GetLightYearDistance
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsNPC, IsPlayerCorporation
from eve.common.script.sys.rowset import IndexRowset
from eve.common.script.util import facwarCommon
from eveexceptions import UserError
from eve.common.script.util.facwarCommon import GetFwFactionIDForNpcCorp, GetAllFWFactions, IsAnyFWFaction, IsCombatEnemyFaction, IsOccupierFWFaction, IsFwNpcCorp
from npcs.npccorporations import get_corporation_faction_id
import eve.common.lib.appConst as appConst

class FactionalWarfare(Service):
    __exportedcalls__ = {'JoinFactionAsAlliance': [],
     'JoinFactionAsCorporation': [],
     'JoinFactionAsCharacter': [],
     'LeaveFactionAsCorporation': [],
     'LeaveFactionAsAlliance': [],
     'WithdrawJoinFactionAsAlliance': [],
     'WithdrawJoinFactionAsCorporation': [],
     'WithdrawLeaveFactionAsAlliance': [],
     'WithdrawLeaveFactionAsCorporation': [],
     'GetCorpFactionalWarStatus': [],
     'GetCorporationWarFactionID': [],
     'GetFactionCorporations': [],
     'GetFactionMilitiaCorporation': [],
     'GetCharacterRankInfo': [],
     'GetStats_FactionInfo': [],
     'GetStats_Personal': [],
     'GetStats_Corp': [],
     'GetStats_Alliance': [],
     'GetStats_CorpPilots': [],
     'GetMostDangerousSystems': [],
     'CheckForSafeSystem': [],
     'GetAllianceWarFactionID': [],
     'CheckOwnerInFaction': []}
    __guid__ = 'svc.facwar'
    __servicename__ = 'facwar'
    __displayname__ = 'Factional Warfare'
    __notifyevents__ = ['OnNPCStandingChange', 'OnSolarSystemLPChange', 'OnSessionChanged']
    __dependencies__ = ['loyaltyPointsWalletSvc']

    def __init__(self):
        Service.__init__(self)
        self.warFactionByOwner = {}
        self.topStats = None
        self.remoteFacWarMgr = None
        self.solarSystemLPs = {}

    def Run(self, memStream = None):
        self.LogInfo('Starting Factional Warfare Svc')
        self.objectCaching = sm.GetService('objectCaching')

    @property
    def facWarMgr(self):
        if self.remoteFacWarMgr is None:
            self.remoteFacWarMgr = sm.RemoteSvc('facWarMgr')
        return self.remoteFacWarMgr

    def OnSolarSystemLPChange(self, oldpoints, newpoints):
        self.LogInfo('OnSolarSystemLPChange: ', oldpoints, newpoints)
        self.solarSystemLPs[session.solarsystemid2] = newpoints
        sm.GetService('infoPanel').UpdateFactionalWarfarePanel()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'warfactionid' in change:
            self._RefreshCache()

    def GetSolarSystemUpgradeLevel(self, solarsystemID):
        if solarsystemID in self.solarSystemLPs:
            points = self.solarSystemLPs[solarsystemID]
            return facwarCommon.GetLPUpgradeLevel(points)
        else:
            factionID = self.GetSystemOccupier(solarsystemID)
            if IsOccupierFWFaction(factionID):
                warZoneInfo = self.GetFacWarZoneInfo(factionID)
                return warZoneInfo.systemUpgradeLevel.get(solarsystemID, None)
            return None

    def GetMostDangerousSystems(self):
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatFacWarKills, 24)
        dangerousSystems = []
        for each in historyDB:
            if each.value1 - each.value2 > 0:
                dangerousSystems.append(utillib.KeyVal(solarSystemID=each.solarSystemID, numKills=each.value1 - each.value2))

        dangerousSystems.sort(lambda x, y: cmp(y.numKills, x.numKills))
        return dangerousSystems

    def GetCorporationWarFactionID(self, corpID):
        if idCheckers.IsNPC(corpID):
            factionID = GetFwFactionIDForNpcCorp(corpID)
            if factionID:
                return factionID
            return None
        ret = self.facWarMgr.GetCorporationWarFactionID(corpID)
        if not ret:
            return None
        return ret

    def GetFactionCorporations(self, factionID):
        return self.facWarMgr.GetFactionCorporations(factionID)

    def GetAllianceWarFactionID(self, allianceID):
        return self.facWarMgr.GetAllianceWarFactionID(allianceID)

    def GetFactionIDByRaceID(self, raceID):
        return appConst.factionByRace.get(raceID, None)

    def GetSolarSystemsOccupiedByFactions(self, factionIDs):
        fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        occupationStatesBySolarsystemByWarzone = fwWarzoneSvc.GetAllOccupationStates()
        occupierBySolarsystem = {}
        for occupationStatesBySolarsystem in occupationStatesBySolarsystemByWarzone.itervalues():
            for solarsystemID, occupationState in occupationStatesBySolarsystem.iteritems():
                if occupationState.occupierID in factionIDs:
                    occupierBySolarsystem[solarsystemID] = occupationState.occupierID

        return occupierBySolarsystem

    def GetSystemOccupier(self, solarSystemID):
        fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        occupationState = fwWarzoneSvc.GetOccupationState(solarSystemID)
        if occupationState is not None:
            return occupationState.occupierID

    def GetFactionWars(self, ownerID):
        warFactionID = self.GetCorporationWarFactionID(ownerID)
        factionWars = self.GetFactionWarsForWarFactionID(warFactionID)
        return factionWars

    def GetFactionWarsForWarFactionID(self, warFactionID):
        factionWars = {}
        if warFactionID:
            factions = GetAllFWFactions()
            factionWars = IndexRowset(['warID',
             'declaredByID',
             'againstID',
             'timeDeclared',
             'timeFinished',
             'retracted',
             'retractedBy',
             'billID',
             'mutual'], [], 'warID')
            for i, faction in enumerate(factions):
                if facwarCommon.IsCombatEnemyFaction(faction, warFactionID):
                    factionWars[i * -1] = [None,
                     faction,
                     warFactionID,
                     None,
                     None,
                     None,
                     None,
                     None,
                     True]

        return factionWars

    def GetFactionMilitiaCorporation(self, factionID):
        ret = self.facWarMgr.GetFactionMilitiaCorporation(factionID)
        if not ret:
            return None
        return ret

    def GetFacWarZoneInfo(self, factionID):
        return sm.RemoteSvc('map').GetFacWarZoneInfo(factionID)

    def GetSystemUpgradeLevelBenefits(self, systemUpgradeLevel):
        return facwarCommon.BENEFITS_BY_LEVEL.get(systemUpgradeLevel, [])

    def EnforceOccupierFaction(self, factionID):
        if factionID and facwarCommon.IsOccupierFWFaction(factionID):
            return factionID
        return self.GetFactionIDByRaceID(session.raceID)

    def GetPreferredOccupierFactionID(self):
        factionID = self._GetActiveOccupierFactionID()
        return self.EnforceOccupierFaction(factionID)

    def _GetActiveOccupierFactionID(self):
        if session.warfactionid and facwarCommon.IsOccupierFWFaction(session.warfactionid):
            return session.warfactionid
        factionID = self.CheckStationElegibleForMilitia()
        if factionID:
            return factionID
        occupierID = self.GetSystemOccupier(session.solarsystemid2)
        if occupierID:
            return occupierID

    def JoinFactionAsCharacter(self, factionID, warfactionid):
        if warfactionid:
            alreadyInMilitiaLabel = localization.GetByLabel('UI/FactionWarfare/AlreadyInMilitia')
            eve.Message('CustomInfo', {'info': alreadyInMilitiaLabel})
            return
        if IsPlayerCorporation(session.corpid):
            header = localization.GetByLabel('UI/FactionWarfare/leaveYourCorpForFWQuestion')
            question = localization.GetByLabel('UI/FactionWarfare/leaveYourCorpForFWDesc', corpName=cfg.eveowners.Get(session.corpid).name)
            leaveCurrentCorpAnswer = eve.Message('CustomQuestion', {'header': header,
             'question': question}, uiconst.YESNO)
            if leaveCurrentCorpAnswer != uiconst.ID_YES:
                return
        ownerName = cfg.eveowners.Get(factionID).name
        headerLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionPlayer', factionName=ownerName)
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.GetService('sessionMgr').PerformSessionChange('corp.joinmilitia', self.facWarMgr.JoinFactionAsCharacter, factionID)

    def _RefreshCache(self):
        invalidate = [('facWarMgr', 'GetMyCharacterRankInfo', ()),
         ('facWarMgr', 'GetMyCharacterRankOverview', ()),
         ('facWarMgr', 'GetCorpFactionalWarStatus', ()),
         ('corporationSvc', 'GetEmploymentRecord', (session.charid,))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)

    def JoinFactionAsAlliance(self, factionID, warfactionid):
        ownerName = cfg.eveowners.Get(factionID).name
        headerLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionAlliance', factionName=ownerName)
        if warfactionid:
            alreadyInMilitiaLabel = localization.GetByLabel('UI/FactionWarfare/AlreadyInMilitia')
            eve.Message('CustomInfo', {'info': alreadyInMilitiaLabel})
            return
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            self.facWarMgr.JoinFactionAsAlliance(factionID)
            self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])
            sm.ScatterEvent('OnJoinMilitia')

    def JoinFactionAsCorporation(self, factionID, warfactionid):
        ownerName = cfg.eveowners.Get(factionID).name
        headerLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationHeader')
        bodyLabel = localization.GetByLabel('UI/FactionWarfare/JoinConfirmationQuestionCorp', factionName=ownerName)
        if warfactionid:
            alreadyInMilitiaLabel = localization.GetByLabel('UI/FactionWarfare/AlreadyInMilitia')
            eve.Message('CustomInfo', {'info': alreadyInMilitiaLabel})
            return
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            self.facWarMgr.JoinFactionAsCorporation(factionID)
            self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])
            sm.ScatterEvent('OnJoinMilitia')

    def LeaveFactionAsAlliance(self, factionID):
        self.facWarMgr.LeaveFactionAsAlliance(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def LeaveFactionAsCorporation(self, factionID):
        self.facWarMgr.LeaveFactionAsCorporation(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def WithdrawJoinFactionAsAlliance(self, factionID):
        self.facWarMgr.WithdrawJoinFactionAsAlliance(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def WithdrawJoinFactionAsCorporation(self, factionID):
        self.facWarMgr.WithdrawJoinFactionAsCorporation(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def WithdrawLeaveFactionAsAlliance(self, factionID):
        self.facWarMgr.WithdrawLeaveFactionAsAlliance(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def WithdrawLeaveFactionAsCorporation(self, factionID):
        self.facWarMgr.WithdrawLeaveFactionAsCorporation(factionID)
        self.objectCaching.InvalidateCachedMethodCalls([('facWarMgr', 'GetCorpFactionalWarStatus', ())])

    def GetCorpFactionalWarStatus(self):
        return self.facWarMgr.GetCorpFactionalWarStatus()

    def GetCharacterRankInfo(self, charID):
        if charID == session.charid:
            return self.facWarMgr.GetMyCharacterRankInfo()
        else:
            return self.facWarMgr.GetCharacterRankInfo(charID)

    def GetCharacterRankOverview(self, charID):
        if not charID == session.charid:
            return None
        return self.facWarMgr.GetMyCharacterRankOverview()

    def IsCharacterInFwCooldown(self):
        now = gametime.GetWallclockTime()
        cooldownTimestamp = sm.GetService('fwEnlistmentSvc').GetEnlistmentCooldownTimestamp()
        if cooldownTimestamp > gametime.GetWallclockTime():
            return True
        employmentHistory = sm.RemoteSvc('corporationSvc').GetEmploymentRecord(session.charid)
        yesterday = now - const.DAY
        for job in employmentHistory:
            if job.startDate > yesterday:
                if IsFwNpcCorp(job.corporationID):
                    return True
            else:
                break

        return False

    def RefreshCorps(self):
        return self.facWarMgr.RefreshCorps()

    def OnNPCStandingChange(self, fromID, newStanding, oldStanding):
        if session.warfactionid and fromID == self.GetFactionMilitiaCorporation(session.warfactionid):
            oldrank = self.GetCharacterRankInfo(session.charid).currentRank
            if oldrank != min(max(int(newStanding), 0), 9):
                newrank = self.facWarMgr.CheckForRankChange()
                if newrank is not None and oldrank != newrank:
                    self.DoOnRankChange(oldrank, newrank)
        invalidate = [('facWarMgr', 'GetMyCharacterRankInfo', ()), ('facWarMgr', 'GetMyCharacterRankOverview', ())]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)

    def DoOnRankChange(self, oldrank, newrank):
        messageID = 'RankGained' if newrank > oldrank else 'RankLost'
        rankLabel, rankDescription = self.GetRankLabel(session.warfactionid, newrank)
        try:
            eve.Message(messageID, {'rank': rankLabel})
        except:
            sys.exc_clear()

        sm.ScatterEvent('OnRankChange', oldrank, newrank)

    def GetStats_FactionInfo(self):
        return self.facWarMgr.GetStats_FactionInfo()

    def GetStats_Personal(self):
        header = ['you', 'top', 'all']
        data = {'killsY': {'you': 0,
                    'top': 0,
                    'all': 0},
         'killsLW': {'you': 0,
                     'top': 0,
                     'all': 0},
         'killsTotal': {'you': 0,
                        'top': 0,
                        'all': 0},
         'vpY': {'you': 0,
                 'top': 0,
                 'all': 0},
         'vpLW': {'you': 0,
                  'top': 0,
                  'all': 0},
         'vpTotal': {'you': 0,
                     'top': 0,
                     'all': 0}}
        if not self.topStats:
            self.topStats = self.facWarMgr.GetStats_TopAndAllKillsAndVPs()
        for k in ('killsY', 'killsLW', 'killsTotal', 'vpY', 'vpLW', 'vpTotal'):
            data[k]['top'] = self.topStats[0][const.groupCharacter][k]
            data[k]['all'] = self.topStats[1][const.groupCharacter][k]

        for k, v in self.facWarMgr.GetStats_Character().items():
            data[k]['you'] = v

        return {'header': header,
         'data': data}

    def GetStats_Corp(self, corpID):
        header = ['your', 'top', 'all']
        data = {'killsY': {'your': 0,
                    'top': 0,
                    'all': 0},
         'killsLW': {'your': 0,
                     'top': 0,
                     'all': 0},
         'killsTotal': {'your': 0,
                        'top': 0,
                        'all': 0},
         'vpY': {'your': 0,
                 'top': 0,
                 'all': 0},
         'vpLW': {'your': 0,
                  'top': 0,
                  'all': 0},
         'vpTotal': {'your': 0,
                     'top': 0,
                     'all': 0}}
        if not self.topStats:
            self.topStats = self.facWarMgr.GetStats_TopAndAllKillsAndVPs()
        for k in ('killsY', 'killsLW', 'killsTotal', 'vpY', 'vpLW', 'vpTotal'):
            data[k]['top'] = self.topStats[0][const.groupCorporation][k]
            data[k]['all'] = self.topStats[1][const.groupCorporation][k]

        for k, v in self.facWarMgr.GetStats_Corp().items():
            data[k]['your'] = v

        return {'header': header,
         'data': data}

    def GetStats_Alliance(self, allianceID):
        header = ['your', 'top', 'all']
        data = {'killsY': {'your': 0,
                    'top': 0,
                    'all': 0},
         'killsLW': {'your': 0,
                     'top': 0,
                     'all': 0},
         'killsTotal': {'your': 0,
                        'top': 0,
                        'all': 0},
         'vpY': {'your': 0,
                 'top': 0,
                 'all': 0},
         'vpLW': {'your': 0,
                  'top': 0,
                  'all': 0},
         'vpTotal': {'your': 0,
                     'top': 0,
                     'all': 0}}
        if not self.topStats:
            self.topStats = self.facWarMgr.GetStats_TopAndAllKillsAndVPs()
        for k in ('killsY', 'killsLW', 'killsTotal', 'vpY', 'vpLW', 'vpTotal'):
            data[k]['top'] = self.topStats[0][const.groupAlliance][k]
            data[k]['all'] = self.topStats[1][const.groupAlliance][k]

        for k, v in self.facWarMgr.GetStats_Alliance().items():
            data[k]['your'] = v

        return {'header': header,
         'data': data}

    def GetStats_Militia(self):
        return self.facWarMgr.GetStats_Militia()

    def GetStats_CorpPilots(self):
        return self.facWarMgr.GetStats_CorpPilots()

    def CheckOwnerInFaction(self, ownerID):
        if ownerID not in self.warFactionByOwner:
            factionID = get_corporation_faction_id(ownerID)
            if factionID and IsAnyFWFaction(factionID):
                self.warFactionByOwner[ownerID] = factionID
        return self.warFactionByOwner.get(ownerID, None)

    def CheckForSafeSystem(self, dockableItem, factionID, solarSystemID = None):
        ss = sm.GetService('map').GetSecurityClass(solarSystemID or session.solarsystemid2)
        if ss != const.securityClassHighSec:
            return True
        if IsNPC(dockableItem.ownerID):
            fosi = get_corporation_faction_id(dockableItem.ownerID)
            if fosi is None:
                return True
        foss = sm.GetService('faction').GetFactionOfSolarSystem(solarSystemID or session.solarsystemid2)
        if IsCombatEnemyFaction(factionID, foss):
            return False
        return True

    def CheckStationElegibleForMilitia(self):
        if session.warfactionid:
            return session.warfactionid
        if not session.stationid:
            return False
        factionID = self.GetCurrentStationFactionID()
        if factionID:
            return factionID
        return False

    def GetCurrentStationFactionID(self):
        if not session.stationid:
            return
        ownerID = sm.GetService('station').stationItem.ownerID
        factionID = None
        if ownerID:
            factionID = self.CheckOwnerInFaction(ownerID)
        return factionID

    def GetRankLabel(self, factionID, rank):
        rank = min(9, rank)
        rankLabel, rankDescription = ('', '')
        if rank < 0:
            rankLabel = localization.GetByLabel('UI/FactionWarfare/Ranks/NoRank')
            rankDescription = ''
        else:
            rankPath, descPath = RankLabelsByFactionID.get((factionID, rank), ('UI/FactionWarfare/Ranks/NoRank', 'UI/FactionWarfare/Ranks/NoRank'))
            rankLabel = localization.GetByLabel(rankPath)
            rankDescription = localization.GetByLabel(descPath)
        return (rankLabel, rankDescription)

    def GetSolarSystemLPs(self, solarSystemID = None):
        if not solarSystemID:
            solarSystemID = session.solarsystemid2
        if not sm.GetService('fwWarzoneSvc').IsWarzoneSolarSystem(solarSystemID):
            return 0
        if solarSystemID not in self.solarSystemLPs:
            self.solarSystemLPs[solarSystemID] = self.facWarMgr.GetSolarSystemLPs(solarSystemID)
        return self.solarSystemLPs[solarSystemID]

    def DonateLPsToSolarSystem(self, pointsDonated, pointsToIhub):
        pointsDonated = max(pointsDonated, const.facwarMinLPDonation)
        militiaCorpID = self.GetFactionMilitiaCorporation(session.warfactionid)
        if militiaCorpID is None:
            raise RuntimeError("Don't know the militia corp for faction", session.warfactionid)
        pointsWithCorp = self.loyaltyPointsWalletSvc.GetCharacterWalletLPBalance(militiaCorpID)
        if pointsDonated > pointsWithCorp:
            militiaName = cfg.eveowners.Get(militiaCorpID).ownerName
            raise UserError('FacWarCantDonateSoMuch', {'militiaName': militiaName,
             'points': pointsWithCorp})
        solarSystemLPs = self.GetSolarSystemLPs()
        if pointsToIhub + solarSystemLPs > const.facwarSolarSystemMaxLPPool:
            militiaName = cfg.eveowners.Get(militiaCorpID).ownerName
            maxPointsToAdd = const.facwarSolarSystemMaxLPPool - solarSystemLPs
            raise UserError('FacWarPoolOverloaded', {'militiaName': militiaName,
             'points': maxPointsToAdd})
        return self.facWarMgr.DonateLPsToSolarSystem(pointsDonated, pointsToIhub)

    def GetNearestFactionWarfareStationData(self, preferredFaction = None, fallbackToLightYears = False):
        stations = sm.RemoteSvc('map').GetStationInfo()
        warFactionsByOwner = sm.GetService('starmap').GetWarFactionByOwner(stations)
        factionStationsBySolarSystem = {}
        for stationRow in stations:
            stationID = stationRow.stationID
            solarSystemID = stationRow.solarSystemID
            ownerID = stationRow.ownerID
            if ownerID in warFactionsByOwner:
                factionID = warFactionsByOwner[ownerID]
                if factionID == preferredFaction:
                    factionStationsBySolarSystem[solarSystemID] = stationID
                elif preferredFaction is None:
                    factionStationsBySolarSystem[solarSystemID] = stationID

        nearestStationID = None
        jumpsToNearestStation = 999999
        for solarSystemID, stationID in factionStationsBySolarSystem.iteritems():
            dist = sm.GetService('clientPathfinderService').GetJumpCount(session.solarsystemid2, solarSystemID)
            if dist <= jumpsToNearestStation:
                jumpsToNearestStation = dist
                nearestStationID = stationID

        if nearestStationID is None and fallbackToLightYears:
            lyToNearestStation = 999999
            for solarSystemID, stationID in factionStationsBySolarSystem.iteritems():
                lyDistance = GetLightYearDistance(session.solarsystemid2, solarSystemID, False)
                if lyDistance <= lyToNearestStation:
                    lyToNearestStation = lyDistance
                    nearestStationID = stationID

        return (jumpsToNearestStation, nearestStationID)


RankLabelsByFactionID = {(const.factionCaldariState, 0): ('UI/FactionWarfare/Ranks/RankCaldari0', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari0'),
 (const.factionCaldariState, 1): ('UI/FactionWarfare/Ranks/RankCaldari1', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari1'),
 (const.factionCaldariState, 2): ('UI/FactionWarfare/Ranks/RankCaldari2', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari2'),
 (const.factionCaldariState, 3): ('UI/FactionWarfare/Ranks/RankCaldari3', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari3'),
 (const.factionCaldariState, 4): ('UI/FactionWarfare/Ranks/RankCaldari4', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari4'),
 (const.factionCaldariState, 5): ('UI/FactionWarfare/Ranks/RankCaldari5', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari5'),
 (const.factionCaldariState, 6): ('UI/FactionWarfare/Ranks/RankCaldari6', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari6'),
 (const.factionCaldariState, 7): ('UI/FactionWarfare/Ranks/RankCaldari7', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari7'),
 (const.factionCaldariState, 8): ('UI/FactionWarfare/Ranks/RankCaldari8', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari8'),
 (const.factionCaldariState, 9): ('UI/FactionWarfare/Ranks/RankCaldari9', 'UI/FactionWarfare/Ranks/RankDescriptionCaldari9'),
 (const.factionMinmatarRepublic, 0): ('UI/FactionWarfare/Ranks/RankMinmatar0', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar0'),
 (const.factionMinmatarRepublic, 1): ('UI/FactionWarfare/Ranks/RankMinmatar1', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar1'),
 (const.factionMinmatarRepublic, 2): ('UI/FactionWarfare/Ranks/RankMinmatar2', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar2'),
 (const.factionMinmatarRepublic, 3): ('UI/FactionWarfare/Ranks/RankMinmatar3', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar3'),
 (const.factionMinmatarRepublic, 4): ('UI/FactionWarfare/Ranks/RankMinmatar4', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar4'),
 (const.factionMinmatarRepublic, 5): ('UI/FactionWarfare/Ranks/RankMinmatar5', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar5'),
 (const.factionMinmatarRepublic, 6): ('UI/FactionWarfare/Ranks/RankMinmatar6', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar6'),
 (const.factionMinmatarRepublic, 7): ('UI/FactionWarfare/Ranks/RankMinmatar7', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar7'),
 (const.factionMinmatarRepublic, 8): ('UI/FactionWarfare/Ranks/RankMinmatar8', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar8'),
 (const.factionMinmatarRepublic, 9): ('UI/FactionWarfare/Ranks/RankMinmatar9', 'UI/FactionWarfare/Ranks/RankDescriptionMinmatar9'),
 (const.factionAmarrEmpire, 0): ('UI/FactionWarfare/Ranks/RankAmarr0', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr0'),
 (const.factionAmarrEmpire, 1): ('UI/FactionWarfare/Ranks/RankAmarr1', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr1'),
 (const.factionAmarrEmpire, 2): ('UI/FactionWarfare/Ranks/RankAmarr2', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr2'),
 (const.factionAmarrEmpire, 3): ('UI/FactionWarfare/Ranks/RankAmarr3', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr3'),
 (const.factionAmarrEmpire, 4): ('UI/FactionWarfare/Ranks/RankAmarr4', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr4'),
 (const.factionAmarrEmpire, 5): ('UI/FactionWarfare/Ranks/RankAmarr5', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr5'),
 (const.factionAmarrEmpire, 6): ('UI/FactionWarfare/Ranks/RankAmarr6', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr6'),
 (const.factionAmarrEmpire, 7): ('UI/FactionWarfare/Ranks/RankAmarr7', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr7'),
 (const.factionAmarrEmpire, 8): ('UI/FactionWarfare/Ranks/RankAmarr8', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr8'),
 (const.factionAmarrEmpire, 9): ('UI/FactionWarfare/Ranks/RankAmarr9', 'UI/FactionWarfare/Ranks/RankDescriptionAmarr9'),
 (const.factionGallenteFederation, 0): ('UI/FactionWarfare/Ranks/RankGallente0', 'UI/FactionWarfare/Ranks/RankDescriptionGallente0'),
 (const.factionGallenteFederation, 1): ('UI/FactionWarfare/Ranks/RankGallente1', 'UI/FactionWarfare/Ranks/RankDescriptionGallente1'),
 (const.factionGallenteFederation, 2): ('UI/FactionWarfare/Ranks/RankGallente2', 'UI/FactionWarfare/Ranks/RankDescriptionGallente2'),
 (const.factionGallenteFederation, 3): ('UI/FactionWarfare/Ranks/RankGallente3', 'UI/FactionWarfare/Ranks/RankDescriptionGallente3'),
 (const.factionGallenteFederation, 4): ('UI/FactionWarfare/Ranks/RankGallente4', 'UI/FactionWarfare/Ranks/RankDescriptionGallente4'),
 (const.factionGallenteFederation, 5): ('UI/FactionWarfare/Ranks/RankGallente5', 'UI/FactionWarfare/Ranks/RankDescriptionGallente5'),
 (const.factionGallenteFederation, 6): ('UI/FactionWarfare/Ranks/RankGallente6', 'UI/FactionWarfare/Ranks/RankDescriptionGallente6'),
 (const.factionGallenteFederation, 7): ('UI/FactionWarfare/Ranks/RankGallente7', 'UI/FactionWarfare/Ranks/RankDescriptionGallente7'),
 (const.factionGallenteFederation, 8): ('UI/FactionWarfare/Ranks/RankGallente8', 'UI/FactionWarfare/Ranks/RankDescriptionGallente8'),
 (const.factionGallenteFederation, 9): ('UI/FactionWarfare/Ranks/RankGallente9', 'UI/FactionWarfare/Ranks/RankDescriptionGallente9'),
 (const.factionAngelCartel, 0): ('UI/FactionWarfare/Ranks/RankAngel0', 'UI/FactionWarfare/Ranks/RankDescriptionAngel0'),
 (const.factionAngelCartel, 1): ('UI/FactionWarfare/Ranks/RankAngel1', 'UI/FactionWarfare/Ranks/RankDescriptionAngel1'),
 (const.factionAngelCartel, 2): ('UI/FactionWarfare/Ranks/RankAngel2', 'UI/FactionWarfare/Ranks/RankDescriptionAngel2'),
 (const.factionAngelCartel, 3): ('UI/FactionWarfare/Ranks/RankAngel3', 'UI/FactionWarfare/Ranks/RankDescriptionAngel3'),
 (const.factionAngelCartel, 4): ('UI/FactionWarfare/Ranks/RankAngel4', 'UI/FactionWarfare/Ranks/RankDescriptionAngel4'),
 (const.factionAngelCartel, 5): ('UI/FactionWarfare/Ranks/RankAngel5', 'UI/FactionWarfare/Ranks/RankDescriptionAngel5'),
 (const.factionAngelCartel, 6): ('UI/FactionWarfare/Ranks/RankAngel6', 'UI/FactionWarfare/Ranks/RankDescriptionAngel6'),
 (const.factionAngelCartel, 7): ('UI/FactionWarfare/Ranks/RankAngel7', 'UI/FactionWarfare/Ranks/RankDescriptionAngel7'),
 (const.factionAngelCartel, 8): ('UI/FactionWarfare/Ranks/RankAngel8', 'UI/FactionWarfare/Ranks/RankDescriptionAngel8'),
 (const.factionAngelCartel, 9): ('UI/FactionWarfare/Ranks/RankAngel9', 'UI/FactionWarfare/Ranks/RankDescriptionAngel9'),
 (const.factionGuristasPirates, 0): ('UI/FactionWarfare/Ranks/RankGuristas0', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas0'),
 (const.factionGuristasPirates, 1): ('UI/FactionWarfare/Ranks/RankGuristas1', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas1'),
 (const.factionGuristasPirates, 2): ('UI/FactionWarfare/Ranks/RankGuristas2', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas2'),
 (const.factionGuristasPirates, 3): ('UI/FactionWarfare/Ranks/RankGuristas3', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas3'),
 (const.factionGuristasPirates, 4): ('UI/FactionWarfare/Ranks/RankGuristas4', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas4'),
 (const.factionGuristasPirates, 5): ('UI/FactionWarfare/Ranks/RankGuristas5', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas5'),
 (const.factionGuristasPirates, 6): ('UI/FactionWarfare/Ranks/RankGuristas6', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas6'),
 (const.factionGuristasPirates, 7): ('UI/FactionWarfare/Ranks/RankGuristas7', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas7'),
 (const.factionGuristasPirates, 8): ('UI/FactionWarfare/Ranks/RankGuristas8', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas8'),
 (const.factionGuristasPirates, 9): ('UI/FactionWarfare/Ranks/RankGuristas9', 'UI/FactionWarfare/Ranks/RankDescriptionGuristas9')}
