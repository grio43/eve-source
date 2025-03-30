#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewColorHandler.py
import random
import appConst
from carbonui.util.bunch import Bunch
from carbonui.util.color import Color
from characterdata.factions import get_faction, get_faction_name
from collections import defaultdict
import eve.client.script.ui.shared.maps.mapcommon as mapcommon
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.mapView.colorModes.colorModeInfoSovereignty import ColorModeInfoSearch_Faction
from eve.client.script.ui.shared.mapView.filters import filtersByID
from eve.client.script.ui.shared.mapView.filters.mapFilterConst import ATTACKED_COLOR, BASE11_COLORRANGE, BASE3_COLORRANGE, BASE5_COLORRANGE, COLOR_ASSETS, COLOR_DEVINDEX, COLOR_GRAY, COLOR_GREEN, COLOR_ORANGE, COLOR_PURPLE, COLOR_RED, COLOR_STANDINGS_BAD, COLOR_STANDINGS_GOOD, COLOR_STANDINGS_NEUTRAL, COLOR_WHITE, COLOR_YELLOW, CONFISCATED_COLOR, DEFAULT_MAX_COLOR, INTENSITY_COLORRANGE, MIN_MAX_COLORRANGE, NEG_NEU_POS_3RANGE, NEUTRAL_COLOR, STAR_COLORTYPE_DATA, STAR_SIZE_FACTOR_MAX, STAR_SIZE_FACTOR_STANDARD
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.client.script.ui.shared.maps.maputils import GetJumpClonesBySystemID
from eve.client.script.ui.util.uix import EditStationName
from eve.common.script.sys.eveCfg import GetActiveShip, CanUseAgent
from eve.common.script.sys.idCheckers import IsFaction
from eve.common.script.sys.idCheckers import IsSolarSystem
from eve.common.script.util.structuresCommon import IsRepairServiceAvailable
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetESSBountyColor
import evetypes
import geo2
import industry
import inventorycommon.typeHelpers
from evestations.data import service_in_station_operation
from factionwarfare.client.text import GetVictoryPointStateText
from localization import GetByMessageID, GetByLabel
import logging
from eve.client.script.ui.shared.maps.mapcommon import LegendItem
import talecommon.const as taleConst
from npcs.divisions import get_division_name
from security.client.securityColor import COLORCURVE_SECURITY
from solarsysteminterference.client.ui import GetInterferenceBandLabel
from solarsysteminterference.const import INTERFERENCE_BAND_NONE, INTERFERENCE_BAND_LOW, INTERFERENCE_BAND_MEDIUM, INTERFERENCE_BAND_HIGH
log = logging.getLogger(__name__)

def GetBase11ColorByID(objectID):
    return BASE11_COLORRANGE[objectID % 11]


def ColorStarsByDevIndex(colorInfo, starColorMode, indexID, indexName):
    sovSvc = sm.GetService('sov')
    indexData = sovSvc.GetAllDevelopmentIndicesMapped()
    color = COLOR_DEVINDEX
    hintFunc = lambda indexName, level: GetByLabel('UI/Map/StarModeHandler/devIndxLevel', indexName=indexName, level=level)
    maxLevel = 0
    for solarSystemID, info in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        maxLevel = max(maxLevel, levelInfo.level)

    for solarSystemID, info in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        if levelInfo.level == 0:
            continue
        starSize = GetStarSizeByDataValue(levelInfo.level, maxLevel)
        colorInfo.solarSystemDict[solarSystemID] = (starSize,
         None,
         (hintFunc, (indexName, levelInfo.level)),
         color)

    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/devIndxDevloped'), color, data=None))
    colorInfo.colorType = STAR_COLORTYPE_DATA


def GetStarSizeByDataValue(value, maxValue, minValue = 0.0, numValues = None):
    range = float(maxValue - minValue)
    if range:
        x = (value - minValue) / range
        ret = STAR_SIZE_FACTOR_STANDARD + x * (STAR_SIZE_FACTOR_MAX - STAR_SIZE_FACTOR_STANDARD)
    else:
        ret = STAR_SIZE_FACTOR_STANDARD
    if numValues is not None:
        x = 2.0 - min(numValues / 30.0, 1.25)
        ret *= x
    return 2 * ret


def ColorStarsByAssets(colorInfo, starColorMode):
    myassets = sm.GetService('assets').GetAll('allitems')
    bySystemID = {}
    stuffToPrime = []
    for solarsystemID, station in myassets:
        stuffToPrime.append(station.stationID)
        stuffToPrime.append(solarsystemID)
        if solarsystemID not in bySystemID:
            bySystemID[solarsystemID] = []
        bySystemID[solarsystemID].append(station)

    if stuffToPrime:
        cfg.evelocations.Prime(stuffToPrime)

    def hintFunc(stationData, solarSystemID):
        hint = ''
        for station in stationData:
            shortStationName = EditStationName(cfg.evelocations.Get(station.stationID).name, usename=1)
            subc = GetByLabel('UI/Map/StarModeHandler/StationNameWithItemCount', shortStationName=shortStationName, numItems=station.itemCount)
            if hint:
                hint += '<br>'
            hint += '<url=localsvc:method=ShowAssets&stationID=%d>%s</url>' % (station.stationID, subc)

        return hint

    _PrepareStandardColorData(colorInfo, bySystemID, hintFunc=hintFunc, hintArgs=None, amountKey='itemCount')
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/assetsHasAssets'), COLOR_ASSETS, data=None))


def ColorStarsByVisited(colorInfo, starColorMode):
    history = sm.RemoteSvc('map').GetSolarSystemVisits()
    visited = []
    maxValue = 0
    for entry in history:
        visited.append((entry.lastDateTime, entry.solarSystemID, entry.visits))
        maxValue = max(maxValue, entry.visits)

    visited.sort()
    if len(visited):
        divisor = 1.0 / float(len(visited))
    hintFunc = lambda solarSystemID, visits, lastDateTime: GetByLabel('UI/Map/ColorModeHandler/VisitedLastVisit', count=visits, lastVisit=lastDateTime)
    for i, (lastDateTime, solarSystemID, visits) in enumerate(visited):
        starSize = GetStarSizeByDataValue(visits, maxValue)
        colorInfo.solarSystemDict[solarSystemID] = (starSize,
         float(i) * divisor,
         (hintFunc, (solarSystemID, visits, lastDateTime)),
         None)

    colorInfo.colorList = INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsBySecurity(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    securitySvc = sm.GetService('securitySvc')
    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        secStatus = securitySvc.get_modified_security_level(solarSystemID)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         secStatus,
         None,
         None)

    colorInfo.colorList = COLORCURVE_SECURITY
    for i in xrange(0, 11):
        lbl = GetByLabel('UI/Map/StarModeHandler/securityLegendItem', level=1.0 - i * 0.1)
        colorInfo.legend.add(LegendItem(i, lbl, COLORCURVE_SECURITY[10 - i], data=None))


