#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\maputils.py
import types
from carbon.common.script.sys.serviceConst import ROLE_GML
from collections import defaultdict
import evetypes
import trinity
import localization
import utillib
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.maps import mapcommon
from eve.client.script.ui.shared.planet.planetConst import PLANET_TYPES
from eve.common.lib import appConst as const
from eve.common.script.util.facwarCommon import GetOccupierFWFactions
from security.client.securityColor import get_security_status_color

def GetValidSolarsystemGroups():
    return [const.groupSun,
     const.groupScannerProbe,
     const.groupPlanet,
     const.groupMoon,
     const.groupStation,
     const.groupAsteroidBelt,
     const.groupBeacon,
     const.groupCynosuralBeacon,
     const.groupSatellite,
     const.groupStargate,
     const.groupSovereigntyClaimMarkers,
     const.groupSovereigntyDisruptionStructures,
     'bookmark',
     'scanresult']


def GetVisibleSolarsystemBrackets():
    return settings.user.ui.Get('groupsInSolarsystemMap', GetValidSolarsystemGroups())


def GetHintsOnSolarsystemBrackets():
    return settings.user.ui.Get('hintsInSolarsystemMap', [const.groupStation])


def GetMyPos():
    bp = sm.GetService('michelle').GetBallpark()
    if bp and bp.ego:
        ego = bp.balls[bp.ego]
        myPos = trinity.TriVector(ego.x, ego.y, ego.z)
    elif eve.session.stationid:
        s = sm.GetService('ui').GetStationStaticInfo(eve.session.stationid)
        myPos = trinity.TriVector(s.x, s.y, s.z)
    else:
        myPos = trinity.TriVector()
    return myPos


def GetDistance(slimItem = None, mapData = None, ball = None, transform = None):
    if ball:
        return ball.surfaceDist
    if slimItem:
        ballPark = sm.GetService('michelle').GetBallpark()
        if ballPark and slimItem.itemID in ballPark.balls:
            return ballPark.balls[slimItem.itemID].surfaceDist
    myPos = GetMyPos()
    if mapData:
        pos = trinity.TriVector(mapData.x, mapData.y, mapData.z)
    elif transform:
        pos = transform.translation
        if type(pos) == types.TupleType:
            pos = trinity.TriVector(*pos)
    else:
        return None
    return (pos - myPos).Length()


def GetNameFromMapCache(messageID, messageType = None):
    return localization.GetByMessageID(messageID)


def GetServicesOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsClone'), mapcommon.STARMODE_SERVICE_Cloning],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsFactory'), mapcommon.STARMODE_SERVICE_Factory],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsFitting'), mapcommon.STARMODE_SERVICE_Fitting],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsInsurance'), mapcommon.STARMODE_SERVICE_Insurance],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsLaboratory'), mapcommon.STARMODE_SERVICE_Laboratory],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsRepair'), mapcommon.STARMODE_SERVICE_RepairFacilities],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitia'), mapcommon.STARMODE_SERVICE_NavyOffices],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsRefinery'), mapcommon.STARMODE_SERVICE_ReprocessingPlant],
     [localization.GetByLabel('UI/Map/MapPallet/StarmodeSecurityOffices'), mapcommon.STARMODE_SERVICE_SecurityOffice]]
    ret.sort()
    return ret


def GetPersonalOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsMyBookmarks'), mapcommon.STARMODE_BOOKMARKED],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsMyAssets'), mapcommon.STARMODE_ASSETS],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsIVisited'), mapcommon.STARMODE_VISITED],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsCargoLeagal'), mapcommon.STARMODE_CARGOILLEGALITY],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsPIScanRange'), mapcommon.STARMODE_PISCANRANGE]]
    if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & eve.session.corprole != 0:
        ret += [[localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpOffices'), mapcommon.STARMODE_CORPOFFICES],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpImpounded'), mapcommon.STARMODE_CORPIMPOUNDED],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpProperty'), mapcommon.STARMODE_CORPPROPERTY],
         [localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpDeliveries'), mapcommon.STARMODE_CORPDELIVERIES],
         [localization.GetByLabel('UI/Corporations/Assets/AssetSafety'), mapcommon.STARMODE_CORPWRAPS]]
    ret += [[localization.GetByLabel('UI/Map/MapPallet/cbStarsCorpMembers'), mapcommon.STARMODE_FRIENDS_CORP],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsFleetMembers'), mapcommon.STARMODE_FRIENDS_FLEET],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsMyAgents'), mapcommon.STARMODE_FRIENDS_AGENT],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsMyJumpClones'), mapcommon.STARMODE_JUMP_CLONES]]
    ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsMyColonies'), mapcommon.STARMODE_MYCOLONIES])
    ret.sort()
    return ret


