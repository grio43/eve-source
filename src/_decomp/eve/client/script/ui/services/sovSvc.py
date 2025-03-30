#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\sovSvc.py
from collections import defaultdict
import blue
import utillib
from brennivin.threadutils import expiring_memoize
from carbon.common.script.sys.service import Service
from entosis.entosisConst import STRUCTURES_UPDATED
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_LOCATION_INFO
from eve.common.lib import appConst as const
from eve.common.script.sys import devIndexUtil, idCheckers
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from entosis.occupancyCalculator import GetOccupancyMultiplier
from inventorycommon.const import typeTerritorialClaimUnit, typeInfrastructureHub
import localization
from sovereignty.data_types import SovClaimInfo
from utillib import KeyVal
import gametime
CLAIM_DAYS_TO_SECONDS = 86400

class SovService(Service):
    __guid__ = 'svc.sov'
    __dependencies__ = ['audio']
    __startupdependencies__ = ['fwWarzoneSvc']
    __notifyevents__ = ['ProcessSovStatusChanged',
     'OnSessionChanged',
     'OnSovereigntyAudioEvent',
     'OnSolarSystemSovStructuresUpdated',
     'OnSolarSystemDevIndexChanged']

    def __init__(self):
        Service.__init__(self)
        self.sovInfoBySystemID = {}
        self.devIndexMgr = None
        self.outpostData = None

    def Run(self, *args):
        Service.Run(self, *args)
        self.indexLevels = []
        for level in devIndexUtil.GetDevIndexLevels()[const.attributeDevIndexMilitary].itervalues():
            self.indexLevels.append(level.maxLevel)

        self.indexLevels.sort()
        self.holdTimeLevels = devIndexUtil.GetTimeIndexLevels()

    def GetTimeIndexValuesInDays(self):
        return [ t / CLAIM_DAYS_TO_SECONDS for t in self.holdTimeLevels ]

    def ProcessSovStatusChanged(self, *args):
        solarSystemID, newStatus = args
        if newStatus is None and solarSystemID in self.sovInfoBySystemID:
            del self.sovInfoBySystemID[solarSystemID]
        else:
            self.sovInfoBySystemID[solarSystemID] = newStatus
        if solarSystemID == session.solarsystemid2:
            sm.ScatterEvent('OnSystemStatusChanged')

    def GetSystemSovereigntyInfo(self, solarSystemID, forceUpdate = False):
        fwOccupationState = self.fwWarzoneSvc.GetOccupationState(solarSystemID)
        if fwOccupationState is not None:
            return SovClaimInfo(None, None, fwOccupationState.occupierID)
        if not forceUpdate and solarSystemID in self.sovInfoBySystemID:
            self.LogInfo('GetSystemSovereigntyInfo: Returning cached sov info', self.sovInfoBySystemID[solarSystemID])
            return self.sovInfoBySystemID[solarSystemID]
        sovClaimInfo = sm.RemoteSvc('sovMgr').GetSystemSovereigntyInfo(solarSystemID)
        self.sovInfoBySystemID[solarSystemID] = sovClaimInfo
        self.LogInfo('GetSystemSovereigntyInfo: Returning sov status from server:', sovClaimInfo)
        return sovClaimInfo

    @expiring_memoize(15)
    def GetInfrastructureHubInfo(self, solarSystemID):
        return sm.RemoteSvc('sovMgr').GetInfrastructureHubInfo(solarSystemID)

    @expiring_memoize(30)
    def GetSovStructuresInfoForSolarSystem(self, solarsystemID):
        sovMgr = sm.RemoteSvc('sovMgr')
        if solarsystemID == session.solarsystemid2:
            solarSystemStructuresInfo = sovMgr.GetSovStructuresInfoForLocalSolarSystem()
        else:
            solarSystemStructuresInfo = sovMgr.GetSovStructuresInfoForSolarSystem(solarsystemID)
        self.ModifyStructureInfoIfNeeded(solarSystemStructuresInfo, solarsystemID)
        return solarSystemStructuresInfo

    def GetSpecificSovStructuresInfoInSolarSystem(self, solarsystemID, itemID):
        solarsystemStructureInfo = self.GetSovStructuresInfoForSolarSystem(solarsystemID)
        for structureInfo in solarsystemStructureInfo:
            if structureInfo.itemID == itemID:
                return structureInfo

    def ModifyStructureInfoIfNeeded(self, solarSystemStructuresInfo, solarsystemID):
        if solarSystemStructuresInfo is None:
            return
        for structureInfo in solarSystemStructuresInfo:
            structureInfo['solarSystemID'] = solarsystemID
            structureInfo['constellationID'] = cfg.mapSystemCache.Get(solarsystemID).constellationID

    def OnSolarSystemSovStructuresUpdated(self, solarsystemID, solarSystemStructuresInfo, changes = None):
        self.LogInfo('OnSolarSystemSovStructuresUpdated', solarsystemID, solarSystemStructuresInfo)
        self.ModifyStructureInfoIfNeeded(solarSystemStructuresInfo, solarsystemID)
        self.GetSovStructuresInfoForSolarSystem.prime_cache_result((self, solarsystemID), solarSystemStructuresInfo)
        if changes:
            for sourceItemID, whatChanged in changes.iteritems():
                sm.ScatterEvent('OnSolarsystemSovStructureChanged', solarsystemID, whatChanged, sourceItemID)

        else:
            sm.ScatterEvent('OnSolarsystemSovStructureChanged', solarsystemID, whatChanged=set([STRUCTURES_UPDATED]))

    def OnSolarSystemDevIndexChanged(self, solarsystemID):
        if solarsystemID == session.solarsystemid2:
            self.InvalidateCacheForGetDevelopmentIndicesForSystem(solarsystemID)
            locationPanel = self.GetLocationPanel()
            locationPanel.Update()

    def GetLocationPanel(self):
        infoPanelSvc = sm.GetService('infoPanel')
        locationPanel = infoPanelSvc.GetPanelByTypeID(PANEL_LOCATION_INFO)
        return locationPanel

    def GetContestedState(self, solarSystemID):
        return localization.GetByLabel('UI/Inflight/Brackets/SystemContested')

    def GetKillLast24H(self, itemID):
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 24)
        systems = set(sm.GetService('map').IterateSolarSystemIDs(itemID))
        totalKills = 0
        totalPods = 0
        for stats in historyDB:
            if stats.solarSystemID in systems:
                kills = stats.value1 - stats.value2
                totalKills += kills
                totalPods += stats.value3

        return (totalKills, totalPods)

    def AddToBucket(self, buckets, systemOwners, systemID):
        self.counter += 1
        sovID = systemOwners.get(systemID, None)
        if sovID is None:
            sovID = sm.GetService('map').GetItem(systemID).factionID
        if sovID is not None:
            count = buckets.get(sovID, 0)
            buckets[sovID] = count + 1

    def GetIdFromScope(self, scope):
        if scope == 'world':
            itemID = None
        elif scope == 'region':
            itemID = session.regionid
        elif scope == 'constellation':
            itemID = session.constellationid
        else:
            itemID = session.solarsystemid2
        return itemID

    def GetDevIndexMgr(self):
        if self.devIndexMgr is None:
            self.devIndexMgr = sm.RemoteSvc('devIndexManager')
        return self.devIndexMgr

    def GetIndexLevel(self, value, indexID, isUpgrade = False):
        if indexID == const.attributeDevIndexUpgrade:
            indexLevels = const.facwarSolarSystemUpgradeThresholds[1:]
        elif indexID == const.attributeDevIndexSovereignty:
            indexLevels = self.holdTimeLevels
        else:
            indexLevels = self.indexLevels
        if value >= indexLevels[-1]:
            return utillib.KeyVal(level=5, remainder=0.0)
        for level, maxValue in enumerate(indexLevels):
            if value < maxValue:
                if level == 0:
                    minValue = 0.0
                else:
                    minValue = float(indexLevels[level - 1])
                if value < 0:
                    remainder = 0
                remainder = value - minValue
                remainder = remainder / (maxValue - minValue)
                if isUpgrade:
                    level = value
                return utillib.KeyVal(level=level, remainder=remainder)

    def GetLevelInfoForIndex(self, indexID, devIndex = None, solarsystemID = None):
        if solarsystemID is None:
            solarsystemID = session.solarsystemid2
        increasing = False
        if indexID == const.attributeDevIndexSovereignty:
            iHubInfo = self.GetInfrastructureHubInfo(solarsystemID)
            if iHubInfo:
                currentTime = blue.os.GetWallclockTime()
                timeDiff = currentTime - iHubInfo.claimTime
                value = timeDiff / const.SEC
                increasing = True
            else:
                value = 0
        else:
            if devIndex is None:
                devIndex = self.GetDevelopmentIndicesForSystem(solarsystemID).get(indexID, None)
            if devIndex is None:
                self.LogError('The index', indexID, 'does not exist')
                value = 0
                increasing = True
            else:
                increasing = devIndex.increasing
                value = devIndex.points
        ret = self.GetIndexLevel(value, indexID)
        ret.increasing = increasing
        return ret

    def GetAllDevelopmentIndicesMapped(self):
        systemToIndexMap = {}
        for indexInfo in sm.RemoteSvc('devIndexManager').GetAllDevelopmentIndices():
            systemToIndexMap[indexInfo.solarSystemID] = {const.attributeDevIndexMilitary: indexInfo.militaryPoints,
             const.attributeDevIndexIndustrial: indexInfo.industrialPoints,
             const.attributeDevIndexSovereignty: indexInfo.claimedFor * CLAIM_DAYS_TO_SECONDS}

        return systemToIndexMap

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            self.devIndexMgr = None
            self.outpostData = None
            oldSolarSystemID2, newSolarSystemID2 = change['solarsystemid2']
            self.GetSovStructuresInfoForSolarSystem.remove_from_cache((self, newSolarSystemID2))
            self.GetInfrastructureHubInfo.remove_from_cache((self, newSolarSystemID2))

    def GetCurrentData(self, locationID):
        fwData = {}
        if IsKnownSpaceSystem(locationID):
            constellationID = sm.GetService('map').GetParent(locationID)
            data = sm.RemoteSvc('map').GetCurrentSovData(constellationID)
            indexedData = data.Index('locationID')
            sovData = [indexedData[locationID]]
            fwData = sm.RemoteSvc('map').GetConstellationLPData(constellationID).Index('solarSystemID')
        else:
            if idCheckers.IsConstellation(locationID):
                fwData = sm.RemoteSvc('map').GetConstellationLPData(locationID).Index('solarSystemID')
            sovData = sm.RemoteSvc('map').GetCurrentSovData(locationID)
        return (sovData, fwData)

    def GetRecentActivity(self):
        data = sm.RemoteSvc('map').GetRecentSovActivity()
        return data

    def GetDevIndexLevel(self, points):
        ret = 0
        for level, value in enumerate(self.indexLevels):
            if value < points:
                ret = level + 1
            else:
                break

        return ret

    def OnSovereigntyAudioEvent(self, eventID, textParams):
        if eventID in const.sovAudioEventFiles:
            self.audio.SendUIEvent(unicode(const.sovAudioEventFiles[eventID][0]))
            if const.sovAudioEventFiles[eventID][1] is not None:
                eve.Message(const.sovAudioEventFiles[eventID][1], textParams)

    def InvalidateCacheForGetDevelopmentIndicesForSystem(self, solarsystemID):
        self.GetDevelopmentIndicesForSystem.remove_from_cache((self, solarsystemID))
        sm.GetService('objectCaching').InvalidateCachedMethodCall('devIndexManager', 'GetDevelopmentIndicesForSystem', solarsystemID)

    @expiring_memoize(120)
    def GetDevelopmentIndicesForSystem(self, solarsystemID):
        return self.GetDevIndexMgr().GetDevelopmentIndicesForSystem(solarsystemID)

    def GetIndexInfoForSolarsystem(self, solarsystemID):
        devIndices = self.GetDevelopmentIndicesForSystem(solarsystemID)
        militaryIndex = devIndices.get(const.attributeDevIndexMilitary, None)
        industrialIndex = devIndices.get(const.attributeDevIndexIndustrial, None)
        strategicIndex = devIndices.get(const.attributeDevIndexSovereignty, None)
        militaryIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexMilitary, devIndex=militaryIndex, solarsystemID=solarsystemID)
        industrialIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexIndustrial, devIndex=industrialIndex, solarsystemID=solarsystemID)
        strategicIndexInfo = self.GetLevelInfoForIndex(const.attributeDevIndexSovereignty, devIndex=strategicIndex, solarsystemID=solarsystemID)
        ret = utillib.KeyVal(militaryIndexLevel=militaryIndexInfo.level, industrialIndexLevel=industrialIndexInfo.level, strategicIndexLevel=strategicIndexInfo.level, militaryIndexRemainder=militaryIndexInfo.remainder, industrialIndexRemainder=industrialIndexInfo.remainder, strategicIndexRemainder=strategicIndexInfo.remainder)
        return ret

    def GetSovInfoForSolarsystem(self, solarsystemID, isCapital):
        indexInfo = self.GetIndexInfoForSolarsystem(solarsystemID)
        multiplier = 1 / GetOccupancyMultiplier(indexInfo.industrialIndexLevel, indexInfo.militaryIndexLevel, indexInfo.strategicIndexLevel, isCapital)
        sovInfo = self.GetSystemSovereigntyInfo(solarsystemID)
        if sovInfo:
            solSovOwnerID = sovInfo.allianceID
        else:
            solSovOwnerID = None
        indexInfo.defenseMultiplier = multiplier
        indexInfo.sovHolderID = solSovOwnerID
        return indexInfo

    def IsSystemConquarable(self, solarsystemID):
        if not IsKnownSpaceSystem(solarsystemID):
            return False
        if sm.GetService('map').GetSecurityClass(solarsystemID) != const.securityClassZeroSec:
            return False
        solarSystem = cfg.mapSystemCache.get(solarsystemID, None)
        factionID = getattr(solarSystem, 'factionID', None)
        if factionID:
            return False
        return True

    def GetSovereigntyStructuresInfoForAlliance(self):
        if session.allianceid is None:
            return
        allianceSvc = sm.GetService('alliance')
        alliance = allianceSvc.GetMoniker()
        tcuRows, iHubRows, campaignScores = alliance.GetAllianceSovereigntyStructuresInfo()
        scoresPerStructure = defaultdict(dict)
        for campaignScore in campaignScores:
            scoresPerStructure[campaignScore.sourceItemID][campaignScore.teamID] = campaignScore.score

        structuresPerSolarsystem = defaultdict(list)
        rowsPerType = [(tcuRows, typeTerritorialClaimUnit), (iHubRows, typeInfrastructureHub)]
        for structureRows, structureType in rowsPerType:
            for structureRow in structureRows:
                structureInfo = KeyVal({'itemID': structureRow.structureID,
                 'typeID': structureType,
                 'campaignState': None,
                 'vulnerabilityState': None,
                 'defenseMultiplier': 1.0,
                 'solarSystemID': structureRow.solarSystemID})
                if structureType == typeInfrastructureHub:
                    structureInfo.corporationID = structureRow.corporationID
                if structureRow.campaignStartTime and structureRow.campaignEventType:
                    structureInfo.campaignState = (structureRow.campaignEventType,
                     session.allianceid,
                     structureRow.campaignStartTime,
                     scoresPerStructure[structureRow.structureID])
                    structureInfo.defenseMultiplier = structureRow.campaignOccupancyLevel
                elif structureRow.vulnerableStartTime and structureRow.vulnerableEndTime:
                    structureInfo.vulnerabilityState = (structureRow.vulnerableStartTime, structureRow.vulnerableEndTime)
                    structureInfo.defenseMultiplier = structureRow.vulnerabilityOccupancyLevel
                structuresPerSolarsystem[structureRow.solarSystemID].append(structureInfo)

        return structuresPerSolarsystem

    def GetMyCapitalSystem(self):
        if session.allianceid:
            capitalSystemInfo = sm.GetService('alliance').GetCapitalSystemInfo()
            if capitalSystemInfo:
                return capitalSystemInfo.currentCapitalSystem

    def GetSovHubFuelAccessGroup(self, solarSystemID):
        sovMgr = sm.RemoteSvc('sovMgr')
        return sovMgr.GetSovHubFuelAccessGroup(solarSystemID)

    def SetSovHubFuelAccessGroup(self, solarSystemID, fuelAccessGroupID):
        sovMgr = sm.RemoteSvc('sovMgr')
        return sovMgr.SetSovHubFuelAccessGroup(solarSystemID, fuelAccessGroupID)

    def IsOnLocalSovHubFuelAccessGroup(self):
        sovMgr = sm.RemoteSvc('sovMgr')
        return sovMgr.IsOnLocalSovHubFuelAccessGroup()

    def CleanUpSystem(self, structureIDs):
        return sm.RemoteSvc('sovMgr').CleanUpSystem(structureIDs)

    def CanCleanUpSystem(self):
        if not bool(session.corprole & const.corpRoleStationManager | const.corpRoleDirector):
            return False
        hubInfo = self.GetInfrastructureHubInfo(session.solarsystemid2)
        if not hubInfo or not hubInfo.isSovHubMode or hubInfo.ownerID != session.corpid:
            return False
        return gametime.GetHoursSinceWallclockTime(hubInfo.claimTime) < 1

    def GetStructuresAvailableToCleanUp(self):
        if not self.CanCleanUpSystem():
            return []
        result = []
        ballpark = sm.GetService('michelle').GetBallpark()
        for ball_id in ballpark.balls.iterkeys():
            item = ballpark.GetInvItem(ball_id)
            if item and idCheckers.IsSkyhook(item.typeID) and item.allianceID != session.allianceid:
                result.append(item)

        return result