def ColorStarsBySovChanges(colorInfo, starColorMode, changeMode):
    if changeMode == mapcommon.SOV_CHANGES_SOV_GAIN:
        color = NEG_NEU_POS_3RANGE[2]
    elif changeMode == mapcommon.SOV_CHANGES_SOV_LOST:
        color = NEG_NEU_POS_3RANGE[0]
    else:
        color = NEG_NEU_POS_3RANGE[1]
    changes = GetSovChangeList(changeMode)
    hintFunc = lambda comments: '<br>'.join(comments)
    if changes:
        maxValue = max([ len(comments) for solarSystemID, comments in changes.iteritems() ])
        for solarSystemID, comments in changes.iteritems():
            starSize = GetStarSizeByDataValue(len(comments), maxValue)
            colorInfo.solarSystemDict[solarSystemID] = (starSize,
             None,
             (hintFunc, (comments,)),
             color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/sovereigntyNoSovChanges'), NEUTRAL_COLOR, None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/sovereigntySovChanges'), color, None))
    colorInfo.colorType = STAR_COLORTYPE_DATA


def GetSovChangeList(changeMode):
    data = sm.GetService('sov').GetRecentActivity()
    changes = []
    resultMap = {}
    toPrime = set()
    for item in data:
        if item.stationID is None:
            if bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.ownerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovGained', (None, item.ownerID)))
                toPrime.add(item.ownerID)
            elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_LOST) and item.oldOwnerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovLost', (item.oldOwnerID, None)))
                toPrime.add(item.oldOwnerID)

    cfg.eveowners.Prime(list(toPrime))
    for solarSystemID, text, owners in changes:
        if owners[0]:
            ownerData = cfg.eveowners.Get(owners[0])
            oldOwner = '<url=showinfo:%d//%d>%s</url>' % (ownerData.typeID, owners[0], ownerData.ownerName)
        else:
            oldOwner = ''
        if owners[1]:
            ownerData = cfg.eveowners.Get(owners[1])
            owner = '<url=showinfo:%d//%d>%s</url>' % (ownerData.typeID, owners[1], ownerData.ownerName)
        else:
            owner = ''
        if solarSystemID not in resultMap:
            resultMap[solarSystemID] = []
        resultMap[solarSystemID].append(GetByLabel(text, owner=owner, oldOwner=oldOwner))

    return resultMap


def ColorStarsByCorporationSettledSystems(colorInfo, starColorMode):
    corporationID = starColorMode[1]
    solarSystems = sm.RemoteSvc('config').GetStationSolarSystemsByOwner(corporationID)
    colorInfo.colorType = STAR_COLORTYPE_DATA
    corporationName = cfg.eveowners.Get(corporationID).name
    mapHintCallback = lambda : GetByLabel('UI/InfoWindow/SystemSettledByCorp', corpName=corporationName)
    for solarSystem in solarSystems:
        colorInfo.solarSystemDict[solarSystem.solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         None,
         (mapHintCallback, ()),
         (1.0, 0.0, 0.0, 1.0))


def ColorStarsByDynamicBountyOutput(colorInfo, starColorMode):
    solarSystems = sm.RemoteSvc('dynamicResourceCacheMgr').GetDBSMapData()
    settings = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()
    colorInfo.colorType = STAR_COLORTYPE_DATA
    minVal = settings['minOutput']
    maxVal = settings['maxOutput']
    eq = settings['equilibriumValue']
    for solarSystem in solarSystems:
        systemValue = solarSystems[solarSystem]
        distance = (systemValue - minVal) * 100 / (maxVal - minVal) / 100
        clampedDistance = min(max(0.0, distance), 1.0)
        significanceExponent = 0
        if systemValue <= eq:
            significanceExponent = 3
        starSize = GetStarSizeByDataValue(systemValue, maxVal, minValue=minVal) * clampedDistance ** significanceExponent
        mapHintCallback = lambda systemValue: GetByLabel('UI/Map/ColorModeHandler/BountyOutputHint', output=systemValue * 100)
        color = GetESSBountyColor(minVal, maxVal, eq, systemValue)
        colorInfo.solarSystemDict[solarSystem] = (starSize,
         None,
         (mapHintCallback, (systemValue,)),
         (color[0],
          color[1],
          color[2],
          float(color[3]) * clampedDistance))


def _GetValueForInterferenceBand(interferenceBand):
    if interferenceBand == INTERFERENCE_BAND_NONE:
        return 0.0
    if interferenceBand == INTERFERENCE_BAND_LOW:
        return 33.0
    if interferenceBand == INTERFERENCE_BAND_MEDIUM:
        return 66.0
    if interferenceBand == INTERFERENCE_BAND_HIGH:
        return 100.0


def _GetInterferenceBandFromMapPlaceholderValue(placeholderValue):
    high = _GetValueForInterferenceBand(INTERFERENCE_BAND_HIGH)
    low = _GetValueForInterferenceBand(INTERFERENCE_BAND_LOW)
    med = _GetValueForInterferenceBand(INTERFERENCE_BAND_MEDIUM)
    if placeholderValue == high:
        return INTERFERENCE_BAND_HIGH
    if placeholderValue == low:
        return INTERFERENCE_BAND_LOW
    if placeholderValue == med:
        return INTERFERENCE_BAND_MEDIUM
    return INTERFERENCE_BAND_NONE


def ColorStarsBySolarSystemInterference(colorInfo, _starColorMode):
    interferenceSvc = sm.GetService('solarsystemInterferenceSvc')
    interferenceBands = interferenceSvc.GetAllInterferenceBands()
    hintFunc = lambda interference, _: GetByLabel('UI/Map/StarModeHandler/interference', interference=GetInterferenceBandLabel(_GetInterferenceBandFromMapPlaceholderValue(interference)))
    interferenceMapData = {}
    for solarsystemID, interferenceBand in interferenceBands.iteritems():
        if interferenceBand != INTERFERENCE_BAND_NONE:
            interferenceMapData[solarsystemID] = _GetValueForInterferenceBand(interferenceBand)

    _PrepareStandardColorData(colorInfo, interferenceMapData, hintFunc=hintFunc, colorList=INTENSITY_COLORRANGE)