def GetSovereignty_FactionalWarfareOptions():
    warfactionlist = []
    for factionID in GetOccupierFWFactions():
        factionName = cfg.eveowners.Get(factionID).name
        warfactionlist.append([factionName.lower(), factionName, factionID])

    warfactionlist.sort()
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbModeMilitias'), (mapcommon.STARMODE_MILITIA, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)]]
    for fNL, factionName, factionID in warfactionlist:
        ret.append([factionName, (mapcommon.STARMODE_MILITIA, factionID)])

    ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed1H'), mapcommon.STARMODE_MILITIAKILLS1HR])
    ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed24H'), mapcommon.STARMODE_MILITIAKILLS24HR])
    return ret


def GetSovereignty_InsurgencyOptions():
    ret = []
    ret.append([localization.GetByLabel('UI/PirateInsurgencies/dashboardCaption'), mapcommon.STARMODE_INSURGENCY])
    ret.append([localization.GetByLabel('UI/PirateInsurgencies/corruption'), mapcommon.STARMODE_INSURGENCY_CORRUPTION])
    ret.append([localization.GetByLabel('UI/PirateInsurgencies/suppression'), mapcommon.STARMODE_INSURGENCY_SUPPRESSION])
    return ret


def GetSovereignty_SovereigntyOptions():
    factionlist = []
    factionIDs = sm.GetService('starmap').GetAllFactionsAndAlliances()
    cfg.eveowners.Prime(factionIDs)
    for factionID in factionIDs:
        factionName = cfg.eveowners.Get(factionID).name
        factionlist.append([factionName.lower(), factionName, factionID])

    factionlist.sort()
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbModeFactions'), (mapcommon.STARMODE_FACTION, mapcommon.STARMODE_FILTER_FACWAR_ENEMY)], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByStandings'), mapcommon.STARMODE_SOV_STANDINGS], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByEmpireFactions'), (mapcommon.STARMODE_FACTIONEMPIRE, mapcommon.STARMODE_FILTER_EMPIRE)]]
    for fNL, factionName, factionID in factionlist:
        ret.append([factionName, (mapcommon.STARMODE_FACTION, factionID)])

    return ret


def GetSovereignty_ChangesOptions():
    ret = [(localization.GetByLabel('UI/Map/MapPallet/cbStarsByRecientSovChanges'), mapcommon.STARMODE_SOV_CHANGE), (localization.GetByLabel('UI/Map/MapPallet/cbStarsBySovGain'), mapcommon.STARMODE_SOV_GAIN), (localization.GetByLabel('UI/Map/MapPallet/cbStarsBySovLoss'), mapcommon.STARMODE_SOV_LOSS)]
    return ret


def GetAutopilotOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsAdvoidance'), mapcommon.STARMODE_AVOIDANCE]]
    return ret


def GetStatisticsOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsPilots30Min'), mapcommon.STARMODE_PLAYERCOUNT],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsPilotsDocked'), mapcommon.STARMODE_PLAYERDOCKED],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsJumps'), mapcommon.STARMODE_JUMPS1HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsDestroyed'), mapcommon.STARMODE_SHIPKILLS1HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsDestroyed24H'), mapcommon.STARMODE_SHIPKILLS24HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsPoded1H'), mapcommon.STARMODE_PODKILLS1HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsPoded24H'), mapcommon.STARMODE_PODKILLS24HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsNPCDestroyed'), mapcommon.STARMODE_FACTIONKILLS1HR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsStationCount'), mapcommon.STARMODE_STATIONCOUNT],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsCynosuarl'), mapcommon.STARMODE_CYNOSURALFIELDS],
     [localization.GetByLabel('UI/Map/MapPallet/SolarSystemInterference'), mapcommon.STARMODE_SYSTEM_INTERFERENCE]]
    ret.sort()
    return ret


def GetSovereignty_Development_IndicesOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxStrategic'), mapcommon.STARMODE_INDEX_STRATEGIC], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxMilitary'), mapcommon.STARMODE_INDEX_MILITARY], [localization.GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxIndustry'), mapcommon.STARMODE_INDEX_INDUSTRY]]
    return ret


def GetPlanetsOptions():
    ret = []
    for planetTypeID in PLANET_TYPES:
        ret.append((evetypes.GetName(planetTypeID), (mapcommon.STARMODE_PLANETTYPE, planetTypeID)))

    ret.sort()
    return ret


def GetIndustry_JobsOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsByJobsStartedLast24Hours'), mapcommon.STARMODE_JOBS24HOUR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingJobsStartedLast24Hours'), mapcommon.STARMODE_MANUFACTURING_JOBS24HOUR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeJobsStartedLast24Hours'), mapcommon.STARMODE_RESEARCHTIME_JOBS24HOUR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialJobsStartedLast24Hours'), mapcommon.STARMODE_RESEARCHMATERIAL_JOBS24HOUR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByCopyJobsStartedLast24Hours'), mapcommon.STARMODE_COPY_JOBS24HOUR],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByInventionJobsStartedLast24Hours'), mapcommon.STARMODE_INVENTION_JOBS24HOUR]]
    return ret


