#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\mapSvc.py
import evetypes
import eveuniverse.security
import fsd.schemas.binaryLoader as fsdBinaryLoader
import itertoolsext
import telemetry
import trinity
import uthread
import utillib
from caching.memoize import Memoize
from carbon.common.script.sys import service
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.util.color import Color
from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
from eve.client.script.ui.shared.maps.mapcommon import LINESET_EFFECT
from eve.client.script.ui.shared.maps.palette import MapPalette
from eve.client.script.ui.util import searchUtil
from eve.common.lib import appConst as const
from eve.common.script.search.const import ResultType
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem, IsKnownSpaceRegion, IsKnownSpaceConstellation
from eve.common.script.util import eveFormat

class MapSvc(service.Service):
    __guid__ = 'svc.map'
    __servicename__ = 'map'
    __displayname__ = 'Map Client Service'
    __update_on_reload__ = 0
    __startupdependencies__ = ['settings']
    __dependencies__ = ['securitySvc']
    __notifyevents__ = ['OnSessionReset']

    def Run(self, memStream = None):
        self.state = service.SERVICE_START_PENDING
        self.LogInfo('Starting Map Client Svc')
        self.Reset()
        self.state = service.SERVICE_RUNNING

    def Stop(self, memStream = None):
        if trinity.device is None:
            return
        self.LogInfo('Map svc')
        self.Reset()

    def Reset(self):
        self.LogInfo('MapSvc Reset')
        self.securityInfo = None
        self.minimizedWindows = []
        self.activeMap = ''
        self.mapconnectionscache = None
        self.landmarks = None
        sm.ScatterEvent('OnMapReset')

    def OnSessionReset(self):
        self.GetJumpBridgesWithMyAccess.clear_memoized()

    def Open(self):
        viewSvc = sm.GetService('viewState')
        if not viewSvc.IsViewActive('starmap', 'systemmap'):
            activeMap = settings.user.ui.Get('activeMap', 'starmap')
            viewSvc.ActivateView(activeMap)

    def GetActiveMapName(self):
        return settings.user.ui.Get('activeMap', 'starmap')

    def MinimizeWindows(self):
        lobby = LobbyWnd.GetIfOpen()
        if lobby and not lobby.destroyed and lobby.state != uiconst.UI_HIDDEN and not lobby.IsMinimized() and not lobby.IsCollapsed():
            lobby.Minimize()
            self.minimizedWindows.append(LobbyWnd.default_windowID)

    def ResetMinimizedWindows(self):
        if len(self.minimizedWindows) > 0:
            windowSvc = sm.GetService('window')
            for windowID in self.minimizedWindows:
                wnd = Window.GetIfOpen(windowID=windowID)
                if wnd and wnd.IsMinimized():
                    wnd.Maximize()

            self.minimizedWindows = []

    def Toggle(self, *args):
        viewSvc = sm.GetService('viewState').ToggleSecondaryView(self.GetActiveMapName())

    def ToggleMode(self, *args):
        viewSvc = sm.GetService('viewState')
        if viewSvc.IsViewActive('starmap'):
            viewSvc.ActivateView('systemmap')
        elif viewSvc.IsViewActive('systemmap'):
            viewSvc.ActivateView('starmap')

    def OpenMapsPalette(self):
        openMinimized = settings.user.ui.Get('MapWindowMinimized', False)
        MapPalette.Open(openMinimized=openMinimized)

    def CloseMapsPalette(self):
        MapPalette.CloseIfOpen()

    def GetSecurityStatus(self, solarSystemID, getColor = False):
        securityValue = self.GetSystemSecurityValue(solarSystemID)
        return eveFormat.FmtSystemSecStatus(securityValue, getColor)

    def GetSystemSecurityValue(self, solarSystemID):
        if self.securityInfo is None:
            uthread.Lock(self)
            try:
                self.securityInfo = {}
                for systemID, each in cfg.mapSystemCache.iteritems():
                    self.securityInfo[systemID] = each.pseudoSecurity

            finally:
                uthread.UnLock(self)

        securityValue = self.securityInfo.get(solarSystemID, 0.0)
        return securityValue

    def GetSecurityClass(self, solarSystemID):
        secLevel = self.GetSecurityStatus(solarSystemID)
        return eveuniverse.security.SecurityClassFromLevel(secLevel)

    @telemetry.ZONE_METHOD
    def GetSolarsystemItems(self, solarsystemID, requireLocalizedTexts = True, doYields = False):
        local, structures = uthread.parallel([(cfg.GetLocationsLocalBySystem, (solarsystemID, requireLocalizedTexts, doYields)), (sm.GetService('structureDirectory').GetStructureMapData, (solarsystemID,))], contextSuffix='GetSolarsystemItems')
        for structure in structures:
            local.InsertNew(structure)

        return local

    def GetPlanetMoonsInPlayerSystem(self, planetID):
        if cfg.evelocations.Get(planetID).solarSystemID == session.solarsystemid2:
            return self._GetMoons(planetID)

    @Memoize
    def _GetMoons(self, planetID):
        return [ i for i in self.GetSolarsystemItems(cfg.evelocations.Get(planetID).solarSystemID) if i.groupID == const.groupMoon and i.orbitID == planetID ]

    @Memoize
    def GetStarGateIDsInSolarSystem(self, solar_system_id):
        return [ i.itemID for i in self.GetSolarsystemItems(solar_system_id, requireLocalizedTexts=False) if i.groupID == const.groupStargate ]

    def ForEachStarGateIDInSolarSystem(self, solar_system_id, callback):
        systemInfo = cfg.mapSolarSystemContentCache.get(solar_system_id, None)
        if not systemInfo:
            return
        for gateID in systemInfo.stargates.iterkeys():
            callback(gateID)

    def GetMapConnectionCache(self):
        if self.mapconnectionscache is None:
            self.mapconnectionscache = settings.user.ui.Get('map_cacheconnectionsfile', {})
        return self.mapconnectionscache or {}

    def GetItem(self, itemID, retall = False, categoryID = None):
        if idCheckers.IsStation(itemID):
            station = sm.GetService('ui').GetStationStaticInfo(itemID)
            return utillib.KeyVal(itemID=itemID, locationID=station.solarSystemID, itemName=cfg.evelocations.Get(itemID).name, typeID=station.stationTypeID, groupID=const.groupStation, x=station.x, y=station.y, z=station.z)
        elif idCheckers.IsSolarSystem(itemID):
            solarSystem = cfg.mapSystemCache.Get(itemID)
            return utillib.KeyVal(itemID=itemID, locationID=solarSystem.constellationID, itemName=cfg.evelocations.Get(itemID).name, typeID=const.typeSolarSystem, groupID=const.groupSolarSystem, factionID=getattr(solarSystem, 'factionID', None), neighbours=[ i.solarSystemID for i in solarSystem.neighbours ], x=solarSystem.center.x, y=solarSystem.center.y, z=solarSystem.center.z, security=solarSystem.securityStatus)
        elif idCheckers.IsConstellation(itemID):
            constellation = cfg.mapConstellationCache.Get(itemID)
            return utillib.KeyVal(itemID=itemID, locationID=constellation.regionID, itemName=cfg.evelocations.Get(itemID).name, typeID=const.typeConstellation, neighbours=list(constellation.neighbours), groupID=const.groupConstellation, x=constellation.center.x, y=constellation.center.y, z=constellation.center.z)
        elif idCheckers.IsRegion(itemID):
            region = cfg.mapRegionCache.Get(itemID)
            return utillib.KeyVal(itemID=itemID, locationID=const.locationUniverse, itemName=cfg.evelocations.Get(itemID).name, neighbours=list(region.neighbours), typeID=const.typeRegion, groupID=const.groupRegion, x=region.center.x, y=region.center.y, z=region.center.z)
        elif idCheckers.IsCelestial(itemID):
            solarSystemID = cfg.mapCelestialLocationCache[itemID]
            typeID, pos = self._GetCelestialsTypeIdAndPosition(itemID, solarSystemID)
            return utillib.KeyVal(itemID=itemID, locationID=solarSystemID, itemName=cfg.evelocations.Get(itemID).name, typeID=typeID, x=pos[0], y=pos[1], z=pos[2])
        elif categoryID and categoryID != const.categoryStructure:
            return
        elif not cfg.evelocations.GetIfExists(itemID):
            return
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(itemID)
            if structureInfo is None:
                return
            locationInfo = cfg.evelocations.Get(itemID)
            return utillib.KeyVal(itemID=itemID, locationID=locationInfo.solarSystemID, itemName=structureInfo.itemName, typeID=structureInfo.typeID, groupID=evetypes.GetGroupID(structureInfo.typeID), x=locationInfo.x, y=locationInfo.y, z=locationInfo.z)

    def _GetCelestialsTypeIdAndPosition(self, itemID, solarSystemID):
        if itemID in cfg.mapSolarSystemContentCache.celestials:
            celestial = cfg.mapSolarSystemContentCache.celestials[itemID]
            return (celestial.typeID, celestial.position)
        solarSystem = cfg.mapSolarSystemContentCache[solarSystemID]
        if itemID == solarSystem.star.id:
            return (solarSystem.star.typeID, (0.0, 0.0, 0.0))
        raise KeyError('Celestial with id %s not found' % itemID)

    @telemetry.ZONE_METHOD
    def GetParentLocationID(self, locationID):
        if idCheckers.IsSolarSystem(locationID):
            solarSystem = cfg.mapSystemCache.Get(locationID)
            return (const.locationUniverse,
             solarSystem.regionID,
             solarSystem.constellationID,
             locationID,
             None)
        if idCheckers.IsConstellation(locationID):
            constellation = cfg.mapConstellationCache.Get(locationID)
            return (const.locationUniverse,
             constellation.regionID,
             locationID,
             None,
             None)
        if idCheckers.IsRegion(locationID):
            return (const.locationUniverse,
             locationID,
             None,
             None,
             None)
        if idCheckers.IsCelestial(locationID):
            solarSystemID = cfg.mapCelestialLocationCache[locationID]
            solarSystem = cfg.mapSystemCache.Get(solarSystemID)
            return (const.locationUniverse,
             solarSystem.regionID,
             solarSystem.constellationID,
             solarSystemID,
             locationID)
        if idCheckers.IsStation(locationID):
            station = cfg.stations.Get(locationID)
            ssID = station.solarSystemID
            solarSystem = cfg.mapSystemCache.Get(ssID)
            return (const.locationUniverse,
             solarSystem.regionID,
             solarSystem.constellationID,
             ssID,
             locationID)
        ssID = cfg.evelocations.Get(locationID).solarSystemID
        if ssID is None:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(locationID)
            if structureInfo is not None:
                ssID = structureInfo.solarSystemID
        if ssID is not None:
            mapData = cfg.mapSystemCache.Get(ssID)
            return (const.locationUniverse,
             mapData.regionID,
             mapData.constellationID,
             ssID,
             locationID)
        return (const.locationUniverse,
         None,
         None,
         None,
         locationID)

    def FindByName(self, searchstr, ignorecommas = 1):
        searchGroupList = [ResultType.constellation, ResultType.solar_system, ResultType.region]
        results = searchUtil.GetResultsList(searchstr, searchGroupList)
        return map(self.GetItem, results)

    def GetLandmarks(self):
        if self.landmarks is None:
            self.landmarks = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/landmarks.static')
        return self.landmarks

    def GetLandmark(self, landmarkID):
        return self.GetLandmarks()[landmarkID]

    def GetNeighbors(self, itemID):
        if not (IsKnownSpaceSystem(itemID) or IsKnownSpaceConstellation(itemID) or IsKnownSpaceRegion(itemID)):
            return []
        if idCheckers.IsSolarSystem(itemID):
            solarSystem = cfg.mapSystemCache.Get(itemID)
            return [ i.solarSystemID for i in solarSystem.neighbours ]
        if idCheckers.IsConstellation(itemID):
            constellation = cfg.mapConstellationCache.Get(itemID)
            return constellation.neighbours
        if idCheckers.IsRegion(itemID):
            region = cfg.mapRegionCache.Get(itemID)
            return region.neighbours
        return []

    def GetParent(self, itemID):
        if idCheckers.IsSolarSystem(itemID):
            solarSystem = cfg.mapSystemCache.Get(itemID)
            return solarSystem.constellationID
        elif idCheckers.IsConstellation(itemID):
            constellation = cfg.mapConstellationCache.Get(itemID)
            return constellation.regionID
        elif idCheckers.IsRegion(itemID):
            return const.locationUniverse
        elif idCheckers.IsCelestial(itemID):
            return cfg.mapCelestialLocationCache[itemID]
        elif idCheckers.IsStation(itemID):
            station = cfg.stations.Get(itemID)
            return station.solarSystemID
        else:
            return None

    def GetRegionForSolarSystem(self, solarSystemID):
        if idCheckers.IsSolarSystem(solarSystemID):
            solarSystem = cfg.mapSystemCache.Get(solarSystemID)
            return solarSystem.regionID
        else:
            return None

    def GetConstellationForSolarSystem(self, solarSystemID):
        if idCheckers.IsSolarSystem(solarSystemID):
            solarSystem = cfg.mapSystemCache.Get(solarSystemID)
            return solarSystem.constellationID
        else:
            return None

    def GetLocationChildren(self, itemID):
        if idCheckers.IsConstellation(itemID):
            return cfg.mapConstellationCache.Get(itemID).solarSystemIDs
        if idCheckers.IsRegion(itemID):
            return cfg.mapRegionCache.Get(itemID).constellationIDs
        raise Exception('Unexpected itemID calling GetLocationChildren?' + str(itemID))

    def ExpandItems(self, itemIDs):
        ret = []
        for i in itemIDs:
            ret.extend(self.GetSolarSystemIDsIn(i))

        return ret

    def GetSolarSystemIDsIn(self, i):
        if idCheckers.IsSolarSystem(i):
            return [i]
        if idCheckers.IsConstellation(i):
            return list(cfg.mapConstellationCache.Get(i).solarSystemIDs)
        if idCheckers.IsRegion(i):
            return list(cfg.mapRegionCache.Get(i).solarSystemIDs)

    def GetKnownspaceRegions(self):
        for regionID in cfg.mapRegionCache.iterkeys():
            if IsKnownSpaceRegion(regionID):
                yield regionID

    def IterateKnownspaceRegions(self):
        for regionID, region in cfg.mapRegionCache.iteritems():
            if IsKnownSpaceRegion(regionID):
                yield (regionID, region)

    def GetSleeperspaceRegions(self):
        for regionID in cfg.mapRegionCache.iterkeys():
            if regionID >= const.mapWormholeRegionMin:
                yield regionID

    def GetNumberOfStargates(self, itemID):
        return len(cfg.mapSolarSystemContentCache[itemID].stargates)

    def IterateSolarSystemIDs(self, itemID = None):
        if itemID is None:
            for regionID in self.GetKnownspaceRegions():
                for s in cfg.mapRegionCache.Get(regionID).solarSystemIDs:
                    yield s

        elif idCheckers.IsSolarSystem(itemID):
            yield itemID
        elif idCheckers.IsConstellation(itemID):
            for systemID in cfg.mapConstellationCache.Get(itemID).solarSystemIDs:
                yield systemID

        elif idCheckers.IsRegion(itemID):
            for systemID in cfg.mapRegionCache.Get(itemID).solarSystemIDs:
                yield systemID

    def IterateKnownSpaceSolarSystems(self):
        for systemID, system in cfg.mapSystemCache.iteritems():
            if IsKnownSpaceSystem(systemID):
                yield (systemID, system)

    def GetInfoOnPilotsBySolarSystemIDs(self):
        sol, sta, statDivisor = sm.ProxySvc('machoNet').GetClusterGameStatisticsForClient('EVE', ({}, {}, 0))
        ret = {}
        for sfoo in sol.iterkeys():
            dockedInStationRawCount = sta.get(sfoo, 0)
            inSystemRawCount = sol.get(sfoo, 0)
            inSpaceRawCount = inSystemRawCount - dockedInStationRawCount
            amountDocked = dockedInStationRawCount / float(statDivisor)
            amountInSpace = inSpaceRawCount / float(statDivisor)
            amountDockedRounded = round(amountDocked)
            amountInSpaceRounded = round(amountInSpace)
            solarSystemID = sfoo + 30000000
            ret[solarSystemID] = itertoolsext.Bundle(amountDocked=amountDockedRounded, amountInSpace=amountInSpaceRounded)

        return ret

    def GetPlanetInfo(self, planetID, hierarchy = False):
        p = cfg.mapSolarSystemContentCache.planets[planetID]
        typeID = p.typeID
        solarSystemID = p.solarSystemID
        info = utillib.KeyVal(solarSystemID=solarSystemID, typeID=typeID)
        if hierarchy:
            u, regionID, constellationID, s, i = self.GetParentLocationID(solarSystemID)
            info.regionID = regionID
            info.constellationID = constellationID
        return info

    def IteratePlanetInfo(self):
        for planetID, planetData in cfg.mapSolarSystemContentCache.planets.iteritems():
            yield self.PlanetInfo(planetID, planetData.solarSystemID, planetData.typeID)

    @Memoize(5)
    def GetJumpBridgesWithMyAccess(self):
        return sm.RemoteSvc('structureDirectory').GetJumpBridgesWithMyAccess()

    def CreateLineSet(self, path = LINESET_EFFECT):
        lineSet = trinity.EveLineSet()
        lineSet.effect = trinity.Tr2Effect()
        lineSet.effect.effectFilePath = path
        lineSet.renderTransparent = False
        return lineSet

    def CreateCurvedLineSet(self, effectPath = None):
        lineSet = trinity.EveCurveLineSet()
        if effectPath is not None:
            lineSet.lineEffect.effectFilePath = effectPath
        texMap = trinity.TriTextureParameter()
        texMap.name = 'TexMap'
        texMap.resourcePath = 'res:/dx9/texture/UI/lineSolid.dds'
        lineSet.lineEffect.resources.append(texMap)
        overlayTexMap = trinity.TriTextureParameter()
        overlayTexMap.name = 'OverlayTexMap'
        overlayTexMap.resourcePath = 'res:/dx9/texture/UI/lineOverlay5.dds'
        lineSet.lineEffect.resources.append(overlayTexMap)
        return lineSet

    class PlanetInfo(object):
        __slots__ = ['planetID', 'solarSystemID', 'typeID']

        def __init__(self, planetID, solarSystemID, typeID):
            self.planetID = planetID
            self.solarSystemID = solarSystemID
            self.typeID = typeID

    def GetSystemColorString(self, solarSystemID):
        col = self.GetSystemColor(solarSystemID)
        return Color.RGBtoHex(col[0], col[1], col[2])

    @Memoize
    def GetEdencomFortressSystems(self):
        return sm.RemoteSvc('map').GetEdencomFortressSystems()

    @Memoize
    def GetEdencomMinorVictorySystems(self):
        return sm.RemoteSvc('map').GetEdencomMinorVictorySystems()

    def GetEdencomAvoidanceSystems(self):
        return self.GetEdencomFortressSystems() + self.GetEdencomMinorVictorySystems()

    @Memoize
    def GetTriglavianMinorVictorySystems(self):
        return sm.RemoteSvc('map').GetTriglavianMinorVictorySystems()

    @Memoize(1)
    def GetAllRoamingWeatherSystems(self):
        return sm.RemoteSvc('map').GetAllRoamingWeatherSystems()

    def GetSystemColor(self, solarSystemID):
        sec, col = eveFormat.FmtSystemSecStatus(self.GetSecurityStatus(solarSystemID), 1)
        return col

    def GetModifiedSystemColor(self, solarSystemID):
        modifiedSecurityLevel = self.securitySvc.get_modified_security_level(solarSystemID)
        sec, col = eveFormat.FmtSystemSecStatus(modifiedSecurityLevel, 1)
        return col

    def GetStation(self, stationID):
        station = sm.RemoteSvc('stationSvc').GetStation(stationID)
        if station and idCheckers.IsLocalIdentity(stationID):
            station.stationName = cfg.evelocations.Get(stationID).name
        return station

    def GetMapDataForStructure(self, solarSystemID, structureID):
        structuresInSystem = sm.GetService('structureDirectory').GetStructureMapData(solarSystemID)
        return itertoolsext.first_or_default(structuresInSystem, lambda x: x.itemID == structureID)