def ColorStarsBySuppressionValue(colorInfo, _starColorMode):
    insurgencySvc = sm.GetService('insurgencyCampaignSvc')
    corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
    snapshots = insurgencySvc.GetCurrentCampaignSnapshots_Memoized()
    insurgencyMapData = {}
    nameData = {}
    suppressionStage = {}

    def hintFunc(_data, solarsystemid):
        factionName = nameData[solarsystemid]
        return u'{}<br/>{}<br/>{}'.format(GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency'), factionName, GetByLabel('UI/PirateInsurgencies/stageLabel', stage=suppressionStage[solarsystemid]))

    for snapshot in snapshots:
        for solarsystemid in snapshot.coveredSolarsystemIDs:
            systemData = corruptionSuppressionSvc.GetSystemSuppression(solarsystemid)
            if systemData is not None:
                insurgencyMapData[solarsystemid] = systemData.totalProportion
                nameData[solarsystemid] = get_faction_name(snapshot.pirateFactionID)
                suppressionStage[solarsystemid] = systemData.stage

    _PrepareStandardColorData(colorInfo, insurgencyMapData, hintFunc=hintFunc, colorList=[eveColor.WHITE, eveColor.WHITE])


def ColorStarsByCorruptionValue(colorInfo, _starColorMode):
    insurgencySvc = sm.GetService('insurgencyCampaignSvc')
    corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
    snapshots = insurgencySvc.GetCurrentCampaignSnapshots_Memoized()
    insurgencyMapData = {}
    nameData = {}
    corruptionStage = {}

    def hintFunc(_data, solarsystemid):
        factionName = nameData[solarsystemid]
        return u'{}<br/>{}<br/>{}'.format(GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency'), factionName, GetByLabel('UI/PirateInsurgencies/stageLabel', stage=corruptionStage[solarsystemid]))

    for snapshot in snapshots:
        for solarsystemid in snapshot.coveredSolarsystemIDs:
            systemData = corruptionSuppressionSvc.GetSystemCorruption(solarsystemid)
            if systemData is not None:
                insurgencyMapData[solarsystemid] = systemData.totalProportion
                nameData[solarsystemid] = get_faction_name(snapshot.pirateFactionID)
                corruptionStage[solarsystemid] = systemData.stage

    _PrepareStandardColorData(colorInfo, insurgencyMapData, hintFunc=hintFunc, colorList=[eveColor.WHITE, Color.HextoRGBA('#9EFF00')])


def ColorStarsByInsurgencyInvolvement(colorInfo, _starColorMode):
    insurgencySvc = sm.GetService('insurgencyCampaignSvc')
    corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
    snapshots = insurgencySvc.GetCurrentCampaignSnapshots_Memoized()
    insurgencyMapData = {}
    nameData = {}
    corruptionSuppressionValue = {}
    for snapshot in snapshots:
        for solarsystemid in snapshot.coveredSolarsystemIDs:
            insurgencyMapData[solarsystemid] = 1.0
            nameData[solarsystemid] = get_faction_name(snapshot.pirateFactionID)
            corruptionStage = corruptionSuppressionSvc.GetSystemCorruptionStage(solarsystemid)
            suppressionStage = corruptionSuppressionSvc.GetSystemSuppressionStage(solarsystemid)
            corruptionSuppressionValue[solarsystemid] = (corruptionStage, suppressionStage)

    def hintFunc(_data, solarsystemid):
        factionName = nameData[solarsystemid]
        corruption, suppression = corruptionSuppressionValue[solarsystemid]
        if corruption == 5:
            maxStageLabel = GetByLabel('UI/PirateInsurgencies/maxCorruption')
            return u'{}<br/>{}<br/>{}'.format(GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency'), factionName, maxStageLabel)
        elif suppression == 5:
            maxStageLabel = GetByLabel('UI/PirateInsurgencies/maxSuppression')
            return u'{}<br/>{}<br/>{}'.format(GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency'), factionName, maxStageLabel)
        else:
            return u'{}<br/>{}'.format(GetByLabel('UI/PirateInsurgencies/systemAffectedByInsurgency'), factionName)

    _PrepareStandardColorData(colorInfo, insurgencyMapData, hintFunc=hintFunc, colorList=[eveColor.WHITE, Color.HextoRGBA('#9EFF00')])


def ColorStarsByFactionStandings(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    colorByFaction = {}
    neutral = COLOR_STANDINGS_NEUTRAL
    for factionID in mapViewData.GetAllFactionsAndAlliances():
        color = starmap.GetColorByStandings(factionID)
        if len(color) == 3:
            color = tuple(color) + (1.0,)
        colorByFaction[factionID] = color

    lbl = GetByLabel('UI/Map/StarModeHandler/factionStandings')
    hintFunc = lambda : lbl
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        color = colorByFaction.get(solarSystem.factionID, neutral)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         None,
         (hintFunc, ()),
         color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/factionGoodStandings'), COLOR_STANDINGS_GOOD, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/factionNeutralStandings'), COLOR_STANDINGS_NEUTRAL, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/factionBadStandings'), COLOR_STANDINGS_BAD, data=None))


def GetColorStarsByFactionSearchArgs():
    return settings.char.ui.Get('mapView_GetColorStarsByFactionSearchArgs', None)


def SetColorStarsByFactionSearchArgs(filterFactionID):
    return settings.char.ui.Set('mapView_GetColorStarsByFactionSearchArgs', filterFactionID)


def ColorStarsByFactionSearch(colorInfo, starColorMode):
    filterFactionID = GetColorStarsByFactionSearchArgs()
    return _ColorStarsByFaction(colorInfo, filterFactionID)


def ColorStarsByFaction(colorInfo, starColorMode):
    return _ColorStarsByFaction(colorInfo, None)


def _ColorStarsByFaction(colorInfo, factionID):
    starmap = sm.GetService('starmap')
    allianceSolarSystems = mapViewData.GetAllianceSolarSystems()
    sovBySolarSystemID = {}
    toPrime = set()
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        if factionID == mapcommon.STARMODE_FILTER_EMPIRE:
            secClass = starmap.map.GetSecurityStatus(solarSystemID)
            if not IsFaction(solarSystem.factionID) or secClass == const.securityClassZeroSec:
                continue
        sovHolderID = starmap._GetFactionIDFromSolarSystem(allianceSolarSystems, solarSystemID)
        if sovHolderID is None:
            continue
        if factionID >= 0 and sovHolderID != factionID:
            continue
        sovBySolarSystemID[solarSystemID] = sovHolderID
        toPrime.add(sovHolderID)

    cfg.eveowners.Prime(list(toPrime))
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/factionSovereignty', name=name)
    for solarSystemID, sovHolderID in sovBySolarSystemID.iteritems():
        name = cfg.eveowners.Get(sovHolderID).name
        col = GetBase11ColorByID(sovHolderID)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         None,
         (hintFunc, (name,)),
         col)
        colorInfo.legend.add(LegendItem(None, name, col, data=sovHolderID))


def ColorStarsByMilitia(colorInfo, starColorMode):
    factionID = starColorMode[1]
    if factionID < -1:
        log.error('Invalid factionID %s' % factionID)
        return
    fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
    maxPointsByFaction = defaultdict(lambda : 1)
    occupiedSystems = {}
    occupationStatesBySolarsystemByWarzone = sm.GetService('fwWarzoneSvc').GetAllOccupationStates()
    for occupationStatesBySolarsystem in occupationStatesBySolarsystemByWarzone.itervalues():
        for solarsystemID, occupationState in occupationStatesBySolarsystem.iteritems():
            occupierID = occupationState.occupierID
            if occupierID == factionID or factionID == -1:
                victoryPointState = fwVictoryPointSvc.GetVictoryPointState(solarsystemID)
                if victoryPointState is not None:
                    maxPointsByFaction[occupierID] = max(victoryPointState.score, maxPointsByFaction[occupierID])
                    occupiedSystems[solarsystemID] = (occupierID, victoryPointState)

    for solarSystemID, (occupierID, victoryPointState) in occupiedSystems.iteritems():
        size = GetStarSizeByDataValue(victoryPointState.score, maxPointsByFaction[occupierID])
        col = GetBase11ColorByID(occupierID)
        colorInfo.solarSystemDict[solarSystemID] = (size,
         None,
         (GetFWHint, (occupierID, victoryPointState)),
         col)
        colorInfo.colorType = STAR_COLORTYPE_DATA


def GetFWHint(ownerID, victoryPointState):
    return GetByLabel('UI/Map/StarModeHandler/militiaSystemStatus', name=cfg.eveowners.Get(ownerID).name, status=GetVictoryPointStateText(victoryPointState))


def ColorStarsByRegion(colorInfo, starColorMode):
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/regionNameEntry', name=name)
    for regionID, region in mapViewData.GetKnownUniverseRegions().iteritems():
        regionName = cfg.evelocations.Get(regionID).name
        col = BASE5_COLORRANGE[regionID % len(BASE5_COLORRANGE)]
        for solarSystemID in region.solarSystemIDs:
            colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
             None,
             (hintFunc, (regionName,)),
             col)

        colorInfo.legend.add(LegendItem(None, regionName, col, data=regionID))


def HintCargoIllegality(attackTypeIDs, confiscateTypeIDs):
    systemDescription = ''
    for typeID in attackTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityAttackHint', stuff=evetypes.GetName(typeID))

    for typeID in confiscateTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityConfiscateHint', item=evetypes.GetName(typeID))

    return systemDescription


def ColorStarsByCargoIllegality(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    invCache = sm.GetService('invCache')
    activeShipID = GetActiveShip()
    if activeShipID is None:
        shipCargo = []
    else:
        inv = invCache.GetInventoryFromId(activeShipID, locationID=session.stationid)
        shipCargo = inv.List()
    factionIllegality = {}
    while len(shipCargo) > 0:
        item = shipCargo.pop(0)
        if item.groupID in [const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer]:
            shipCargo.extend(invCache.GetInventoryFromId(item.itemID).List())
        itemIllegalities = inventorycommon.typeHelpers.GetIllegality(item.typeID)
        if itemIllegalities:
            for factionID, illegality in itemIllegalities.iteritems():
                if factionID not in factionIllegality:
                    factionIllegality[factionID] = {}
                if item.typeID not in factionIllegality[factionID]:
                    factionIllegality[factionID][item.typeID] = [max(0.0, illegality.confiscateMinSec), max(0.0, illegality.attackMinSec)]

    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        colour = None
        factionID = solarSystem.factionID
        if factionID is None or factionID not in factionIllegality:
            continue
        systemIllegality = False
        attackTypeIDs = []
        confiscateTypeIDs = []
        securityStatus = starmap.map.GetSecurityStatus(solarSystemID)
        for typeID in factionIllegality[factionID]:
            if securityStatus >= factionIllegality[factionID][typeID][1]:
                systemIllegality = True
                if not colour or colour[0] < 2:
                    colour = (2, ATTACKED_COLOR)
                attackTypeIDs.append(typeID)
            elif securityStatus >= factionIllegality[factionID][typeID][0]:
                systemIllegality = True
                if not colour:
                    colour = (1, CONFISCATED_COLOR)
                confiscateTypeIDs.append(typeID)

        if systemIllegality:
            colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
             0.0,
             (HintCargoIllegality, (attackTypeIDs, confiscateTypeIDs)),
             colour[1])

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/legalityNoConsequences'), NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/legalityConfiscate'), CONFISCATED_COLOR, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/legalityWillAttack'), ATTACKED_COLOR, data=None))


def ColorStarsByNumPilots(colorInfo, starColorMode):
    infoOnPilotsBySolarSystemIDs = sm.GetService('map').GetInfoOnPilotsBySolarSystemIDs()
    pilotcountDict = {}
    for solarSystemID, info in infoOnPilotsBySolarSystemIDs.iteritems():
        if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
            amount = info.amountInSpace
        else:
            amount = info.amountDocked
        if amount:
            pilotcountDict[solarSystemID] = amount

    if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/PilotsInSpace', count=count)
    else:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/PilotsInStation', count=count)
    _PrepareStandardColorData(colorInfo, pilotcountDict, hintFunc=hintFunc, colorList=INTENSITY_COLORRANGE)


def ColorStarsByStationCount(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starmap.stationCountCache is None:
        starmap.stationCountCache = sm.RemoteSvc('map').GetStationCount()
    history = starmap.stationCountCache
    hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/StationsCount', count=count)
    _PrepareStandardColorData(colorInfo, dict(history), hintFunc=hintFunc)


def HintDungeons(dungeons):
    comments = []
    for dungeonID, difficulty, dungeonName in dungeons:
        ded = ''
        if difficulty:
            ded = GetByLabel('UI/Map/ColorModeHandler/DungeonDedDifficulty', count=difficulty)
        comments.append(GetByLabel('UI/Map/ColorModeHandler/DungeonDedLegendHint', dungeonName=dungeonName, dedName=ded))

    return '<br>'.join(comments)


def ColorStarsByDungeons(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_DUNGEONS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceComplexMap(eve.session.languageID)
    elif starColorMode == mapcommon.STARMODE_DUNGEONSAGENTS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceAgentsMap(eve.session.languageID)
    if dungeons is None:
        return
    solmap = {}
    for solarSystemID, dungeonID, difficulty, dungeonName in dungeons:
        solmap.setdefault(solarSystemID, []).append((dungeonID, difficulty, dungeonName))

    maxDungeons = max([ len(solarSystemDungeons) for solarSystemID, solarSystemDungeons in solmap.iteritems() ])
    numValues = len(solmap)
    for solarSystemID, solarSystemDungeons in solmap.iteritems():
        maxDifficulty = 1
        for dungeonID, difficulty, dungeonName in solarSystemDungeons:
            if difficulty:
                maxDifficulty = max(maxDifficulty, difficulty)

        maxDifficulty = (10 - maxDifficulty) / 9.0
        starSize = GetStarSizeByDataValue(len(solarSystemDungeons), maxDungeons, numValues=numValues)
        colorInfo.solarSystemDict[solarSystemID] = (starSize,
         maxDifficulty,
         (HintDungeons, (solarSystemDungeons,)),
         None)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.colorList = COLORCURVE_SECURITY
    colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
    for i in xrange(0, 10):
        lbl = GetByLabel('UI/Map/StarModeHandler/dungeonDedLegendDiffaculty', difficulty=i + 1)
        colorInfo.legend.add(LegendItem(i, lbl, starmap.GetColorCurveValue(colorCurve, (9 - i) / 9.0), data=None))


def ColorStarsByJumps1Hour(colorInfo, starColorMode):
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatJumps, 1)
    history = {}
    for entry in historyDB:
        if entry.value1 > 0:
            history[entry.solarSystemID] = entry.value1

    hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/JumpsLastHour', count=count)
    _PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc)


def ColorStarsByKills(colorInfo, starColorMode, statID, hours):
    historyDB = sm.RemoteSvc('map').GetHistory(statID, hours)
    history = {}
    for entry in historyDB:
        if entry.value1 - entry.value2 > 0:
            history[entry.solarSystemID] = entry.value1 - entry.value2

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsShipsInLast', count=count, hours=hours)
    _PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByPodKills(colorInfo, starColorMode):
    if starColorMode == mapcommon.STARMODE_PODKILLS24HR:
        hours = 24
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 24)
    else:
        hours = 1
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 1)
    history = {}
    for entry in historyDB:
        if entry.value3 > 0:
            history[entry.solarSystemID] = entry.value3

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsPodInLast', hours=hours, count=count)
    _PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByFactionKills(colorInfo, starColorMode):
    hours = 24
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, hours)
    history = {}
    for entry in historyDB:
        if entry.value2 > 0:
            history[entry.solarSystemID] = entry.value2

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsFactionInLast', hours=hours, count=count)
    _PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByCynosuralFields(colorInfo, starColorMode):
    fleetBeaconCount = sm.RemoteSvc('map').GetBeaconCount()
    solarSystemsWithBeacons = sm.GetService('structureDirectory').GetSolarSystemsWithBeacons()
    orange = COLOR_ORANGE
    green = COLOR_GREEN
    red = COLOR_RED
    hintFuncTotal = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGeneratorsNumber', count=count)
    hintFuncModule = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsNumber', count=count)
    hintFuncStructure = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveGeneratorNumber', count=count)
    maxModule = 0
    maxStructure = 0
    for solarSystemID, moduleCnt in fleetBeaconCount.iteritems():
        maxModule = max(maxModule, moduleCnt)

    if solarSystemsWithBeacons:
        maxStructure = 1
    allSolarSystemIDs = set(fleetBeaconCount.keys()).union(solarSystemsWithBeacons)
    for eachSolarSystemID in allSolarSystemIDs:
        moduleCnt = fleetBeaconCount.get(eachSolarSystemID, 0)
        structureCnt = 1 if eachSolarSystemID in solarSystemsWithBeacons else 0
        if moduleCnt > 0 and structureCnt > 0:
            ttlcnt = moduleCnt + structureCnt
            starSize = GetStarSizeByDataValue(ttlcnt, maxModule + maxStructure)
            colorInfo.solarSystemDict[eachSolarSystemID] = (starSize,
             1.0,
             (hintFuncTotal, (ttlcnt,)),
             red)
        elif moduleCnt:
            starSize = GetStarSizeByDataValue(moduleCnt, maxModule)
            colorInfo.solarSystemDict[eachSolarSystemID] = (starSize,
             1.0,
             (hintFuncModule, (moduleCnt,)),
             green)
        elif structureCnt:
            starSize = GetStarSizeByDataValue(structureCnt, maxStructure)
            colorInfo.solarSystemDict[eachSolarSystemID] = (starSize,
             1.0,
             (hintFuncStructure, (structureCnt,)),
             orange)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/cynoActiveFields'), green, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/cynoActiveGenerators'), orange, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGenerators'), red, data=None))