def GetIndustry_CostModifierOptions():
    return [[localization.GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingIndustryCostModifier'), mapcommon.STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeIndustryCostModifier'), mapcommon.STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialIndustryCostModifier'), mapcommon.STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByCopyIndustryCostModifier'), mapcommon.STARMODE_INDUSTRY_COPY_COST_INDEX],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsByInventionIndustryCostModifier'), mapcommon.STARMODE_INDUSTRY_INVENTION_COST_INDEX]]


def GetActiveStarColorModeLabel():
    activeMode = settings.user.ui.Get('starscolorby', mapcommon.STARMODE_SECURITY)
    groupFunctions = [GetRootOptions,
     GetAutopilotOptions,
     GetPersonalOptions,
     GetPlanetsOptions,
     GetServicesOptions,
     GetSovereignty_Development_IndicesOptions,
     GetSovereignty_FactionalWarfareOptions,
     GetSovereignty_InsurgencyOptions,
     GetSovereignty_ChangesOptions,
     GetStatisticsOptions,
     GetSovereignty_SovereigntyOptions,
     GetIndustry_JobsOptions,
     GetIndustry_CostModifierOptions]
    for function in groupFunctions:
        for label, starModeConst in function():
            if starModeConst == activeMode:
                return label


def GetRootOptions():
    ret = [[localization.GetByLabel('UI/Map/MapPallet/cbStarsActual'), mapcommon.STARMODE_REAL],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsSecurity'), mapcommon.STARMODE_SECURITY],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsRegion'), mapcommon.STARMODE_REGION],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsDedDeadspace'), mapcommon.STARMODE_DUNGEONS],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsDedAgents'), mapcommon.STARMODE_DUNGEONSAGENTS],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsIncursion'), mapcommon.STARMODE_INCURSION],
     [localization.GetByLabel('UI/Map/MapPallet/cbStarsRoamingWeather'), mapcommon.STARMODE_ROAMING_WEATHER]]
    if eve.session.role & ROLE_GML:
        ret.append([localization.GetByLabel('UI/Map/MapPallet/cbStarsIncursionGM'), mapcommon.STARMODE_INCURSIONGM])
    ret.sort()
    return ret


def GetSolarSystemOptions():
    from eve.client.script.ui.shared.maps.entries import BracketSelectorEntry
    validGroups = GetValidSolarsystemGroups()
    wantedGroups = GetVisibleSolarsystemBrackets()
    wantedHints = GetHintsOnSolarsystemBrackets()
    scrolllist = []
    for groupID in validGroups:
        data = utillib.KeyVal()
        data.visible = groupID in wantedGroups
        data.showhint = groupID in wantedHints
        data.groupID = groupID
        if type(groupID) in types.StringTypes:
            cerbString = {'bookmark': 'UI/Map/MapPallet/cbSolarSystem_bookmark',
             'scanresult': 'UI/Map/MapPallet/cbSolarSystem_scanresult'}[groupID]
            data.label = localization.GetByLabel(cerbString)
        else:
            data.label = evetypes.GetGroupNameByGroup(groupID)
        scrolllist.append((data.label, GetFromClass(BracketSelectorEntry, data)))

    if scrolllist:
        scrolllist = SortListOfTuples(scrolllist)
    return scrolllist


def GetRoundedSecurityStatus(security):
    sec = round(security, 1)
    if sec == -0.0:
        sec = 0.0
    return sec


def GetColorBySecurityStatus(sec):
    return get_security_status_color(sec)


def GetSecurityStatusText(security):
    security = GetRoundedSecurityStatus(security)
    color = GetColorBySecurityStatus(security)
    return '<color=%s>%s</color>' % (Color.RGBtoHex(*color), security)


def GetJumpClonesBySystemID():
    from eve.client.script.ui.shared.neocom.charsheet.jumpClonesPanel import JumpClone
    bySystemID = defaultdict(list)
    stuffToPrime = set()
    allClonesInDockableLocations = []
    for eachCloneInfo in sm.GetService('clonejump').GetClones():
        clone = JumpClone(clone_id=eachCloneInfo.jumpCloneID, location_id=eachCloneInfo.locationID, name=eachCloneInfo.cloneName, implants=[])
        if clone.in_station or clone.in_structure:
            allClonesInDockableLocations.append(clone)

    if stuffToPrime:
        cfg.evelocations.Prime(stuffToPrime)
    for eachClone in allClonesInDockableLocations:
        solarSystemID = None
        if eachClone.in_station:
            solarSystemID = cfg.stations.Get(eachClone.location_id).solarSystemID
        else:
            structure = sm.GetService('structureDirectory').GetStructureInfo(eachClone.location_id)
            if structure is not None:
                solarSystemID = structure.solarSystemID
        if solarSystemID:
            bySystemID[solarSystemID].append(eachClone)

    return bySystemID