def ColorStarsByCorpAssets(colorInfo, starColorMode, assetKey, legendName):
    rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, assetKey)
    solarsystems = {}
    stuffToPrime = []
    for row in rows:
        stationID = row.locationID
        try:
            solarsystemID = sm.GetService('ui').GetStationStaticInfo(row.locationID).solarSystemID
        except:
            solarsystemID = row.locationID

        if solarsystemID not in solarsystems:
            solarsystems[solarsystemID] = {}
            stuffToPrime.append(solarsystemID)
        if stationID not in solarsystems[solarsystemID]:
            solarsystems[solarsystemID][stationID] = []
            stuffToPrime.append(stationID)
        solarsystems[solarsystemID][stationID].append(row)

    cfg.evelocations.Prime(stuffToPrime)
    hintFunc = lambda stations, solarSystemID: '<br>'.join([ cfg.evelocations.Get(stationID).name for stationID in stations ])
    _PrepareStandardColorData(colorInfo, solarsystems, hintFunc=hintFunc)


def _IsServiceAvailable(serviceTypeID, solarSystemID, stationID, ownerID, operationID, stations):
    isRepairService = serviceTypeID == const.stationServiceRepairFacilities
    if isRepairService and IsRepairServiceAvailable(solarSystemID):
        return True
    if operationID == None or not service_in_station_operation(operationID, serviceTypeID):
        return False
    isMilitiaService = serviceTypeID == const.stationServiceNavyOffices
    if isMilitiaService and ownerID not in sm.GetService('starmap').GetWarFactionByOwner(stations):
        return False
    isSecurityService = serviceTypeID == const.stationServiceSecurityOffice
    if isSecurityService and not sm.GetService('securityOfficeSvc').CanAccessServiceInStation(stationID):
        return False
    return True


def ColorStarsByServices(colorInfo, starColorMode, serviceTypeID):
    stationIDs = []
    solarsystems = defaultdict(list)
    stations = sm.RemoteSvc('map').GetStationInfo()
    for stationRow in stations:
        stationID = stationRow.stationID
        solarSystemID = stationRow.solarSystemID
        ownerID = stationRow.ownerID
        operationID = stationRow.operationID
        if _IsServiceAvailable(serviceTypeID, solarSystemID, stationID, ownerID, operationID, stations):
            solarsystems[solarSystemID].append(stationID)
            stationIDs.append(stationID)

    cfg.evelocations.Prime(stationIDs)

    def hintFunc(stationIDs):
        hint = ''
        for stationID in stationIDs:
            station = sm.StartService('ui').GetStationStaticInfo(stationID)
            stationName = cfg.evelocations.Get(stationID).name
            stationTypeID = station.stationTypeID
            if hint:
                hint += '<br>'
            hint += '<url=showinfo:%d//%d>%s</url>' % (stationTypeID, stationID, stationName)

        return hint

    countAll = [ len(stationIDs) for solarSystemID, stationIDs in solarsystems.iteritems() ]
    maxCount = max(countAll)
    for solarsystemID, stationIDs in solarsystems.iteritems():
        starSize = GetStarSizeByDataValue(len(stationIDs), maxCount, numValues=len(countAll))
        colorValue = len(stationIDs) / float(maxCount)
        colorInfo.solarSystemDict[solarsystemID] = (starSize,
         colorValue,
         (hintFunc, (stationIDs,)),
         None)

    colorInfo.colorList = INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsByFleetMembers(colorInfo, starColorMode):
    fleetComposition = sm.GetService('fleet').GetFleetComposition()
    if fleetComposition is not None:
        solarSystems = defaultdict(list)
        for each in fleetComposition:
            solarSystems[each.solarSystemID].append(each.characterID)

        def hintFunc(characterIDs, solarSystemID):
            return '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])

        _PrepareStandardColorData(colorInfo, solarSystems, hintFunc=hintFunc)


def ColorStarsByCorpMembers(colorInfo, starColorMode):
    corp = sm.RemoteSvc('map').GetMyExtraMapInfo()
    if corp is not None:
        solarSystems = defaultdict(list)
        for each in corp:
            if IsSolarSystem(each.locationID):
                solarSystems[each.locationID].append(each.characterID)

        def hintFunc(characterIDs, solarSystemID):
            if len(characterIDs) > 10:
                return GetByLabel('UI/Map/ColorModeHandler/CountCorporationMembers', count=len(characterIDs))
            else:
                return '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])

        _PrepareStandardColorData(colorInfo, solarSystems, hintFunc=hintFunc)


def ColorStarsByMyAgents(colorInfo, starColorMode):
    standingInfo = sm.RemoteSvc('map').GetMyExtraMapInfoAgents().Index('fromID')
    solarsystems = {}
    valid = (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent)
    agentsByID = sm.GetService('agents').GetAgentsByID()
    facWarService = sm.GetService('facwar')
    skills = {}
    for agentID in agentsByID:
        agent = agentsByID[agentID]
        fa = standingInfo.get(agent.factionID, 0.0)
        if fa:
            fa = fa.rank * 10.0
        co = standingInfo.get(agent.corporationID, 0.0)
        if co:
            co = co.rank * 10.0
        ca = standingInfo.get(agent.agentID, 0.0)
        if ca:
            ca = ca.rank * 10.0
        isLimitedToFacWar = False
        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarService.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            isLimitedToFacWar = True
        if agent.agentTypeID in valid and CanUseAgent(agent.level, agent.agentTypeID, fa, co, ca, agent.corporationID, agent.factionID, skills) and isLimitedToFacWar == False:
            if agent.stationID:
                solarsystems.setdefault(agent.solarsystemID, []).append(agent)

    def hintFunc(agents, solarSystemID):
        caption = ''
        for agent in agents:
            agentOwner = cfg.eveowners.Get(agent.agentID)
            agentString = GetByLabel('UI/Map/StarModeHandler/agentCaptionDetails', divisionName=get_division_name(agent.divisionID), agentName=agentOwner.name, level=agent.level)
            if caption:
                caption += '<br>'
            caption += '<url=showinfo:%d//%d>%s</url>' % (agentOwner.typeID, agent.agentID, agentString)

        return caption

    _PrepareStandardColorData(colorInfo, solarsystems, hintFunc=hintFunc, colorList=MIN_MAX_COLORRANGE)


def ColorStarsByJumpClones(colorInfo, starColorMode):
    bySystemID = GetJumpClonesBySystemID()

    def hintFunc(cloneData, solarSystemID):
        hintList = []
        for eachClone in cloneData:
            cloneHint = '%s - %s' % (eachClone.name, EditStationName(cfg.evelocations.Get(eachClone.location_id).name, usename=1))
            hintList.append(cloneHint)

        return '<br>'.join(hintList)

    _PrepareStandardColorData(colorInfo, dict(bySystemID), hintFunc=hintFunc)


def ColorStarsByAvoidedSystems(colorInfo, starColorMode):
    avoidanceSolarSystemIDs = sm.GetService('clientPathfinderService').GetExpandedAvoidanceItems()
    hintFunc = lambda : GetByLabel('UI/Map/StarModeHandler/advoidSystemOnList')
    for solarSystemID in avoidanceSolarSystemIDs:
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         1.0,
         (hintFunc, ()),
         COLOR_RED)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/advoidNotAdvoided'), NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/advoidAdvoided'), DEFAULT_MAX_COLOR, data=None))


def ColorStarsByRealSunColor(colorInfo, starColorMode):
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
         0.0,
         None,
         solarSystem.star.color)

    for typeID, sunType in mapcommon.SUN_DATA.iteritems():
        name = evetypes.GetName(typeID)
        colorInfo.legend.add(LegendItem(name, name, sunType.color, data=None))


def ColorStarsByPIScanRange(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    playerLoc = cfg.evelocations.Get(session.solarsystemid2)
    playerPos = (playerLoc.x, playerLoc.y, playerLoc.z)
    remoteSensing = sm.GetService('skills').GetEffectiveLevel(appConst.typeRemoteSensing) or 0
    hintFunc = lambda range: GetByLabel('UI/Map/StarModeHandler/scanHintDistance', range=range)
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        systemLoc = cfg.evelocations.Get(solarSystemID)
        systemPos = (systemLoc.x, systemLoc.y, systemLoc.z)
        dist = geo2.Vec3Distance(playerPos, systemPos) / appConst.LIGHTYEAR
        proximity = None
        for i, each in enumerate(appConst.planetResourceScanningRanges):
            if not i >= 5 - remoteSensing:
                continue
            if each >= dist:
                proximity = i

        if proximity is not None:
            colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_FACTOR_STANDARD,
             None,
             (hintFunc, (dist,)),
             COLOR_GREEN)

    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsByPlanetType(colorInfo, starColorMode):
    planetTypeID = starColorMode[1]
    systems = defaultdict(int)
    for solarSystemID, d in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        if planetTypeID in d.planetCountByType:
            systems[solarSystemID] = v = d.planetCountByType[planetTypeID]

    def hintFunc(amount, solarSystemID):
        planetTypeName = evetypes.GetName(planetTypeID)
        return '%s: %d' % (planetTypeName, amount)

    _PrepareStandardColorData(colorInfo, systems, hintFunc=hintFunc)


def ColorStarsByMyColonies(colorInfo, starColorMode):
    planetSvc = sm.GetService('planetSvc')
    planetRows = planetSvc.GetMyPlanets()
    if len(planetRows):
        systems = defaultdict(int)
        for row in planetRows:
            systems[row.solarSystemID] += 1

        def hintFunc(count, solarSystemID):
            return GetByLabel('UI/Map/StarModeHandler/planetsColoniesCount', count=count)

        _PrepareStandardColorData(colorInfo, systems, hintFunc=hintFunc)


def ColorStarsByIncursions(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursions()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystem(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), BASE3_COLORRANGE[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionPraticipant'), BASE3_COLORRANGE[-1], data=None))


def ColorStarsByRoamingWeather(colorInfo, starColorMode):
    ms = sm.GetService('map')
    participatingSystems = ms.GetAllRoamingWeatherSystems()
    for solarSystem in participatingSystems:
        if solarSystem.locationID in colorInfo.solarSystemDict:
            color = colorInfo.solarSystemDict[solarSystem.locationID][3]
            if color == COLOR_RED:
                continue
            if color == COLOR_ORANGE and solarSystem.sceneType != taleConst.scenesTypes.onionHeadquarters:
                continue
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintRoamingWeatherSystems(solarSystem.sceneType)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/roamingWeather'), COLOR_RED, data=None))


def ColorStarsByIncursionsGM(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursions()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystemGm(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_GREEN, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionVanguard'), COLOR_YELLOW, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/incursionAssault'), COLOR_ORANGE, data=None))
    colorInfo.legend.add(LegendItem(3, GetByLabel('UI/Map/StarModeHandler/incursionHQ'), COLOR_RED, data=None))
    colorInfo.legend.add(LegendItem(4, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_WHITE, data=None))
    colorInfo.legend.add(LegendItem(5, 'Incursion Spread', COLOR_GRAY, data=None))
    colorInfo.legend.add(LegendItem(6, 'Incursion Final Encounter', COLOR_PURPLE, data=None))


def GetColorAndHintForIncursionSystem(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType in (taleConst.scenesTypes.staging, taleConst.scenesTypes.incursionStaging):
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionStageing')
        return (3.0 * STAR_SIZE_FACTOR_MAX,
         0,
         (incursionHint, ()),
         BASE3_COLORRANGE[0])
    else:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionPraticipant')
        return (1.5 * STAR_SIZE_FACTOR_MAX,
         1,
         (incursionHint, ()),
         BASE3_COLORRANGE[-1])


def GetColorAndHintRoamingWeatherSystems(sceneType):
    hint = lambda : GetByLabel('UI/Map/StarModeHandler/roamingWeather')
    if sceneType == taleConst.scenesTypes.onionHeadquarters:
        size = 2 * STAR_SIZE_FACTOR_MAX
        color = COLOR_RED
    elif sceneType == taleConst.scenesTypes.onionJump1:
        size = 1.5 * STAR_SIZE_FACTOR_MAX
        color = COLOR_ORANGE
    else:
        size = STAR_SIZE_FACTOR_MAX
        color = COLOR_YELLOW
    return (size,
     0,
     (hint, ()),
     color)


def GetColorAndHintForIncursionSystemGm(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType == taleConst.scenesTypes.staging:
        return (1.0,
         0,
         (lambda : distributionName + 'Staging', ()),
         COLOR_GREEN)
    if sceneType == taleConst.scenesTypes.vanguard:
        return (0.5,
         1,
         (lambda : distributionName + 'Vanguard', ()),
         COLOR_YELLOW)
    if sceneType == taleConst.scenesTypes.assault:
        return (0.5,
         2,
         (lambda : distributionName + 'Assault', ()),
         COLOR_ORANGE)
    if sceneType == taleConst.scenesTypes.headquarters:
        return (0.5,
         3,
         (lambda : distributionName + 'HeadQuarters', ()),
         COLOR_RED)
    if sceneType in (taleConst.scenesTypes.incursionStaging, taleConst.scenesTypes.incursionLightInfestation):
        return (0.75,
         4,
         (lambda : distributionName + 'Staging', ()),
         COLOR_WHITE)
    if sceneType in (taleConst.scenesTypes.incursionMediumInfestation, taleConst.scenesTypes.incursionHeavyInfestation):
        return (0.5,
         5,
         (lambda : distributionName + 'Incursion Spread', ()),
         COLOR_GRAY)
    if sceneType == taleConst.scenesTypes.incursionFinalEncounter:
        return (0.5,
         6,
         (lambda : distributionName + 'Incursion Final Encounter', ()),
         COLOR_PURPLE)


def ColorStarsByJobs24Hours(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryJobsOverLast24Hours(activityID)
    if systemRows:

        def hintFunc(amount, solarSystemID):
            return GetByLabel('UI/Map/StarModeHandler/jobsStartedLast24Hours', noOfJobs=amount)

        jobsBySystem = {row.solarSystemID:row.noOfJobs for row in systemRows}
        _PrepareStandardColorData(colorInfo, jobsBySystem, hintFunc=hintFunc)


def ColorStarsByIndustryCostModifier(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryCostModifier(activityID)

    def hintFunc(value, solarSystemID):
        return GetByLabel('UI/Map/StarModeHandler/industryCostModifier', index=value * 100.0)

    _PrepareStandardColorData(colorInfo, systemRows, hintFunc=hintFunc, fixedSize=STAR_SIZE_FACTOR_STANDARD)


def _GetMilitiaHeader(colorMode):
    factionID = colorMode[1]
    if factionID == mapcommon.STARMODE_FILTER_FACWAR_ENEMY:
        return GetByLabel('UI/Map/MapPallet/cbModeMilitias')
    return cfg.eveowners.Get(factionID).name


def _GetPlanetsHeader(colorMode):
    planetTypeID = colorMode[1]
    return evetypes.GetName(planetTypeID)


filterDataByID = {mapcommon.STARMODE_ASSETS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyAssets'), loadFunction=ColorStarsByAssets),
 mapcommon.STARMODE_VISITED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIVisited'), loadFunction=ColorStarsByVisited),
 mapcommon.STARMODE_SECURITY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsSecurity'), loadFunction=ColorStarsBySecurity),
 mapcommon.STARMODE_INDEX_STRATEGIC: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxStrategic'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexSovereignty, GetByLabel('UI/Map/StarMap/Strategic'))),
 mapcommon.STARMODE_INDEX_MILITARY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxMilitary'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexMilitary, GetByLabel('UI/Map/StarMap/Military'))),
 mapcommon.STARMODE_INDEX_INDUSTRY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxIndustry'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexIndustrial, GetByLabel('UI/Map/StarMap/Industry'))),
 mapcommon.STARMODE_SOV_CHANGE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByRecientSovChanges'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_ALL,)),
 mapcommon.STARMODE_SOV_GAIN: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsBySovGain'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_SOV_GAIN,)),
 mapcommon.STARMODE_SOV_LOSS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsBySovLoss'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_SOV_LOST,)),
 mapcommon.STARMODE_SOV_STANDINGS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByStandings'), loadFunction=ColorStarsByFactionStandings),
 mapcommon.STARMODE_FACTION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbModeFactions'), loadFunction=ColorStarsByFactionSearch, searchHandler=ColorModeInfoSearch_Faction),
 mapcommon.STARMODE_FACTIONEMPIRE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByEmpireFactions'), loadFunction=ColorStarsByFaction),
 mapcommon.STARMODE_MILITIA: Bunch(header=_GetMilitiaHeader, loadFunction=ColorStarsByMilitia),
 mapcommon.STARMODE_REGION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRegion'), loadFunction=ColorStarsByRegion),
 mapcommon.STARMODE_CARGOILLEGALITY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCargoLeagal'), loadFunction=ColorStarsByCargoIllegality),
 mapcommon.STARMODE_PLAYERCOUNT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPilots30Min'), loadFunction=ColorStarsByNumPilots),
 mapcommon.STARMODE_PLAYERDOCKED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPilotsDocked'), loadFunction=ColorStarsByNumPilots),
 mapcommon.STARMODE_STATIONCOUNT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsStationCount'), loadFunction=ColorStarsByStationCount),
 mapcommon.STARMODE_DUNGEONS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDedDeadspace'), loadFunction=ColorStarsByDungeons),
 mapcommon.STARMODE_DUNGEONSAGENTS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDedAgents'), loadFunction=ColorStarsByDungeons),
 mapcommon.STARMODE_JUMPS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsJumps'), loadFunction=ColorStarsByJumps1Hour),
 mapcommon.STARMODE_SHIPKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDestroyed'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatKills, 1)),
 mapcommon.STARMODE_SHIPKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDestroyed24H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatKills, 24)),
 mapcommon.STARMODE_MILITIAKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed1H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatFacWarKills, 1)),
 mapcommon.STARMODE_MILITIAKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed24H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatFacWarKills, 24)),
 mapcommon.STARMODE_PODKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPoded1H'), loadFunction=ColorStarsByPodKills),
 mapcommon.STARMODE_PODKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPoded24H'), loadFunction=ColorStarsByPodKills),
 mapcommon.STARMODE_FACTIONKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsNPCDestroyed'), loadFunction=ColorStarsByFactionKills),
 mapcommon.STARMODE_CYNOSURALFIELDS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCynosuarl'), loadFunction=ColorStarsByCynosuralFields),
 mapcommon.STARMODE_CORPOFFICES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpOffices'), loadFunction=ColorStarsByCorpAssets, loadArguments=('offices', GetByLabel('UI/Map/StarMap/Offices'))),
 mapcommon.STARMODE_CORPIMPOUNDED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpImpounded'), loadFunction=ColorStarsByCorpAssets, loadArguments=('impounded', GetByLabel('UI/Map/StarMap/Impounded'))),
 mapcommon.STARMODE_CORPPROPERTY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpProperty'), loadFunction=ColorStarsByCorpAssets, loadArguments=('property', GetByLabel('UI/Map/StarMap/Property'))),
 mapcommon.STARMODE_CORPDELIVERIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpDeliveries'), loadFunction=ColorStarsByCorpAssets, loadArguments=('deliveries', GetByLabel('UI/Map/StarMap/Deliveries'))),
 mapcommon.STARMODE_CORPWRAPS: Bunch(header=GetByLabel('UI/Corporations/Assets/AssetSafety'), loadFunction=ColorStarsByCorpAssets, loadArguments=('assetwraps', GetByLabel('UI/Corporations/Assets/AssetSafety'))),
 mapcommon.STARMODE_FRIENDS_FLEET: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFleetMembers'), loadFunction=ColorStarsByFleetMembers),
 mapcommon.STARMODE_FRIENDS_CORP: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpMembers'), loadFunction=ColorStarsByCorpMembers),
 mapcommon.STARMODE_FRIENDS_AGENT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyAgents'), loadFunction=ColorStarsByMyAgents),
 mapcommon.STARMODE_JUMP_CLONES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyJumpClones'), loadFunction=ColorStarsByJumpClones),
 mapcommon.STARMODE_AVOIDANCE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsAdvoidance'), loadFunction=ColorStarsByAvoidedSystems),
 mapcommon.STARMODE_REAL: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsActual'), loadFunction=ColorStarsByRealSunColor),
 mapcommon.STARMODE_STATION_SERVICE_CLONING: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsClone'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceCloning,)),
 mapcommon.STARMODE_STATION_SERVICE_FACTORY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFactory'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceFactory,)),
 mapcommon.STARMODE_STATION_SERVICE_FITTING: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFitting'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceFitting,)),
 mapcommon.STARMODE_STATION_SERVICE_INSURANCE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsInsurance'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceInsurance,)),
 mapcommon.STARMODE_STATION_SERVICE_LABORATORY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsLaboratory'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceLaboratory,)),
 mapcommon.STARMODE_STATION_SERVICE_REPAIRFACILITIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRepair'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceRepairFacilities,)),
 mapcommon.STARMODE_STATION_SERVICE_NAVYOFFICES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitia'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceNavyOffices,)),
 mapcommon.STARMODE_STATION_SERVICE_REPROCESSINGPLANT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRefinery'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceReprocessingPlant,)),
 mapcommon.STARMODE_STATION_SERVICE_SECURITYOFFICE: Bunch(header=GetByLabel('UI/Map/MapPallet/StarmodeSecurityOffices'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceSecurityOffice,)),
 mapcommon.STARMODE_PISCANRANGE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPIScanRange'), loadFunction=ColorStarsByPIScanRange),
 mapcommon.STARMODE_MYCOLONIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyColonies'), loadFunction=ColorStarsByMyColonies),
 mapcommon.STARMODE_PLANETTYPE: Bunch(header=_GetPlanetsHeader, loadFunction=ColorStarsByPlanetType),
 mapcommon.STARMODE_INCURSION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIncursion'), loadFunction=ColorStarsByIncursions),
 mapcommon.STARMODE_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(None,)),
 mapcommon.STARMODE_MANUFACTURING_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.MANUFACTURING,)),
 mapcommon.STARMODE_RESEARCHTIME_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.RESEARCH_TIME,)),
 mapcommon.STARMODE_RESEARCHMATERIAL_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.RESEARCH_MATERIAL,)),
 mapcommon.STARMODE_COPY_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByCopyJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.COPYING,)),
 mapcommon.STARMODE_INVENTION_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByInventionJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.INVENTION,)),
 mapcommon.STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.MANUFACTURING,)),
 mapcommon.STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.RESEARCH_TIME,)),
 mapcommon.STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.RESEARCH_MATERIAL,)),
 mapcommon.STARMODE_INDUSTRY_COPY_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByCopyIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.COPYING,)),
 mapcommon.STARMODE_INDUSTRY_INVENTION_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByInventionIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.INVENTION,)),
 mapcommon.STARMODE_INDUSTRY_REACTION_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByReactionIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.REACTION,)),
 mapcommon.STARMODE_INCURSIONGM: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIncursionGM'), loadFunction=ColorStarsByIncursionsGM),
 mapcommon.STARMODE_SETTLED_SYSTEMS_BY_CORP: Bunch(header=GetByLabel('UI/InfoWindow/SettledSystems'), loadFunction=ColorStarsByCorporationSettledSystems),
 mapcommon.STARMODE_ROAMING_WEATHER: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRoamingWeather'), loadFunction=ColorStarsByRoamingWeather),
 mapcommon.STARMODE_DYNAMIC_BOUNTY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbDynamicBounty'), loadFunction=ColorStarsByDynamicBountyOutput),
 mapcommon.STARMODE_SYSTEM_INTERFERENCE: Bunch(header=GetByLabel('UI/Map/MapPallet/SolarSystemInterference'), loadFunction=ColorStarsBySolarSystemInterference),
 mapcommon.STARMODE_INSURGENCY: Bunch(header=GetByLabel('UI/PirateInsurgencies/dashboardCaption'), loadFunction=ColorStarsByInsurgencyInvolvement),
 mapcommon.STARMODE_INSURGENCY_CORRUPTION: Bunch(header='Corruption', loadFunction=ColorStarsByCorruptionValue),
 mapcommon.STARMODE_INSURGENCY_SUPPRESSION: Bunch(header='Suppression', loadFunction=ColorStarsBySuppressionValue)}

def GetMapFilterData(colorMode):
    filterData = filterDataByID.get(colorMode, None)
    return filterData


def GetFormatFunctionLabel(colorMode):
    colorModeKey = _GetColorModeKey(colorMode)
    filterCls = filtersByID.GetFilterByID(colorModeKey)
    if filterCls:
        return filterCls.GetName()
    colorModeMapping = GetMapFilterData(colorModeKey)
    if colorModeMapping is None:
        return
    if callable(colorModeMapping.header):
        label = colorModeMapping.header(colorMode)
    else:
        label = colorModeMapping.header
    return label


def _GetColorModeKey(colorMode):
    if isinstance(colorMode, tuple):
        colorModeKey = colorMode[0]
    else:
        colorModeKey = colorMode
    return colorModeKey


def GetColorModeHint(colorMode):
    colorModeKey = _GetColorModeKey(colorMode)
    filterCls = filtersByID.GetFilterByID(colorModeKey)
    if filterCls:
        return filterCls.GetHint()


def _PrepareStandardColorData(colorInfo, dataPerSolarSystem, hintFunc = None, hintArgs = None, amountKey = None, colorList = None, fixedSize = None):
    dataWithAmount = {}
    allAmounts = []
    if amountKey:
        for solarSystemID, solarSystemData in dataPerSolarSystem.iteritems():
            if isinstance(solarSystemData, list):
                amount = sum((getattr(data, amountKey, 0) for data in solarSystemData))
            else:
                amount = getattr(solarSystemData, amountKey, 0)
            dataWithAmount[solarSystemID] = (amount, solarSystemData)
            allAmounts.append(amount)

    else:
        for solarSystemID, solarSystemData in dataPerSolarSystem.iteritems():
            if hasattr(solarSystemData, '__iter__'):
                amount = len(solarSystemData)
            else:
                amount = solarSystemData
            dataWithAmount[solarSystemID] = (amount, solarSystemData)
            allAmounts.append(amount)

    if not allAmounts:
        return
    maxAmount = max(allAmounts)
    minAmount = min(allAmounts)
    numValues = len(allAmounts)
    for solarSystemID, (amount, solarSystemData) in dataWithAmount.iteritems():
        sizeFactor = fixedSize or GetStarSizeByDataValue(amount, maxAmount, minAmount, numValues)
        colorValue = amount / float(maxAmount)
        hintFuncArgs = (solarSystemData, solarSystemID)
        if hintArgs:
            hintFuncArgs += hintArgs
        colorInfo.solarSystemDict[solarSystemID] = (sizeFactor,
         colorValue,
         (hintFunc, hintFuncArgs),
         None)

    colorInfo.maxAmount = maxAmount
    colorInfo.minAmount = minAmount
    colorInfo.colorList = colorList or INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA
