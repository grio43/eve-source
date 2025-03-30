#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\starMapSvc.py
from collections import defaultdict
import itertools
import math
from math import sin, cos, pi
import sys
import mathext
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML, SERVICE_RUNNING, SERVICE_START_PENDING
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.bracket import Bracket as BracketCore
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.camera.starmapCamera import StarmapCamera
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.inflight.bracket import Bracket
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
from eve.client.script.ui.shared.maps.label import MapLabel, TransformableLabel
from eve.client.script.ui.shared.maps.route import MapRoute
import evecamera
import evetypes
import industry
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem, IsKnownSpaceRegion, IsKnownSpaceConstellation, IsDeprecatedStation, IsTriglavianSystem
import blue
import telemetry
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
import trinity
from eve.client.script.ui.util import uix
import uthread
from eve.client.script.ui.shared.fleet import fleetbroadcastexports as fleetbr, fleetBroadcastConst
from carbonui.primitives.line import Line
from eve.client.script.ui.shared.maps import starModeHandler
from eve.client.script.ui.shared.maps.hexMap import HexMapController
from eve.client.script.ui.control.pointerPanel import RefreshPanelPosition
from evePathfinder.pathfinderconst import ROUTE_TYPE_SAFE, ROUTE_TYPE_SHORTEST, ROUTE_TYPE_UNSAFE
from eve.client.script.ui.shared.maps import mapcommon
from eve.client.script.ui.shared.maps.mapcommon import STARMAP_SCALE, SUN_DATA, JUMP_TYPES, JUMP_COLORS, ZOOM_MAX_STARMAP, ZOOM_MIN_STARMAP, TILE_MODE_SOVEREIGNTY, TILE_MODE_STANDIGS
import geo2
import carbonui.const as uiconst
import localization
from eve.client.script.ui.shared.maps import maputils
from eve.common.script.util.facwarCommon import IsAnyFWFaction
from npcs.npccorporations import get_corporation_faction_id
from starmap.util import SolarSystemMapInfo, ConstellationMapInfo, RegionMapInfo, MapJumpInfo, StarmapInterest, OverrideAlpha, OverrideColour, Pairwise, ScaleColour, SelectiveIndexedIterItems
import time
import cPickle
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from menu import MenuLabel
SHOW_ALL_REGION_LABELS = 3
SHOW_SELECTED_REGION_AND_NEIGHBOURS_LABELS = 2
SHOW_SELECTED_REGION_LABEL = 1
SHOW_NO_REGION_LABELS = 0
SUNBASE = 7.5
LINESTEP_CONSTELLATION = 20.0
LINESTEP_REGION = 40.0
doingDebug = 0
SHOW_NONE = 0
SHOW_SELECTION = 1
SHOW_REGION = 2
SHOW_NEIGHBORS = 3
SHOW_ALL = 4
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/Starmap.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/MapSprite.dds'
OVERGLOW_FACTOR = 'OverGlowFactor'
DISTANCE_RANGE = 'distanceRange'
DEFAULT_STAR_PARTICLE_COLOR = (0.1, 0.1, 0.1, 1.0)
NEUTRAL_COLOR = (0.25, 0.25, 0.25, 1.0)
PICK_RADIUS = 400.0
PICK_RADIUS_NEAR = 100.0
PICK_RADIUS_FAR = 400.0
REGION_LABEL_SCALE = 10.0
MAP_FLATTEN_ANIM_TIME = 750.0
MAP_ROTATION = (0.0, math.radians(180.0), 0.0)
MAP_XYZW_ROTATION = (1.0, 0.0, 0.0, 0.0)
MAP_XYZW_INV_ROTATION = (-1.0, 0.0, 0.0, 0.0)
HEX_TILE_SIZE = 60
DEFAULT_SOLAR_SYSTEM_ID = 30005204

def GetUserUiSetting(name, default):
    return settings.user.ui.Get(name, default)


def GetCharUiSetting(name, default):
    return settings.char.ui.Get(name, default)


def SetUserUiSetting(name, value):
    return settings.user.ui.Set(name, value)


def SetCharUiSetting(name, value):
    return settings.char.ui.Set(name, value)


class StarMapSvc(Service):
    __guid__ = 'svc.starmap'
    __notifyevents__ = ['OnServerMapDataPush',
     'OnAvoidanceItemsChanged',
     'OnMapReset',
     'OnUIScalingChange',
     'OnAutopilotUpdated',
     'OnDestinationChange',
     'ProcessSessionReset',
     'OnSessionReset',
     'OnCharacterSessionChanged']
    __servicename__ = 'starmap'
    __displayname__ = 'Star Map Client Service'
    __dependencies__ = ['clientPathfinderService',
     'map',
     'sceneManager',
     'viewState',
     'autoPilot',
     'loading']
    __startupdependencies__ = ['settings',
     'solarsystemInterferenceSvc',
     'insurgencyCampaignSvc',
     'corruptionSuppressionSvc']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.HINT_LOCATION_HEADERS = (localization.GetByLabel('UI/Common/LocationTypes/Region'),
         localization.GetByLabel('UI/Common/Constellation'),
         localization.GetByLabel('UI/Common/SolarSystem'),
         '')
        self.state = SERVICE_START_PENDING
        self.LogInfo('Starting Map Client Svc')
        self.changingPerspective = False
        self.Reset()
        self.state = SERVICE_RUNNING
        self.ClearMapCache()
        self.doingLogoff = False

    def ClearMapCache(self):
        self.starMapCache = None
        self.knownSolarSystems = None
        self.knownConstellations = None
        self.knownRegions = None
        self.mapJumps = None
        self.LogInfo('Starmap cache cleared')

    def Stop(self, memStream = None):
        if trinity.device is None:
            return
        self.LogInfo('Map svc')
        self.Reset()

    def Open(self, interestID = None, starColorMode = None, *args):
        OpenMap(interestID=interestID, starColorMode=starColorMode)

    def OnAvoidanceItemsChanged(self):
        if self.viewState.IsViewActive('starmap'):
            starColorMode = GetUserUiSetting('starscolorby', mapcommon.STARMODE_SECURITY)
            if starColorMode == mapcommon.STARMODE_AVOIDANCE:
                self.SetStarColorMode(mapcommon.STARMODE_AVOIDANCE)

    def OnUIScalingChange(self, *args):
        viewStateSvc = self.viewState
        if viewStateSvc.IsViewActive('starmap'):
            viewStateSvc.ToggleSecondaryView('starmap')
            viewStateSvc.ToggleSecondaryView('starmap')

    def OnMapReset(self):
        self.Reset()

    def ProcessSessionReset(self):
        SetCharUiSetting('autopilot_waypoints', self.GetWaypoints())
        self.doingLogoff = True

    def OnSessionReset(self):
        self.Reset()
        self.doingLogoff = False

    def OnCharacterSessionChanged(self, oldCharacterID, newCharacterID):
        if oldCharacterID is None and newCharacterID is not None:
            self.UpdateRoute()

    @telemetry.ZONE_METHOD
    def CleanUp(self):
        cachedDestinationPath = self.destinationPath
        self.Reset()
        self.destinationPath = cachedDestinationPath
        for child in uicore.layer.starmap.children[:]:
            if child.name == '__cursor' or child.name == 'myloc' or child.name == 'myDest':
                child.Close()

        scene = self.sceneManager.GetRegisteredScene('starmap')
        if scene:
            del scene.objects[:]
            scene.curveSets.remove(self.curveSet)
            self.curveSet = None
        self.sceneManager.UnregisterScene('starmap')
        self.sceneManager.UnregisterCamera(evecamera.CAM_STARMAP)
        self.mylocation = None

    @telemetry.ZONE_METHOD
    def Reset(self):
        self.LogInfo('MapSvc Reset')
        self.securityInfo = None
        self.destinationPath = [None]
        self.interest = None
        self.currentSolarsystemID = None
        self.currentSolarsystem = None
        self.solarsystemBracketsLoaded = None
        self.solarsystemHierarchyData = {}
        self.expandingHint = None
        rangeCircleTF = getattr(self, 'rangeCircleTF', None)
        if rangeCircleTF:
            for each in rangeCircleTF.curveSets[:]:
                rangeCircleTF.curveSets.remove(each)

        self.rangeCircleTF = None
        self.rangeLineSet = None
        if hasattr(self, 'mapRoot') and self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        if hasattr(self, 'hexMap') and self.hexMap is not None:
            self.hexMap.tilePool = []
            self.hexMap = None
        self.particleIDToSystemIDMap = None
        self.solarSystemIDToParticleID = None
        self.currentLineColour = {}
        self.mapconnectionscache = None
        self.autoPilotRoute = None
        self.genericRoute = None
        self.genericRoutePath = None
        self.flattened = GetUserUiSetting('mapFlattened', 1)
        self.wasConnectionViewMode = None
        self.regionLabels = None
        self.regionLabelParent = None
        self.solarsystemsCache = None
        self.lineIdAndToSystemIdByFromSystemId = None
        self.allianceSolarSystems = {'s': {},
         'c': {}}
        self.ClearLabels()
        toClose = getattr(self, 'labels', {})
        for each in toClose.itervalues():
            each.Close()

        self.labels = {}
        self.labeltrackersTF = None
        self.landmarkTF = None
        self.labeltrackers = {}
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.cursor = None
        toClose = getattr(self, 'uicursor', None)
        if toClose:
            toClose.Close()
        self.uicursor = None
        self.minimizedWindows = []
        self.stationCountCache = None
        self.warFactionByOwner = None

    def GetInterest(self):
        if self.interest is None:
            self.interest = StarmapInterest(session.regionid, session.constellationid, session.solarsystemid2)
        return self.interest

    def OnServerMapDataPush(self, tricolors, data):
        self.viewState.ActivateView('starmap')
        processedData = {}
        for systemID, blobSize, colorScale, descriptionText, overrideColor in data:
            if overrideColor == (None, None, None):
                processedData[systemID] = (blobSize,
                 colorScale,
                 descriptionText,
                 None)
            else:
                processedData[systemID] = (blobSize,
                 colorScale,
                 descriptionText,
                 trinity.TriColor(*overrideColor))

        self.HighlightSolarSystems(processedData, [ trinity.TriColor(r, g, b) for r, g, b in tricolors ])

    def PickSolarSystemID(self):
        if self.starParticles is None:
            return
        projection, view, viewport = uix.GetFullscreenProjectionViewAndViewport()
        x, y = int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling)
        particleID = trinity.PickParticle(self.starParticles, x, y, self.mapStars.worldTransform, view, projection, viewport, self.GetStarPickRadius())
        return self.particleIDToSystemIDMap.get(particleID, None)

    def PickParticle(self):
        if self.starParticles is None:
            return
        try:
            projection, view, viewport = uix.GetFullscreenProjectionViewAndViewport()
        except AttributeError:
            return

        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        particleID = trinity.PickParticle(self.starParticles, x, y, self.mapStars.worldTransform, view, projection, viewport, self.GetStarPickRadius())
        if particleID != -1:
            return particleID
        else:
            return

    def GetItemMenu(self, itemID):
        item = self.map.GetItem(itemID, retall=True)
        if not item:
            return []
        m = []
        itemLabel = MenuLabel('UI/Map/StarMap/ItemMenuLabel', {'loc': itemID,
         'item': item.typeID})
        m.append((itemLabel, self.SetInterest, (item.itemID,)))
        parentID = self.map.GetParent(item.itemID)
        while parentID != const.locationUniverse:
            parent = self.map.GetItem(parentID)
            if parent is not None:
                parentLabel = MenuLabel('UI/Map/StarMap/ItemMenuParentLabel', {'loc': parentID,
                 'item': parent.typeID})
                m.append((parentLabel, self.SetInterest, (parentID,)))
            parentID = self.map.GetParent(parentID)

        m.append(None)
        m += GetMenuService().CelestialMenu(itemID, mapItem=item)
        m.append(None)
        m.append((MenuLabel('UI/Map/StarMap/CenterOnScreen'), self.SetInterest, (itemID, 1)))
        return m

    @telemetry.ZONE_METHOD
    def MakeBroadcastBracket(self, gbType, itemID, charID):
        if gbType != 'TravelTo':
            raise NotImplementedError
        if self.mapRoot is None:
            return
        sysname = cfg.evelocations.Get(itemID).name.encode('utf-8')
        tracker = trinity.EveTransform()
        tracker.name = '__fleetbroadcast_%s' % sysname
        self.mapRoot.children.append(tracker)
        loc = self.map.GetItem(itemID)
        pos = (loc.x * STARMAP_SCALE, loc.y * STARMAP_SCALE, loc.z * STARMAP_SCALE)
        tracker.translation = pos
        anchor = Bracket(parent=uicore.layer.starmap, state=uiconst.UI_DISABLED, width=1, height=1, align=uiconst.NOALIGN, name='fleetBroadcastAnchor_%s' % sysname)
        anchor.itemID = itemID
        anchor.display = True
        anchor.trackTransform = tracker
        iconPath = fleetBroadcastConst.iconsLargeByBroadcastType[fleetBroadcastConst.BROADCAST_TRAVEL_TO]
        icon = eveIcon.Icon(icon=iconPath, parent=anchor, idx=0, pos=(0, 0, 32, 32), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        icon.name = 'fleetBroadcastIcon_%s' % sysname
        icon.hint = fleetbr.GetCaption_TravelTo(charID, itemID, itemID)
        icon.GetMenu = fleetbr.MenuGetter('TravelTo', charID, itemID)

        def Cleanup(*args):
            try:
                self.mapRoot.children.fremove(tracker)
            except (AttributeError, ValueError):
                sys.exc_clear()

        icon.OnClose = Cleanup
        return anchor

    def GetCloudNumFromItemID(self, itemID):
        if itemID in self.solarSystemIDToParticleID:
            return self.solarSystemIDToParticleID[itemID]

    def GetItemIDFromParticleID(self, particleID):
        solarSystemID = None
        if self.particleIDToSystemIDMap:
            solarSystemID = self.particleIDToSystemIDMap[particleID]
        return solarSystemID

    @telemetry.ZONE_METHOD
    def UpdateHint(self, nav = None):
        if getattr(self, 'doinghint', 0):
            return
        self.doinghint = 1
        if self.starParticles is None:
            self.doinghint = 0
            return
        projection, view, viewport = uix.GetFullscreenProjectionViewAndViewport()
        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        particleID = trinity.PickParticle(self.starParticles, x, y, self.mapStars.worldTransform, view, projection, viewport, self.GetStarPickRadius())
        if getattr(self, 'lastpick', None) == particleID:
            self.doinghint = 0
            return
        hint = ''
        if particleID in self.particleIDToSystemIDMap:
            itemID = self.particleIDToSystemIDMap[particleID]
            item = self.map.GetItem(itemID)
            hint = item.itemName
            hierarchy = self.map.GetParentLocationID(itemID)
            if hierarchy:
                locs = []
                for locationID in hierarchy[1:]:
                    if locationID is not None:
                        if locationID not in locs:
                            locs.append(locationID)

                if len(locs):
                    cfg.evelocations.Prime(locs)
                hintParts = []
                for i, locationID in enumerate(hierarchy[1:]):
                    if locationID is not None:
                        hintParts.appen('%s %s' % (cfg.evelocations.Get(locationID).name, self.HINT_LOCATION_HEADERS[i]))

                hint = ' - '.join(hintParts)
        self.lastpick = particleID
        if nav:
            nav.hint = hint
        self.doinghint = 0

    def RemoveChild(self, tf, childname):
        for each in tf.children[:]:
            if each.name == childname:
                tf.children.remove(each)

    @telemetry.ZONE_METHOD
    def ShowJumpDriveRange(self):
        if getattr(self, 'mylocation', None):
            for each in self.mylocation.trackerTransform.children[:]:
                if each.name == 'jumpDriveRange':
                    self.mylocation.trackerTransform.children.remove(each)

        else:
            return
        if not IsKnownSpaceRegion(session.regionid):
            return
        if not InShipInSpace():
            return
        shipID = eveCfg.GetActiveShip()
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        driveRange = dogmaLM.GetAttributeValue(shipID, const.attributeJumpDriveRange)
        if driveRange is None or driveRange == 0:
            return
        scale = 2.0 * driveRange * const.LIGHTYEAR * STARMAP_SCALE
        sphere = trinity.Load('res:/dx9/model/UI/JumpRangeBubble.red')
        sphere.scaling = (scale, scale, scale)
        sphere.name = 'jumpDriveRange'
        if self.IsFlat():
            sphere.display = False
        self.mylocation.trackerTransform.children.append(sphere)

    def RemoveMyLocation(self):
        self.RemoveChild(self.mapRoot, '__mylocation')
        if getattr(self, 'mylocationBracket', None):
            self.mylocationBracket.Close()
            self.mylocationBracket = None
            self.mylocation = None

    @telemetry.ZONE_METHOD
    def ShowWhereIAm(self):
        if self.mapRoot is None:
            return
        if not IsKnownSpaceRegion(session.regionid):
            self.RemoveMyLocation()
        else:
            locationid = session.solarsystemid2
            if getattr(self, 'mylocation', None) is None:
                self.RemoveMyLocation()
                tracker = trinity.EveTransform()
                tracker.name = '__mylocation'
                self.mapRoot.children.append(tracker)
                label = self.GetCurrLocationBracket()
                label.Startup('myloc', locationid, None, tracker, None, 1)
                label.clipChildren = False
                labeltext = eveLabel.EveHeaderSmall(text=localization.GetByLabel('UI/Map/StarMap/lblYouAreHere'), parent=label, left=210, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, idx=0)
                sm.GetService('ui').BlinkSpriteA(labeltext, 1.0, 750, None, passColor=0, minA=0.5)
                self.labeltext = labeltext
                self.mylocationBracket = label
            else:
                tracker = self.mylocation.trackerTransform
            pos = self.knownSolarSystems[locationid].scaledCenter
            tracker.translation = pos
            bp = sm.GetService('michelle').GetBallpark()
            if bp is not None:
                ship = bp.GetBall(session.shipid)
                if ship is not None:
                    shipPos = geo2.Vector(ship.x, ship.y, ship.z)
                    shipPos *= STARMAP_SCALE
                    pos += shipPos
                    tracker.translation = pos
            self.mylocation = utillib.KeyVal(locationID=locationid, trackerTransform=tracker)
        self.ShowDestination()
        self.ShowJumpDriveRange()

    @telemetry.ZONE_METHOD
    def ShowDestination(self):
        if not self.viewState.IsViewActive('starmap'):
            return
        waypoints = self.GetWaypoints()
        self.mydestination = getattr(self, 'mydestination', [])
        if len(self.mydestination) == 0:
            if len(waypoints) == 0:
                return
        else:
            for waypoint in self.mydestination:
                waypoint.label.Close()
                self.mapRoot.children.fremove(waypoint.tracker)

        self.mydestination = []
        lastWaypoint = session.solarsystemid2
        totalJumps = 0
        if len(waypoints) > 0:
            currentExtractWaypoint = waypoints[0]
            waypointIndex = 0
            waypointDestinationList = []
            currentDestinationList = [lastWaypoint]
            for locationID in self.destinationPath:
                currentDestinationList.append(locationID)
                if locationID == currentExtractWaypoint:
                    waypointDestinationList.append(currentDestinationList)
                    currentDestinationList = [locationID]
                    waypointIndex += 1
                    if waypointIndex == len(waypoints):
                        break
                    currentExtractWaypoint = waypoints[waypointIndex]

        else:
            waypointDestinationList = []
        waypointLabels = {}
        for waypointIndex, waypointID in enumerate(waypoints):
            destinations = []
            if waypointIndex < len(waypointDestinationList):
                for destination in waypointDestinationList[waypointIndex]:
                    if idCheckers.IsSolarSystem(destination):
                        destinations.append(destination)

            targetItemName = cfg.evelocations.Get(waypointID).locationName
            wpIdx = waypointIndex + 1
            if not len(destinations):
                wpLabel = localization.GetByLabel('UI/Map/StarMap/ShowDestinationWaypointUnreachable', waypointNumber=wpIdx, targetName=targetItemName)
            else:
                totalJumps = totalJumps + len(destinations) - 1
                wpLabel = localization.GetByLabel('UI/Map/StarMap/ShowDestinationWaypoint', waypointNumber=wpIdx, targetName=targetItemName, jumps=totalJumps)
            tracker = trinity.EveTransform()
            tracker.name = '__waypoint_%d' % waypointIndex
            if self.mapRoot:
                self.mapRoot.children.append(tracker)
            label = self.GetCurrLocationBracket()
            label.Startup('myDest', waypointID, const.groupSolarSystem, tracker, None, 1)
            label.clipChildren = False
            if idCheckers.IsStation(waypointID):
                waypointID = cfg.stations.Get(waypointID).solarSystemID
            if waypointID in waypointLabels:
                labeltext = waypointLabels[waypointID]
                labeltext.text += '\n%s' % wpLabel
            else:
                labeltext = eveLabel.EveHeaderSmall(text=wpLabel, parent=label, left=210, top=5, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, idx=0)
                waypointLabels[waypointID] = labeltext
            if waypointID == session.solarsystemid2:
                labeltext.top = 20
            labeltext.SetRGB(1.0, 1.0, 0.0)
            sm.GetService('ui').BlinkSpriteA(labeltext, 1.0, 750, None, passColor=0, minA=0.5)
            location = cfg.evelocations.Get(waypointID)
            pos = (location.x * STARMAP_SCALE, location.y * STARMAP_SCALE, location.z * STARMAP_SCALE)
            tracker.translation = pos
            self.mydestination.append(utillib.KeyVal(waypointID=waypointID, tracker=tracker, label=label))
            label.state = uiconst.UI_DISABLED

    def GetCurrLocationBracket(self):
        currentLocation = MapLabel(parent=uicore.layer.starmap, name='currentlocation', pos=(0, 0, 280, 20), align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN, dock=False)
        Fill(parent=currentLocation, name='white', pos=(154, 11, 48, 1), state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25), align=uiconst.TOPLEFT)
        Sprite(parent=currentLocation, name='frame', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/StarMapSvc/currentLocation.png')
        return currentLocation

    def IsFlat(self):
        return self.flattened

    @telemetry.ZONE_METHOD
    def Unflatten(self):
        registeredScene = self.sceneManager.GetRegisteredScene('starmap')
        if not self.flattened or registeredScene is None:
            return
        try:
            uicore.desktop.state = uiconst.UI_DISABLED
            start = blue.os.GetSimTime()
            cameraParent = self.GetCameraParent()
            current = self.mapRoot.rotationCurve.curve.GetQuaternionAt(start)
            key = list(self.mapRoot.rotationCurve.curve.keys[0])
            key[1] = (current.x,
             current.y,
             current.z,
             current.w)
            self.mapRoot.rotationCurve.curve.keys[0] = tuple(key)
            key = list(self.mapRoot.rotationCurve.curve.keys[1])
            key[0] = 1
            key[1] = MAP_XYZW_ROTATION
            self.mapRoot.rotationCurve.curve.keys[1] = tuple(key)
            self.mapRoot.rotationCurve.curve.OnKeysChanged()
            self.mapRoot.rotationCurve.ResetStart()
            redrawRoute = False
            if self.autoPilotRoute or self.genericRoute:
                redrawRoute = True
                self.ClearRoute('autoPilotRoute')
            redrawGenericRoute = False
            if self.genericRoute:
                redrawGenericRoute = True
                self.ClearRoute('genericRoute')
            if self.rollCamera:
                self.rollCamera = False
                self.starmapCamera.OrbitParent(0.0, 10.0)
            self.UpdateHexMap(isFlat=False)
            if getattr(self, 'mylocation', None):
                for each in self.mylocation.trackerTransform.children[:]:
                    if each.name == 'jumpDriveRange':
                        each.display = True

            posEnd = self.interestEndPos
            posBegin = cameraParent.translation
            self.regionLabelParent.display = False
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetSimTime()) / 1000.0, 1.0))
                self.mapRoot.scaling = self.solarSystemJumpLineSet.scaling = (1.0, mathext.lerp(0.0001, 1.0, ndt), 1.0)
                if posBegin and posEnd:
                    pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                    cameraParent.translation = pos
                lineSet = self.solarSystemJumpLineSet
                for lineID, curveInfo in self.curvedLineInfoByLineID.iteritems():
                    midPos, offsetVec = curveInfo
                    scaledOffset = geo2.Vec3Scale(offsetVec, ndt)
                    lineSet.ChangeLineIntermediateCrt(lineID, geo2.Vec3Add(midPos, scaledOffset))

                lineSet.SubmitChanges()
                blue.pyos.synchro.Yield()

            for labelTransform in self.regionLabelParent.children:
                x, y, z = labelTransform.scaling
                labelTransform.scaling = (x, y * 0.0001, z)

            if GetUserUiSetting('rlabel_region', 1):
                self.regionLabelParent.display = True
            self.flattened = 0
            SetUserUiSetting('mapFlattened', self.flattened)
            sm.ScatterEvent('OnFlattenModeChanged', self.flattened)
            if redrawRoute:
                self.UpdateRoute()
            if redrawGenericRoute and self.genericRoutePath:
                self.DrawRouteTo(targetID=self.genericRoutePath[-1], sourceID=self.genericRoutePath[0])
            self.OnCameraMoved()
        finally:
            uicore.desktop.state = uiconst.UI_NORMAL

    def GetCameraParent(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_STARMAP).GetCameraParent()

    @telemetry.ZONE_METHOD
    def Flatten(self, initing = False):
        if not initing:
            registeredScene = self.sceneManager.GetRegisteredScene('starmap')
            if self.flattened or registeredScene is None:
                return
        try:
            uicore.desktop.state = uiconst.UI_DISABLED
            if initing:
                duration = 0.0001
            else:
                duration = 1.0
            start = blue.os.GetSimTime()
            cameraParent = self.GetCameraParent()
            camera = self.sceneManager.GetRegisteredCamera(evecamera.CAM_STARMAP)
            cY, cP, cR = geo2.QuaternionRotationGetYawPitchRoll(camera.rotationAroundParent)
            current = self.mapRoot.rotationCurve.GetQuaternionAt(start)
            key = list(self.mapRoot.rotationCurve.curve.keys[0])
            key[1] = (current.x,
             current.y,
             current.z,
             current.w)
            self.mapRoot.rotationCurve.curve.keys[0] = tuple(key)
            key = list(self.mapRoot.rotationCurve.curve.keys[1])
            key[0] = duration
            key[1] = geo2.QuaternionRotationSetYawPitchRoll(cY, cP - pi * 0.5, cR)
            self.mapRoot.rotationCurve.curve.keys[1] = tuple(key)
            self.mapRoot.rotationCurve.curve.OnKeysChanged()
            self.mapRoot.rotationCurve.ResetStart()
            redrawRoute = False
            if self.autoPilotRoute or self.genericRoute:
                redrawRoute = True
                self.ClearRoute('autoPilotRoute')
            redrawGenericRoute = False
            if self.genericRoute:
                redrawGenericRoute = True
                self.ClearRoute('genericRoute')
            curveQuat = geo2.QuaternionRotationSetYawPitchRoll(cY, cP - pi * 0.5, cR)
            camPos = cameraParent.translation
            posBegin = geo2.Vector(*camPos)
            reverseQuat = MAP_XYZW_INV_ROTATION
            localCam = geo2.QuaternionTransformVector(reverseQuat, posBegin)
            localCam = geo2.Vector(*localCam)
            localCam.y = 0.0
            posEnd = geo2.QuaternionTransformVector(curveQuat, localCam)
            self.regionLabelParent.display = False
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetSimTime()) / (duration * 1000.0), 1.0))
                self.mapRoot.scaling = self.solarSystemJumpLineSet.scaling = (1.0, mathext.lerp(1.0, 0.0001, ndt), 1.0)
                if posBegin and posEnd:
                    pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                    cameraParent.translation = pos
                lineSet = self.solarSystemJumpLineSet
                for lineID, curveInfo in self.curvedLineInfoByLineID.iteritems():
                    midPos, offsetVec = curveInfo
                    scaledOffset = geo2.Vec3Scale(offsetVec, 1.0 - ndt)
                    lineSet.ChangeLineIntermediateCrt(lineID, geo2.Vec3Add(midPos, scaledOffset))

                lineSet.SubmitChanges()
                blue.pyos.synchro.Yield()

            for labelTransform in self.regionLabelParent.children:
                x, y, z = labelTransform.scaling
                labelTransform.scaling = (x, y * 10000.0, z)

            self.hexMap.Enable(True)
            if getattr(self, 'mylocation', None):
                for each in self.mylocation.trackerTransform.children[:]:
                    if each.name == 'jumpDriveRange':
                        each.display = False

            if GetUserUiSetting('rlabel_region', 1):
                self.regionLabelParent.display = True
            self.flattened = 1
            SetUserUiSetting('mapFlattened', self.flattened)
            self.UpdateHexMap(isFlat=True)
            sm.ScatterEvent('OnFlattenModeChanged', self.flattened)
            if redrawRoute:
                self.UpdateRoute()
            if redrawGenericRoute and self.genericRoutePath:
                self.DrawRouteTo(targetID=self.genericRoutePath[-1], sourceID=self.genericRoutePath[0])
            self.OnCameraMoved()
        finally:
            uicore.desktop.state = uiconst.UI_NORMAL

    def ToggleFlattenMode(self):
        if not self.changingPerspective:
            try:
                self.changingPerspective = True
                flattened = GetUserUiSetting('mapFlattened', 1)
                if flattened:
                    self.Unflatten()
                else:
                    self.Flatten()
            finally:
                self.changingPerspective = False

    @telemetry.ZONE_METHOD
    def DrawPoints(self, parent):
        self.mapStars = trinity.EveTransform()
        self.mapStars.name = '__mapStars'
        tex = trinity.TriTextureParameter()
        tex.name = 'TexMap'
        tex.resourcePath = PARTICLE_SPRITE_TEXTURE
        overglowFactor = trinity.Tr2FloatParameter()
        overglowFactor.name = OVERGLOW_FACTOR
        overglowFactor.value = 0.0
        self.overglowFactor = overglowFactor
        distanceRangeStars = trinity.Tr2Vector4Parameter()
        distanceRangeStars.name = DISTANCE_RANGE
        distanceRangeStars.value = (0, 1, 0, 0)
        self.distanceRangeStars = distanceRangeStars
        self.starParticles = trinity.Tr2RuntimeInstanceData()
        self.starParticles.SetElementLayout([(trinity.PARTICLE_ELEMENT_TYPE.POSITION, 0, 3), (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 0, 1), (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 1, 4)])
        mesh = trinity.Tr2InstancedMesh()
        mesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
        mesh.instanceGeometryResource = self.starParticles
        area = trinity.Tr2MeshArea()
        area.effect = trinity.Tr2Effect()
        area.effect.effectFilePath = PARTICLE_EFFECT
        area.effect.resources.append(tex)
        area.effect.parameters.append(overglowFactor)
        area.effect.parameters.append(distanceRangeStars)
        mesh.additiveAreas.append(area)
        self.mapStars.mesh = mesh
        distanceRangeLines = trinity.Tr2Vector4Parameter()
        distanceRangeLines.name = DISTANCE_RANGE
        distanceRangeLines.value = (0, 1, 0, 0)
        self.distanceRangeLines = distanceRangeLines
        self.solarSystemJumpLineSet.lineEffect.parameters.append(self.distanceRangeLines)
        self.particleIDToSystemIDMap = {}
        self.solarSystemIDToParticleID = {}
        self.particleColors = []
        particleCounter = itertools.count()
        starParticleData = []
        for systemID, system in self.GetKnownUniverseSolarSystems().iteritems():
            particleID = particleCounter.next()
            self.solarSystemIDToParticleID[systemID] = particleID
            self.particleIDToSystemIDMap[particleID] = systemID
            self.particleColors.append(list(system.star.color))
            starParticleData.append((system.scaledCenter, SUNBASE, system.star.color))

        self.starParticles.SetData(starParticleData)
        self.starParticles.UpdateBoundingBox()
        mesh.minBounds = self.starParticles.aabbMin
        mesh.maxBounds = self.starParticles.aabbMax
        parent.children.append(self.mapStars)

    @telemetry.ZONE_METHOD
    def GetStarMapCache(self):
        if self.starMapCache is None:
            res = blue.ResFile()
            starMapResPath = 'res:/staticdata/starMapCache.pickle'
            if not res.open('%s' % starMapResPath):
                self.LogError('Could not load Starmap Cache data file: %s' % starMapResPath)
            else:
                try:
                    pickleData = res.Read()
                    self.starMapCache = cPickle.loads(pickleData)
                finally:
                    res.Close()

        return self.starMapCache

    @telemetry.ZONE_METHOD
    def GetKnownUniverseSolarSystems(self):
        if self.knownSolarSystems is None:
            self.knownSolarSystems = {}
            for systemID, system in self.GetStarMapCache()['solarSystems'].iteritems():
                if not IsKnownSpaceSystem(systemID):
                    continue
                center = system['center']
                scaledCenter = geo2.Scale(geo2.Vector(*center), STARMAP_SCALE)
                solarSystemInfo = SolarSystemMapInfo()
                solarSystemInfo.center = center
                solarSystemInfo.scaledCenter = scaledCenter
                solarSystemInfo.regionID = system['regionID']
                solarSystemInfo.constellationID = system['constellationID']
                solarSystemInfo.star = SUN_DATA[system['sunTypeID']]
                solarSystemInfo.factionID = system['factionID']
                solarSystemInfo.neighbours = system['neighbours']
                solarSystemInfo.planetCountByType = system['planetCountByType']
                solarSystemInfo.planetItemIDs = system['planetItemIDs']
                self.knownSolarSystems[systemID] = solarSystemInfo

        return self.knownSolarSystems

    @telemetry.ZONE_METHOD
    def GetKnownUniverseRegions(self):
        if self.knownRegions is None:
            self.knownRegions = {}
            for regionID, region in self.GetStarMapCache()['regions'].iteritems():
                if not IsKnownSpaceRegion(regionID):
                    continue
                regionInfo = RegionMapInfo()
                regionInfo.neighbours = region['neighbours']
                regionInfo.solarSystemIDs = region['solarSystemIDs']
                regionInfo.constellationIDs = region['constellationIDs']
                regionInfo.scaledCenter = geo2.Scale(geo2.Vector(*region['center']), STARMAP_SCALE)
                self.knownRegions[regionID] = regionInfo

        return self.knownRegions

    @telemetry.ZONE_METHOD
    def GetKnownUniverseConstellations(self):
        if self.knownConstellations is None:
            self.knownConstellations = {}
            for constellationID, constellation in self.GetStarMapCache()['constellations'].iteritems():
                if not IsKnownSpaceConstellation(constellationID):
                    continue
                constellationInfo = ConstellationMapInfo()
                constellationInfo.regionID = constellation['regionID']
                constellationInfo.neighbours = constellation['neighbours']
                constellationInfo.solarSystemIDs = constellation['solarSystemIDs']
                constellationInfo.scaledCenter = geo2.Scale(geo2.Vector(*constellation['center']), STARMAP_SCALE)
                self.knownConstellations[constellationID] = constellationInfo

        return self.knownConstellations

    @telemetry.ZONE_METHOD
    def IterateJumps(self):
        if self.mapJumps is None:
            self.mapJumps = []
            for jump in self.GetStarMapCache()['jumps']:
                fromSystemID = jump['fromSystemID']
                toSystemID = jump['toSystemID']
                fromSystem = self.GetKnownSolarSystem(fromSystemID)
                toSystem = self.GetKnownSolarSystem(toSystemID)
                fromToDirection = geo2.Scale(geo2.Vector(*geo2.Vec3Normalize(geo2.Vec3Subtract(fromSystem.scaledCenter, toSystem.scaledCenter))), 8.0)
                jumpInfo = MapJumpInfo()
                jumpInfo.jumpType = jump['jumpType']
                jumpInfo.fromSystemID = fromSystemID
                jumpInfo.toSystemID = toSystemID
                jumpInfo.adjustedFromVector = geo2.Vec3Add(fromSystem.scaledCenter, fromToDirection)
                jumpInfo.adjustedToVector = geo2.Vec3Subtract(toSystem.scaledCenter, fromToDirection)
                self.mapJumps.append(jumpInfo)
                yield jumpInfo

        else:
            for jump in self.mapJumps:
                yield jump

    def GetKnownSolarSystem(self, solarSystemID):
        return self.GetKnownUniverseSolarSystems()[solarSystemID]

    def GetKnownConstellation(self, constellationID):
        return self.GetKnownUniverseConstellations()[constellationID]

    def GetKnownRegion(self, regionID):
        return self.GetKnownUniverseRegions()[regionID]

    def CreateHexmap(self):
        hexMapRoot = trinity.EveTransform()
        hexMapRoot.name = '__hexMapRoot'
        hexMapRoot.translation = (0.0, 20000.0, 0.0)
        self.hexMap = HexMapController(hexMapRoot, self.GetKnownUniverseSolarSystems().iteritems())
        self.mapRoot.children.append(hexMapRoot)

    def CreateCursor(self):
        self.cursor = trinity.EveTransform()
        self.cursor.name = '__cursorTF'
        self.mapRoot.children.append(self.cursor)
        self.uicursor = BracketCore(parent=uicore.layer.starmap, align=uiconst.NOALIGN)
        self.uicursor.name = '__cursor'
        self.uicursor.width = uicore.uilib.desktop.width * 2
        self.uicursor.height = uicore.uilib.desktop.height * 2
        self.uicursor.state = uiconst.UI_HIDDEN
        self.uicursor.solarsystemID = None
        icon = eveIcon.Icon(icon='ui_38_16_255', parent=self.uicursor, pos=(0, 0, 16, 16), align=uiconst.CENTER, state=uiconst.UI_DISABLED, pickRadius=5, idx=0)
        self.uicursor.icon = icon
        icon.state = uiconst.UI_NORMAL
        icon.DelegateEvents(uicore.layer.starmap)
        icon.LoadTooltipPanel = self.LoadSolarSystemTooltipPanel
        self.uicursor.trackTransform = self.cursor
        self.uicursor.dock = False

    def LoadSolarSystemTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        mapSvc = sm.GetService('map')
        starmapSvc = sm.GetService('starmap')
        particleID = self.uicursor.particleID
        itemID = self.uicursor.solarsystemID
        mapData = mapSvc.GetItem(itemID)
        if mapData is None:
            return
        securityColor = mapSvc.GetSystemColor(itemID)
        typeID = None
        groupID = None
        if mapData:
            displayName = mapData.itemName
            typeID = mapData.typeID
            groupID = evetypes.GetGroupID(mapData.typeID)
        if groupID is None:
            return
        tooltipPanel.AddLabelLarge(text=displayName, bold=True)
        tooltipPanel.AddCell(cellObject=InfoIcon(typeID=typeID, itemID=itemID, align=uiconst.TOPRIGHT, left=-3))
        tooltipPanel.state = uiconst.UI_NORMAL
        securityStatus = mapSvc.GetSecurityStatus(itemID)
        if securityStatus is not None:
            securityIconText = sm.GetService('securitySvc').get_security_modifier_icon_text(itemID)
            tooltipPanel.AddLabelMedium(text=localization.GetByLabel('Tooltips/Map/SecurityStatus'))
            securityStatusText = str(securityStatus) + securityIconText
            tooltipPanel.AddLabelMedium(text=securityStatusText, align=uiconst.CENTERRIGHT, color=securityColor, cellPadding=(10, 0, 0, 0), state=uiconst.UI_NORMAL)
        data = starmapSvc.GetStarData()
        if particleID in data:
            hintFunc, hintArgs = data[particleID]
            particleHint = hintFunc(*hintArgs)
            if particleHint:
                tooltipPanel.AddCell(Line(align=uiconst.TOTOP, color=(1, 1, 1, 0.2)), colSpan=tooltipPanel.columns, cellPadding=(-11, 3, -11, 3))
                starColorModeLabel = maputils.GetActiveStarColorModeLabel()
                if starColorModeLabel:
                    tooltipPanel.AddLabelMedium(text=starColorModeLabel, bold=True, colSpan=tooltipPanel.columns)
                if isinstance(particleHint, (list, tuple)):
                    for each in particleHint:
                        tooltipPanel.AddLabelSmall(text=each, state=uiconst.UI_NORMAL, colSpan=tooltipPanel.columns)

                else:
                    tooltipPanel.AddLabelSmall(text=particleHint, state=uiconst.UI_NORMAL, colSpan=tooltipPanel.columns)
        uthread.new(self.UpdateTooltipPosition, tooltipPanel)

    def UpdateTooltipPosition(self, tooltipPanel):
        while not tooltipPanel.destroyed:
            RefreshPanelPosition(tooltipPanel)
            blue.synchro.Yield()

    def CreateJumpLineSet(self, scene):
        lineSet = self.map.CreateCurvedLineSet(effectPath=mapcommon.LINESET_3D_EFFECT_STARMAP)
        transform = trinity.EveTransform()
        curveBinding = trinity.TriValueBinding()
        curveBinding.sourceObject = self.mapRoot.rotationCurve
        curveBinding.sourceAttribute = 'currentValue'
        curveBinding.destinationObject = transform
        curveBinding.destinationAttribute = 'rotation'
        curveSet = trinity.TriCurveSet()
        curveSet.bindings.append(curveBinding)
        scene.curveSets.append(curveSet)
        self.curveSet = curveSet
        curveSet.Play()
        transform.children.append(lineSet)
        scene.objects.append(transform)
        self.solarSystemJumpLineSet = lineSet

    def CreateScene(self):
        scene = trinity.EveSpaceScene()
        self.mapRoot = trinity.EveRootTransform()
        self.mapRoot.name = 'universe'
        self.mapRoot.display = True
        initialRotation = geo2.QuaternionRotationSetYawPitchRoll(*MAP_ROTATION)
        rotationCurve = trinity.Tr2CurveQuaternion()
        rotationCurve.AddKey(0, initialRotation)
        rotationCurve.AddKey(1, initialRotation)
        self.mapRoot.rotationCurve = trinity.Tr2RotationAdapter()
        self.mapRoot.rotationCurve.curve = rotationCurve
        scene.objects.append(self.mapRoot)
        return scene

    def CreateCamera(self):
        self.starmapCamera = camera = StarmapCamera()
        camera.idleMove = 0
        camera.friction = 10.0
        camera.translationFromParent = GetUserUiSetting('starmapTFP', 0.6 * ZOOM_MAX_STARMAP)
        if camera.translationFromParent < 0:
            camera.translationFromParent = -camera.translationFromParent
        if not self.IsFlat():
            camera.OrbitParent(0.0, 20.0)
        return camera

    def CreateLandmarkRoot(self):
        landmarkTF = trinity.EveTransform()
        landmarkTF.name = '__landmarkTF'
        self.mapRoot.children.append(landmarkTF)
        self.landmarkTF = landmarkTF

    def CreateLabelRoot(self):
        labeltrackersTF = trinity.EveTransform()
        labeltrackersTF.name = '__labeltrackersTF'
        self.mapRoot.children.append(labeltrackersTF)
        self.labeltrackersTF = labeltrackersTF

    def CreateLocalCameraParent(self):
        localCameraParent = trinity.EveTransform()
        localCameraParent.name = '__localCameraParent'
        self.mapRoot.children.append(localCameraParent)
        self.localCameraParent = localCameraParent

    def SetMapPerspective(self, camera):
        mapFlattened = GetUserUiSetting('mapFlattened', 1)
        if mapFlattened == 1:
            self.Flatten(initing=True)
            self.rollCamera = True
        else:
            camera.OrbitParent(0.0, 20.0)
            self.rollCamera = False

    @telemetry.ZONE_METHOD
    def InitMap(self):
        startTime = time.time()
        self.LogInfo('MapSvc: InitStarMap')
        initMapText = localization.GetByLabel('UI/Map/StarMap/InitializingMap')
        gettingDataText = localization.GetByLabel('UI/Map/StarMap/GettingData')
        self.StartLoadingBar('starmap_init', initMapText, gettingDataText, 4)
        scene = self.CreateScene()
        camera = self.CreateCamera()
        self.UpdateLoadingBar('starmap_init', initMapText, gettingDataText, 1, 4)
        self.CreateLandmarkRoot()
        self.CreateLabelRoot()
        self.CreateLocalCameraParent()
        self.CreateJumpLineSet(scene)
        self.CreateCursor()
        self.CreateHexmap()
        self.UpdateLoadingBar('starmap_init', initMapText, gettingDataText, 2, 4)
        self.DrawPoints(self.mapRoot)
        self.DrawSystemJumpLines()
        self.allianceJumpLines = []
        uthread.new(self.DrawAllJumpBridges)
        self.MakeRegionLabels()
        self.starLegend = []
        self.tileLegend = []
        if self.regionLabelParent:
            self.regionLabelParent.display = 0
        self.sceneManager.RegisterCamera(camera)
        self.sceneManager.RegisterScene(scene, 'starmap')
        self.SetMapPerspective(camera)
        self.RegisterStarColorModes()
        self.sceneManager.SetRegisteredScenes('starmap')
        self.sceneManager.SetSecondaryCamera(evecamera.CAM_STARMAP)
        self.UpdateLoadingBar('starmap_init', initMapText, gettingDataText, 3, 4)
        self.SetStarColorMode()
        self.UpdateLines(updateColor=1, hint='InitStarMap')
        self.UpdateRoute()
        self.CheckAllLabels('InitStarMap')
        self.UpdateHexMap()
        self.ShowWhereIAm()
        self.SetInterest(session.solarsystemid2)
        self.ShowCursorInterest(self.GetInterest().solarSystemID)
        self.OnCameraMoved()
        self.StopLoadingBar('starmap_init')
        self.LogInfo('Initializing the starmap took %f' % (time.time() - startTime))

    def GetStarPickRadius(self):
        range = ZOOM_MAX_STARMAP - ZOOM_MIN_STARMAP
        dist = self.starmapCamera.translationFromParent - ZOOM_MIN_STARMAP
        return PICK_RADIUS_NEAR + (PICK_RADIUS_FAR - PICK_RADIUS_NEAR) * (dist / range)

    def GetUICursor(self):
        return self.uicursor

    def ShowCursorInterest(self, solarsystemID, particleID = None):
        if solarsystemID and IsKnownSpaceSystem(solarsystemID):
            self.cursor.translation = self.GetKnownSolarSystem(solarsystemID).scaledCenter
            self.uicursor.solarsystemID = solarsystemID
            self.uicursor.particleID = particleID
            self.uicursor.display = True
            RefreshTooltipForOwner(self.uicursor.icon)
        elif self.uicursor:
            self.uicursor.solarsystemID = None
            self.uicursor.particleID = None
            self.uicursor.display = False

    def IsRegionLabelVisible(self, regionID, regionOfInterest, regionLabelSelection):
        if regionLabelSelection == SHOW_ALL_REGION_LABELS:
            return True
        if IsKnownSpaceRegion(regionOfInterest):
            if regionLabelSelection == SHOW_SELECTED_REGION_LABEL:
                return regionID == regionOfInterest
            if regionLabelSelection == SHOW_SELECTED_REGION_AND_NEIGHBOURS_LABELS:
                currentNeighbours = self.GetKnownRegion(regionOfInterest).neighbours
                return regionID == regionOfInterest or regionID in currentNeighbours
        return False

    @telemetry.ZONE_METHOD
    def CheckAllLabels(self, hint = ''):
        if getattr(self, 'checkingalllabels', 0) or self.mapRoot is None:
            return
        self.checkingalllabels = 1
        labelsToShow = []
        labelsToRemove = self.labels.keys()
        regionOfInterest, constellationOfInterest, systemOfInterest = self.GetInterest()
        showSolarSystemNames = GetUserUiSetting('label_solarsystem', 1)
        showConstellationNames = GetUserUiSetting('label_constellation', 1)
        regionLabelSelection = GetUserUiSetting('rlabel_region', 1)
        if regionLabelSelection == SHOW_NO_REGION_LABELS:
            if self.regionLabelParent:
                self.regionLabelParent.display = 0
        else:
            if self.regionLabelParent:
                self.regionLabelParent.display = 1
            if self.regionLabels:
                for regionID in self.GetKnownUniverseRegions():
                    showLabel = self.IsRegionLabelVisible(regionID, regionOfInterest, regionLabelSelection)
                    self.regionLabels[regionID].SetDisplay(showLabel)

        if GetUserUiSetting('label_landmarknames', 1):
            for landmarkID in self.map.GetLandmarks().iterkeys():
                labelsToShow.append(landmarkID * -1)

        if systemOfInterest is not None and IsKnownSpaceSystem(systemOfInterest):
            if showSolarSystemNames:
                labelsToShow += [systemOfInterest] + self.GetKnownSolarSystem(systemOfInterest).neighbours
            constellationID = self.GetKnownSolarSystem(systemOfInterest).constellationID
            if showConstellationNames and IsKnownSpaceConstellation(constellationID):
                labelsToShow.append(constellationID)
        elif constellationOfInterest is not None and IsKnownSpaceConstellation(constellationOfInterest):
            if showConstellationNames:
                labelsToShow += [constellationOfInterest] + self.GetKnownConstellation(constellationOfInterest).neighbours
            if showSolarSystemNames:
                labelsToShow += self.GetKnownConstellation(constellationOfInterest).solarSystemIDs
        elif showConstellationNames and IsKnownSpaceRegion(regionOfInterest):
            labelsToShow += self.GetKnownRegion(regionOfInterest).constellationIDs
        if showSolarSystemNames:
            for wayPointID in self.GetDestinationPath():
                if wayPointID not in labelsToShow and wayPointID is not None:
                    labelsToShow.append(wayPointID)

        if hasattr(self, 'focusLabel'):
            if self.focusLabel is not None and self.focusLabel not in labelsToShow:
                labelsToShow.append(self.focusLabel)
        new = [ x for x in labelsToShow if x not in labelsToRemove and not idCheckers.IsStation(x) ]
        old = [ x for x in labelsToRemove if x not in labelsToShow ]
        self.ClearLabels(old)
        self.CreateLabels(new)
        self.CheckLabelDist()
        self.checkingalllabels = 0

    def CheckLabelDist(self):
        if self.mapRoot is None:
            return
        uthread.new(self.CheckCloudLabels, 'checkLabelDist')

    @telemetry.ZONE_METHOD
    def OnCameraMoved(self):
        if self.IsFlat():
            self.distanceRangeStars.value = (0, 0, 0, 0)
            self.distanceRangeLines.value = (0, 0, 0, 0)
            return
        camera = self.sceneManager.GetRegisteredCamera(evecamera.CAM_STARMAP)
        if camera is None:
            return
        geoView = camera.viewMatrix.transform
        aabbMin = self.starParticles.aabbMin
        aabbMax = self.starParticles.aabbMax
        p = geo2.Vec3Transform(aabbMin, geoView)
        znear = zfar = geo2.Vec3Length(p)

        def Update(x, y, z, znear, zfar):
            p = geo2.Vec3Transform((x, y, z), geoView)
            dist = geo2.Vec3Length(p)
            return (min(znear, dist), max(zfar, dist))

        znear, zfar = Update(aabbMin[0], aabbMax[1], aabbMin[2], znear, zfar)
        znear, zfar = Update(aabbMin[0], aabbMin[1], aabbMax[2], znear, zfar)
        znear, zfar = Update(aabbMin[0], aabbMax[1], aabbMax[2], znear, zfar)
        znear, zfar = Update(aabbMax[0], aabbMin[1], aabbMin[2], znear, zfar)
        znear, zfar = Update(aabbMax[0], aabbMax[1], aabbMin[2], znear, zfar)
        znear, zfar = Update(aabbMax[0], aabbMin[1], aabbMax[2], znear, zfar)
        znear, zfar = Update(aabbMax[0], aabbMax[1], aabbMax[2], znear, zfar)
        znear = max(0, znear)
        if zfar <= znear:
            zfar = znear + 1
        self.distanceRangeStars.value = (znear,
         1.0 / (zfar - znear),
         0,
         0)
        self.distanceRangeLines.value = (znear,
         1.0 / (zfar - znear),
         0,
         0)

    @telemetry.ZONE_METHOD
    def CheckCloudLabels(self, reason = ''):
        if doingDebug == 1:
            self.LogInfo('checkloudlabels ', reason)
        if getattr(self, 'checkinglabels', 0):
            return
        setattr(self, 'checkinglabels', 1)
        sel = self.GetInterest()
        dst = self.GetDestination()
        for label in self.labels.itervalues():
            if label is not None and not label.destroyed:
                if len(label.children):
                    if label.sr.id in sel or label.sr.id == getattr(self, 'highlightLabel', -1) or label.sr.id == dst:
                        label.children[0].opacity = 1.0
                    else:
                        label.children[0].opacity = 0.7

        setattr(self, 'checkinglabels', 0)

    def GetStarData(self):
        return getattr(self, 'starData', {})

    def GetPickRay(self, x, y):
        dev = trinity.device
        proj, view, vp = uix.GetFullscreenProjectionViewAndViewport()
        ray, start = dev.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
        return utillib.KeyVal(normal=ray, startPos=start)

    @telemetry.ZONE_METHOD
    def TranslateCamera(self, x, y, dx, dy):
        self.interestEndPos = None
        camera = self.sceneManager.GetRegisteredCamera(evecamera.CAM_STARMAP)
        cameraParent = self.GetCameraParent()
        toRay = self.GetPickRay(x, y)
        fromRay = self.GetPickRay(x - dx, y - dy)
        pos = cameraParent.translation
        planePoint = pos
        pickPlane = geo2.PlaneFromPointNormal(planePoint, camera.viewVec)
        toPoint = geo2.PlaneIntersectLine(pickPlane, toRay.startPos, toRay.startPos + geo2.Vector(*toRay.normal) * 1000000.0)
        if toPoint is None:
            return
        fromPoint = geo2.PlaneIntersectLine(pickPlane, fromRay.startPos, fromRay.startPos + geo2.Vector(*fromRay.normal) * 1000000.0)
        if fromPoint is None:
            return
        offset = geo2.Vector(*fromPoint) - toPoint
        cameraParent.translation = geo2.Vec3Add(cameraParent.translation, offset)
        uthread.new(self.CheckLabelDist)

    def GetWorldPosFromLocalCoord(self, vector = None, flatten = True):
        pos = geo2.Vector(*(vector or self.localCameraParent.translation))
        if flatten and self.IsFlat():
            pos.y = 0.0
        curveQuat = self.mapRoot.rotationCurve.currentValue
        pos = geo2.QuaternionTransformVector(curveQuat, pos)
        return geo2.Vector(*pos)

    @telemetry.ZONE_METHOD
    def SetInterest(self, itemID = None, forceframe = None, forcezoom = None):
        if forceframe is None:
            forceframe = GetUserUiSetting('mapautoframe', 1)
        if forcezoom is None:
            forcezoom = GetUserUiSetting('mapautozoom', 0)
        self.LogInfo('Map Setinterest ', itemID)
        if doingDebug == 1:
            self.LogInfo('setinterest ', itemID, forceframe)
        if self.mapRoot is None:
            return
        dollyEndval = None
        camDuration = None
        interest = self.GetInterest()
        if not IsKnownSpaceSystem(itemID):
            itemID = DEFAULT_SOLAR_SYSTEM_ID
        itemID = itemID or interest.solarSystemID or interest.constellationID or interest.regionID or session.regionid
        endPos = self.GetWorldPosFromLocalCoord(flatten=True)
        self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
        if itemID is None:
            return
        if itemID == const.locationUniverse:
            dollyEndval = 20000.0
        elif itemID < 0:
            lm = self.map.GetLandmark(itemID * -1)
            scaledCenter = geo2.Scale(geo2.Vector(*lm.position), STARMAP_SCALE)
            self.localCameraParent.translation = scaledCenter
            endPos = self.GetWorldPosFromLocalCoord(flatten=True)
            self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
        else:
            self.UpdateLines(itemID, hint='SetInterest')
            scaledCenter = (0.0, 0.0, 0.0)
            if idCheckers.IsSolarSystem(itemID):
                system = self.GetKnownSolarSystem(itemID)
                scaledCenter = system.scaledCenter
                self.interest = StarmapInterest(system.regionID, system.constellationID, itemID)
            elif idCheckers.IsConstellation(itemID):
                constellation = self.GetKnownConstellation(itemID)
                scaledCenter = constellation.scaledCenter
                self.interest = StarmapInterest(constellation.regionID, itemID, None)
            elif idCheckers.IsRegion(itemID) and self.regionLabels:
                scaledCenter = self.GetKnownRegion(itemID).scaledCenter
                self.interest = StarmapInterest(itemID, None, None)
                for regionID in self.knownRegions:
                    self.regionLabels[regionID].SetHighlight(False)

                if IsKnownSpaceRegion(itemID):
                    self.regionLabels[itemID].SetHighlight(True)
            scaledCenter = geo2.Vector(scaledCenter[0], 0.0 if self.IsFlat() else scaledCenter[1], scaledCenter[2])
            camera = self.sceneManager.GetRegisteredCamera(evecamera.CAM_STARMAP)
            dollyEndval = camera.translationFromParent
            if forceframe and forcezoom:
                if idCheckers.IsSolarSystem(itemID):
                    dollyEndval = ZOOM_MIN_STARMAP + (ZOOM_MAX_STARMAP - ZOOM_MIN_STARMAP) * 0.05
                else:
                    item = self.map.GetItem(itemID)
                    mx = abs(item.xMin) + item.xMax
                    my = abs(item.yMin) + item.yMax
                    mz = abs(item.zMin) + item.zMax
                    size = geo2.Scale(geo2.Vector(mx, my, mz), STARMAP_SCALE)
                    radius = max(*size) * 0.5
                    camangle = camera.fieldOfView * 0.5
                    dollyEndval = radius / sin(camangle) * cos(camangle)
            self.localCameraParent.translation = scaledCenter
            endPos = self.GetWorldPosFromLocalCoord()
            self.interestEndPos = self.GetWorldPosFromLocalCoord(flatten=False)
            cameraParent = self.GetCameraParent()
            mapPos = geo2.Vector(*cameraParent.translation)
            camDuration = max(0.25, min(1.0, geo2.Vec3Length(endPos - mapPos) * 1e-05))
        if self.mapRoot is None:
            return
        if forceframe:
            uthread.new(self.MoveInterest, endPos, (camDuration or 0.2) * 1000.0)
            if forcezoom and dollyEndval is not None:
                self.Dolly(dollyEndval, camDuration or 0.2)
        self.CheckAllLabels('SetInterest')
        self.UpdateLines()

    @telemetry.ZONE_METHOD
    def MoveInterest(self, posEnd, time = 500.0):
        uicore.desktop.state = uiconst.UI_DISABLED
        count = 50
        while getattr(self, 'moving', False) and count:
            blue.pyos.synchro.SleepWallclock(100)
            count -= 1

        try:
            self.moving = True
            cameraParent = self.GetCameraParent()
            startPos = cameraParent.translation
            posBegin = geo2.Vector(*startPos)
            start = blue.os.GetWallclockTime()
            ndt = 0.0
            while ndt != 1.0:
                ndt = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / time, 1.0))
                if posBegin and posEnd:
                    pos = geo2.Vec3Lerp(posBegin, posEnd, ndt)
                    cameraParent.translation = pos
                blue.pyos.synchro.Yield()

        except AttributeError:
            pass
        finally:
            uicore.desktop.state = uiconst.UI_NORMAL
            self.moving = False

    def Dolly(self, end, length = 2.0):
        camera = self.sceneManager.GetRegisteredCamera(evecamera.CAM_STARMAP)
        beg = camera.translationFromParent
        end = camera.CheckTranslationFromParent(end)
        camera.PanCamera(beg, end, time=length, source='starmap')
        self.CheckLabelDist()

    @telemetry.ZONE_METHOD
    def MakeRegionLabels(self):
        self.LogInfo('MakeRegionLabels')
        regionLabelParent = trinity.EveTransform()
        regionLabelParent.display = 0
        self.mapRoot.children.append(regionLabelParent)
        regionLabelParent.name = '__regionLabels'
        self.regionLabels = {}
        for regionID, regionItem in self.GetKnownUniverseRegions().iteritems():
            regionName = StripTags(cfg.evelocations.Get(regionID).name, stripOnly=['localized'])
            label = TransformableLabel(regionName, regionLabelParent, size=127)
            label.transform.translation = regionItem.scaledCenter
            label.transform.scaling = geo2.Scale(geo2.Vector(*label.transform.scaling), REGION_LABEL_SCALE)
            label.SetDisplay(False)
            self.regionLabels[regionID] = label

        self.regionLabelParent = regionLabelParent

    def DrawRouteTo(self, targetID, verbose = 1, sourceID = None):
        self.LogInfo('DrawRouteTo ', targetID)
        if targetID == session.solarsystemid2:
            self.ClearRoute('genericRoute')
            return
        if targetID in [session.solarsystemid2, session.constellationid, session.regionid]:
            return []
        targetName = cfg.evelocations.Get(targetID).name
        routeList = self.ShortestGeneralPath(targetID, sourceID=sourceID)
        self.ClearRoute('genericRoute')
        route = MapRoute()
        route.DrawRoute(routeList, flattened=self.flattened, rotationQuaternion=self.GetCurrentStarmapRotation())
        self.genericRoute = route
        scene = self.sceneManager.GetRegisteredScene('starmap')
        scene.objects.append(route.model)
        if not len(routeList):
            if self.viewState.IsViewActive('starmap'):
                if verbose == 1:
                    eve.Message('Command', {'command': localization.GetByLabel('UI/Map/StarMap/NoPathFoundTo', targetItem=targetName)})
            return []
        self.CheckAllLabels('DrawRouteTo')
        if self.viewState.IsViewActive('starmap'):
            if verbose == 1:
                jumps = len(routeList) - 1
                routeType = self.clientPathfinderService.GetAutopilotRouteType()
                if sourceID:
                    sourceItemName = cfg.evelocations.Get(sourceID).name
                    if routeType == ROUTE_TYPE_SHORTEST:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheShortestRouteFromToTakesRegionJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheShortestRouteFromToTakesJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                    elif routeType == ROUTE_TYPE_SAFE:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheSafestRouteFromToTakesRegionJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheSafestRouteFromToTakesJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                    elif routeType == ROUTE_TYPE_UNSAFE:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheUnSafestRouteFromToTakesRegionJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheUnSafestRouteFromToTakesJumps', sourceItem=sourceItemName, targetItem=targetName, jumps=jumps)
                    else:
                        labelText = localization.GetByLabel('UI/Map/StarMap/NoKnownRouteFromTo')
                    eve.Message('Command', {'command': labelText})
                else:
                    if routeType == ROUTE_TYPE_SHORTEST:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheShortestRouteToTakesRegionJumps', targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheShortestRouteToTakesJumps', targetItem=targetName, jumps=jumps)
                    elif routeType == ROUTE_TYPE_SAFE:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheSafestRouteToTakesRegionJumps', targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheSafestRouteToTakesJumps', targetItem=targetName, jumps=jumps)
                    elif routeType == ROUTE_TYPE_UNSAFE:
                        if idCheckers.IsRegion(targetID):
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheUnSafestRouteToTakesJumps', targetItem=targetName, jumps=jumps)
                        else:
                            labelText = localization.GetByLabel('UI/Map/StarMap/TheUnSafestRouteToTakesRegionJumps', targetItem=targetName, jumps=jumps)
                    else:
                        labelText = localization.GetByLabel('UI/Map/StarMap/NoKnownRouteTo')
                    eve.Message('Command', {'command': labelText})
        self.genericRoutePath = routeList
        self.UpdateLines(updateColor=1)
        return routeList

    def RemoveGenericPath(self):
        self.genericRoutePath = None
        self.ClearRoute('genericRoute')
        self.UpdateLines(updateColor=True)

    def ClearRoute(self, routeName = 'autoPilotRoute'):
        route = getattr(self, routeName, None)
        if route:
            scene = self.sceneManager.GetRegisteredScene('starmap')
            if route.model in scene.objects:
                scene.objects.fremove(route.model)
            setattr(self, routeName, None)

    def ShortestGeneralPath(self, targetID, sourceID = None):
        if sourceID is None:
            sourceID = session.solarsystemid2
        if idCheckers.IsConstellation(targetID):
            targets = self.map.GetLocationChildren(targetID)
        elif idCheckers.IsRegion(targetID):
            targets = []
            for constellationID in self.map.GetLocationChildren(targetID):
                targets.extend(self.map.GetLocationChildren(constellationID))

        else:
            targets = [targetID]
        paths = []
        for target in targets:
            routeList = self.clientPathfinderService.GetAutopilotPathBetween(sourceID, target)
            if routeList:
                paths.append(routeList)

        if not len(paths):
            return []
        return min(paths, key=lambda p: len(p))

    def GetAllFactions(self):
        return list(cfg.mapFactionsOwningSolarSystems)

    def GetAllianceSolarSystems(self):
        self.allianceSolarSystems = {}
        allianceSystemCache = sm.RemoteSvc('stationSvc').GetAllianceSystems()
        for x in allianceSystemCache:
            self.allianceSolarSystems[x.solarSystemID] = x.allianceID

        occupationStatesBySolarsystemByWarzone = sm.GetService('fwWarzoneSvc').GetAllOccupationStates()
        for occupationStatesBySolarsystem in occupationStatesBySolarsystemByWarzone.itervalues():
            for solarsystemID, occupationState in occupationStatesBySolarsystem.iteritems():
                self.allianceSolarSystems[solarsystemID] = occupationState.occupierID

        return self.allianceSolarSystems

    def GetAllFactionsAndAlliances(self):
        factions = self.GetAllFactions()
        alliances = self.GetAllianceSolarSystems().values()
        return list(set(factions + alliances))

    def GetDestination(self):
        if self.destinationPath != [None]:
            return self.destinationPath[-1]

    def GetDestinationPath(self):
        if not len(self.destinationPath):
            return [None]
        return self.destinationPath[:]

    def GetFactionOrAllianceColor(self, entityID):
        if not hasattr(self, 'factionOrAllianceColors'):
            self.factionOrAllianceColors = {}
        if entityID not in self.factionOrAllianceColors:
            col = trinity.TriColor()
            hue = entityID * 12.345 * 3.0
            s = entityID % 2 * 0.5 + 0.5
            col.SetHSV(hue % 360.0, s, 1.0)
            self.factionOrAllianceColors[entityID] = col
        return self.factionOrAllianceColors[entityID]

    def GetLineIDForJumpBetweenSystems(self, fromSystemID, toSystemID):
        for lineID, _toSystemID in self.lineIdAndToSystemIdByFromSystemId[fromSystemID]:
            if _toSystemID == toSystemID:
                return lineID
        else:
            raise RuntimeError("Did not find a lineID for a jump between '%s' and '%s'" % (self.map.GetItem(fromSystemID).itemName, self.map.GetItem(toSystemID).itemName))

    def GetLineIDsForSystemID(self, sysID):
        return [ i[0] for i in self.lineIdAndToSystemIdByFromSystemId[sysID] ]

    def GetLineIDsForSystemList(self, solarSystemIDs):
        result = []
        for solarSystemID in solarSystemIDs:
            result.extend(self.GetLineIDsForSystemID(solarSystemID))

        return result

    @telemetry.ZONE_METHOD
    def DrawSystemJumpLines(self):
        self.jumpLineInfoByLineID = {}
        self.lineIdAndToSystemIdByFromSystemId = defaultdict(list)
        self.curvedLineInfoByLineID = {}
        lineSet = self.solarSystemJumpLineSet
        self.jumpLineIDsByJumpType = [[], [], []]
        for jump in self.IterateJumps():
            jumpColor = JUMP_COLORS[jump.jumpType]
            lineID = lineSet.AddStraightLine(jump.adjustedFromVector, jumpColor, jump.adjustedToVector, jumpColor, 2)
            jumpToSystemID = jump.toSystemID
            jumpFromSystemID = jump.fromSystemID
            jumpLineInfo = utillib.KeyVal(lineID=lineID, toID=jumpToSystemID, toPos=jump.adjustedToVector, toColor=jumpColor, fromID=jumpFromSystemID, fromPos=jump.adjustedFromVector, fromColor=jumpColor)
            self.jumpLineIDsByJumpType[jump.jumpType].append(lineID)
            self.jumpLineInfoByLineID[lineID] = jumpLineInfo
            self.currentLineColour[lineID] = (jumpColor, jumpColor)
            self.lineIdAndToSystemIdByFromSystemId[jumpFromSystemID].append((lineID, jumpToSystemID))
            self.lineIdAndToSystemIdByFromSystemId[jumpToSystemID].append((lineID, jumpFromSystemID))

        lineSet.SubmitChanges()

    def DrawAllJumpBridges(self):
        self.allJumpBridges = []
        self.myJumpBridges = []
        jumpBridgesGates, hasAccessTo, hasNoAccessTo = sm.GetService('map').GetJumpBridgesWithMyAccess()
        jumpBridgeColorAccess = ScaleColour(mapcommon.JUMPBRIDGE_COLOR, mapcommon.JUMPBRIDGE_COLOR_SCALE)
        jumpBridgeColorNoAccess = ScaleColour(mapcommon.JUMPBRIDGE_COLOR_NO_ACCESS, mapcommon.JUMPBRIDGE_COLOR_SCALE)
        lineSet = self.solarSystemJumpLineSet
        for structureA, structureB in jumpBridgesGates:
            solarSystemA = structureA.solarSystemID
            solarSystemB = structureB.solarSystemID
            if not idCheckers.IsSolarSystem(solarSystemA) or not idCheckers.IsSolarSystem(solarSystemB):
                self.LogWarn("DrawAllJumpBridges had entry that wasn't a solarsystem:", solarSystemA, solarSystemB)
                continue
            toPos = self.GetKnownSolarSystem(solarSystemA).scaledCenter
            fromPos = self.GetKnownSolarSystem(solarSystemB).scaledCenter
            worldUp = geo2.Vector(0.0, 1.0, 0.0)
            linkVec = geo2.Vec3Subtract(toPos, fromPos)
            normLinkVec = geo2.Vec3Normalize(linkVec)
            rightVec = geo2.Vec3Cross(worldUp, normLinkVec)
            upVec = geo2.Vec3Cross(rightVec, normLinkVec)
            offsetVec = geo2.Vec3Scale(geo2.Vec3Normalize(upVec), geo2.Vec3Length(linkVec) * mapcommon.JUMPBRIDGE_CURVE_SCALE)
            midPos = geo2.Vec3Scale(geo2.Vec3Add(toPos, fromPos), 0.5)
            splinePos = geo2.Vec3Add(midPos, offsetVec)
            hasAccessToA = structureA.structureID in hasAccessTo
            hasAccessToB = structureB.structureID in hasAccessTo
            colorA = jumpBridgeColorAccess if hasAccessToA else jumpBridgeColorNoAccess
            colorB = jumpBridgeColorAccess if hasAccessToB else jumpBridgeColorNoAccess
            animationColor = jumpBridgeColorAccess if hasAccessToA or hasAccessToB else jumpBridgeColorNoAccess
            lineID = lineSet.AddCurvedLineCrt(toPos, colorA, fromPos, colorB, splinePos, 2)
            lineSet.ChangeLineAnimation(lineID, animationColor, mapcommon.JUMPBRIDGE_ANIMATION_SPEED, 1)
            info = utillib.KeyVal(lineID=lineID, toID=solarSystemA, toPos=toPos, toColor=colorA, fromID=solarSystemB, fromPos=fromPos, fromColor=colorB)
            if settings.char.ui.Get('pathFinder_includeJumpGates', False):
                self.lineIdAndToSystemIdByFromSystemId[solarSystemB].append((lineID, solarSystemA))
                self.lineIdAndToSystemIdByFromSystemId[solarSystemA].append((lineID, solarSystemB))
            self.allJumpBridges.append(lineID)
            if hasAccessToA or hasAccessToB:
                self.myJumpBridges.append(lineID)
            self.currentLineColour[lineID] = (colorA, colorB)
            self.jumpLineInfoByLineID[lineID] = info
            self.curvedLineInfoByLineID[lineID] = (midPos, offsetVec)

        lineSet.SubmitChanges()

    def GetHiliteItem(self, hiliteID):
        hiliteItem = None
        if idCheckers.IsSolarSystem(hiliteID) and IsKnownSpaceSystem(hiliteID):
            hiliteItem = self.GetKnownSolarSystem(hiliteID)
        elif idCheckers.IsConstellation(hiliteID) and IsKnownSpaceConstellation(hiliteID):
            hiliteItem = self.GetKnownConstellation(hiliteID)
        elif idCheckers.IsRegion(hiliteID) and IsKnownSpaceRegion(hiliteID):
            hiliteItem = self.GetKnownRegion(hiliteID)
        return hiliteItem

    @telemetry.ZONE_METHOD
    def UpdateLines(self, hiliteID = None, updateColor = False, showlines = None, hint = '', path = None):
        if not sm.GetService('viewState').IsViewActive('starmap'):
            return
        if showlines is None:
            showlines = GetUserUiSetting('showlines', SHOW_ALL)
        interest = self.GetInterest()
        if showlines == SHOW_NONE:
            self.SetJumpLineAlpha(0.0)
        else:
            if hiliteID is None:
                hiliteID = interest.solarSystemID or interest.constellationID or interest.regionID
            if showlines == SHOW_ALL:
                self.SetJumpLineAlpha(0.5)
            else:
                self.SetJumpLineAlpha(0.0)
                if showlines > SHOW_SELECTION and IsKnownSpaceRegion(interest.regionID):
                    regionsToShow = [interest.regionID]
                    if showlines == SHOW_NEIGHBORS:
                        regionsToShow = regionsToShow + self.GetKnownRegion(interest.regionID).neighbours
                    self.SetJumpLineAlpha(0.0)
                    regionIDs = self.map.ExpandItems(regionsToShow)
                    lineIDs = self.GetLineIDsForSystemList(regionIDs)
                    self.SetJumpLineAlpha(0.5, lineIDs)
            if idCheckers.IsSolarSystem(hiliteID) and IsKnownSpaceSystem(hiliteID):
                lineIDs = self.GetLineIDsForSystemID(hiliteID)
                self.SetJumpLineAlpha(1.0, lineIDs)
                lineIDs = self.GetLineIDsForSystemList(self.GetHiliteItem(hiliteID).neighbours)
                self.SetJumpLineAlpha(0.6, lineIDs)
            elif idCheckers.IsConstellation(hiliteID) and IsKnownSpaceConstellation(hiliteID):
                lineIDs = self.GetLineIDsForSystemList(self.GetHiliteItem(hiliteID).solarSystemIDs)
                self.SetJumpLineAlpha(1.0, lineIDs)
            elif idCheckers.IsRegion(hiliteID) and IsKnownSpaceRegion(hiliteID):
                lineIDs = self.GetLineIDsForSystemList(self.GetHiliteItem(hiliteID).solarSystemIDs)
                self.SetJumpLineAlpha(1.0, lineIDs)
        if updateColor:
            self.UpdateLineColor()
        showAllianceLines = GetUserUiSetting('map_alliance_jump_lines', 1)
        self.SetJumpLineAlpha(1.0 if showAllianceLines else 0.0, self.allianceJumpLines)
        showJumpBridges = GetUserUiSetting('showJumpBridges', 0)
        if showJumpBridges == 1:
            self.SetJumpLineAlpha(1.0, self.allJumpBridges)
        else:
            toHide = set(self.allJumpBridges) - set(self.myJumpBridges)
            self.SetJumpLineAlpha(0.0, toHide)
            self.SetJumpLineAlpha(1.0, self.myJumpBridges)
        if path:
            self.ShowPath(path)
        if self.genericRoutePath:
            self.ShowPath(self.genericRoutePath)
        self.ShowDestinationPath()
        self.solarSystemJumpLineSet.SubmitChanges()

    @telemetry.ZONE_METHOD
    def SetJumpLineAlpha(self, alpha, lineIDs = None):
        lineSet = self.solarSystemJumpLineSet
        if lineIDs is None:
            lineIDs = self.jumpLineInfoByLineID.iterkeys()
        for lineID in lineIDs:
            fromColor, toColor = self.currentLineColour[lineID]
            self.ChangeLineColor(lineSet, lineID, OverrideAlpha(fromColor, alpha), OverrideAlpha(toColor, alpha))

    @telemetry.ZONE_METHOD
    def ChangeLineColor(self, lineSet, lineID, fromColor, toColor):
        if lineID in self.allianceJumpLines:
            overlayColor = fromColor
            lineSet.ChangeLineAnimation(lineID, overlayColor, mapcommon.JUMPBRIDGE_ANIMATION_SPEED, 1)
        oldFromColor, oldToColor = self.currentLineColour[lineID]
        newFromColor = OverrideColour(oldFromColor, fromColor)
        newToColor = OverrideColour(oldToColor, toColor)
        self.currentLineColour[lineID] = (newFromColor, newToColor)
        lineSet.ChangeLineColor(lineID, newFromColor, newToColor)

    @telemetry.ZONE_METHOD
    def SetJumpLineColor(self, color, lineIDs = None):
        lineSet = self.solarSystemJumpLineSet
        if lineIDs is None:
            lineIDs = self.jumpLineInfoByLineID.iterkeys()
        for lineID in lineIDs:
            self.ChangeLineColor(lineSet, lineID, color, color)

    @telemetry.ZONE_METHOD
    def SetJumpLineColors(self, lineIDs, fromColor, toColor):
        lineSet = self.solarSystemJumpLineSet
        for lineID in lineIDs:
            self.ChangeLineColor(lineSet, lineID, fromColor, toColor)

    @telemetry.ZONE_METHOD
    def SetJumpLineColorAt(self, lineID, atID, color):
        lineSet = self.solarSystemJumpLineSet
        fromColor, toColor = self.currentLineColour[lineID]
        if atID == info.fromID:
            fromColor = OverrideColour(fromColor, color)
        else:
            toColor = OverrideColour(toColor, color)
        self.ChangeLineColor(lineSet, lineID, fromColor, toColor)

    @telemetry.ZONE_METHOD
    def SetJumpLineAlphaAt(self, lineID, atID, alpha):
        lineSet = self.solarSystemJumpLineSet
        fromColor, toColor = self.currentLineColour[lineID]
        if atID == info.fromID:
            fromColor = OverrideAlpha(fromColor, alpha)
        else:
            toColor = OverrideAlpha(toColor, alpha)
        self.ChangeLineColor(lineSet, lineID, fromColor, toColor)

    @telemetry.ZONE_METHOD
    def SetStarParticleAlpha(self, alpha, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleItemsIterator = enumerate(self.particleColors)
        else:
            particleItemsIterator = SelectiveIndexedIterItems(self.particleColors, particleIDs)
        for key, color in particleItemsIterator:
            particleSystem.SetItemElement(key, 2, OverrideAlpha(color, alpha))

    @telemetry.ZONE_METHOD
    def SetStarParticleColor(self, newColor, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleItemsIterator = enumerate(self.particleColors)
        else:
            particleItemsIterator = SelectiveIndexedIterItems(self.particleColors, particleIDs)
        for key, originalColor in particleItemsIterator:
            c = OverrideColour(originalColor, newColor)
            particleSystem.SetItemElement(key, 2, c)

    @telemetry.ZONE_METHOD
    def SetStarParticleSize(self, size, particleIDs = None):
        particleSystem = self.starParticles
        if particleIDs is None:
            particleIDs = xrange(len(self.particleColors))
        for id in particleIDs:
            particleSystem.SetItemElement(id, 1, size)

    @telemetry.ZONE_METHOD
    def UpdateLineColor(self):
        colorMode = GetUserUiSetting('mapcolorby', mapcommon.COLORMODE_UNIFORM)
        if colorMode == mapcommon.COLORMODE_UNIFORM:
            for jumpType in JUMP_TYPES:
                lineIDs = self.jumpLineIDsByJumpType[jumpType]
                self.SetJumpLineColor(JUMP_COLORS[jumpType][:3], lineIDs)

            self.SetJumpLineColor(ScaleColour(mapcommon.JUMPBRIDGE_COLOR, mapcommon.JUMPBRIDGE_COLOR_SCALE), self.allianceJumpLines)
        elif colorMode == mapcommon.COLORMODE_REGION:
            if not hasattr(self, 'regionJumpColorList'):
                self.regionJumpColorList = []
                for info in self.jumpLineInfoByLineID.itervalues():
                    fromRegionID = self.GetKnownSolarSystem(info.fromID).regionID
                    toRegionID = self.GetKnownSolarSystem(info.toID).regionID
                    fromColor = self.GetRegionColor(fromRegionID)
                    toColor = self.GetRegionColor(toRegionID)
                    self.regionJumpColorList.append(([info.lineID], (fromColor.r, fromColor.g, fromColor.b), (toColor.r, toColor.g, toColor.b)))

            for lineID, formColor, toColor in self.regionJumpColorList:
                self.SetJumpLineColors(lineID, formColor, toColor)

        elif colorMode == mapcommon.COLORMODE_STANDINGS:
            colorByFaction = {}
            for factionID in self.GetAllFactionsAndAlliances():
                colorByFaction[factionID] = self.GetColorByStandings(factionID)

            allianceSolarSystems = self.GetAllianceSolarSystems()
            for info in self.jumpLineInfoByLineID.itervalues():
                fromColor = colorByFaction.get(self._GetFactionIDFromSolarSystem(allianceSolarSystems, info.fromID), mapcommon.COLOR_STANDINGS_NEUTRAL)
                toColor = colorByFaction.get(self._GetFactionIDFromSolarSystem(allianceSolarSystems, info.toID), mapcommon.COLOR_STANDINGS_NEUTRAL)
                self.SetJumpLineColors([info.lineID], fromColor, toColor)

    @telemetry.ZONE_METHOD
    def GetColorByStandings(self, factionID):
        if factionID == session.allianceid:
            return mapcommon.COLOR_STANDINGS_GOOD
        standingSvc = sm.GetService('standing')
        standings = [standingSvc.GetStanding(session.charid, factionID) or 0, standingSvc.GetStanding(session.corpid, factionID) or 0, standingSvc.GetStanding(session.allianceid, factionID) or 0]
        standings = [ s for s in standings if s != 0 ]
        standing = 0 if len(standings) == 0 else max(standings)
        if standing == 0:
            color = mapcommon.COLOR_STANDINGS_NEUTRAL
        elif standing > 0:
            color = mapcommon.COLOR_STANDINGS_GOOD
        else:
            color = mapcommon.COLOR_STANDINGS_BAD
        return color

    def _GetFactionIDFromSolarSystem(self, allianceSolarSystems, solarSystemID):
        if solarSystemID in allianceSolarSystems:
            return allianceSolarSystems[solarSystemID]
        else:
            return self.GetKnownSolarSystem(solarSystemID).factionID

    def ShowPath(self, path):
        if path:
            linesToHighlight = []
            for fromID, toID in Pairwise(path):
                linesToHighlight.append(self.GetLineIDForJumpBetweenSystems(fromID, toID))

            self.SetJumpLineColor((1.0, 0.5, 0.0, 0.8), linesToHighlight)

    def SetColourGradientToLineBetweenSystems(self, fromID, toID, fromColor, toColor):
        lineSet = self.solarSystemJumpLineSet
        lineSetID = self.GetLineIDForJumpBetweenSystems(fromID, toID)
        jumpInfo = self.jumpLineInfoByLineID[lineSetID]
        if fromID == jumpInfo.fromID:
            self.ChangeLineColor(lineSet, lineSetID, fromColor, toColor)
        else:
            self.ChangeLineColor(lineSet, lineSetID, toColor, fromColor)

    @telemetry.ZONE_METHOD
    def ShowDestinationPath(self):

        def GetSystemColorBasedOnSecRating(ssID):
            c = self.map.GetModifiedSystemColor(ssID)
            return (c[0],
             c[1],
             c[2],
             1.0)

        if self.destinationPath[0] is not None:
            destPath = [ locationID for locationID in self.destinationPath if idCheckers.IsSolarSystem(locationID) ]
            if len(destPath) == 0:
                return
            if destPath[0] != session.solarsystemid2 and IsKnownSpaceSystem(session.solarsystemid2):
                destPath = [session.solarsystemid2] + destPath
            for fromID, toID in Pairwise(destPath):
                if fromID == toID:
                    continue
                self.SetColourGradientToLineBetweenSystems(fromID, toID, GetSystemColorBasedOnSecRating(fromID), GetSystemColorBasedOnSecRating(toID))

    @telemetry.ZONE_METHOD
    def HighlightNeighborStars(self, solarSystemID = None):
        interest = self.GetInterest()
        if solarSystemID is None:
            solarSystemID = interest.solarSystemID
        self.SetStarParticleAlpha(0.5)
        self.SetStarParticleAlpha(1.0, [self.solarSystemIDToParticleID[solarSystemID]])
        systemsByDistance = self.clientPathfinderService.GetSystemsWithinJumpRange(solarSystemID, 1, 3)
        for distance, systemIDs in systemsByDistance.iteritems():
            if distance == 1:
                alpha = 0.8
            else:
                alpha = 0.7
            pointIDs = [ self.solarSystemIDToParticleID[systemID] for systemID in systemIDs ]
            self.SetStarParticleAlpha(alpha, pointIDs)

        self.starParticles.UpdateData()

    def RegisterStarColorModes(self):
        self.starColorHandlers = {mapcommon.STARMODE_ASSETS: (localization.GetByLabel('UI/Map/StarMap/ShowAssets'), starModeHandler.ColorStarsByAssets),
         mapcommon.STARMODE_VISITED: (localization.GetByLabel('UI/Map/StarMap/ShowSystemsVisited'), starModeHandler.ColorStarsByVisited),
         mapcommon.STARMODE_SECURITY: (localization.GetByLabel('UI/Map/StarMap/SecurityStatus'), starModeHandler.ColorStarsBySecurity),
         mapcommon.STARMODE_INDEX_STRATEGIC: (localization.GetByLabel('UI/Map/StarMap/Strategic'),
                                              starModeHandler.ColorStarsByDevIndex,
                                              const.attributeDevIndexSovereignty,
                                              localization.GetByLabel('UI/Map/StarMap/Strategic')),
         mapcommon.STARMODE_INDEX_MILITARY: (localization.GetByLabel('UI/Map/StarMap/Military'),
                                             starModeHandler.ColorStarsByDevIndex,
                                             const.attributeDevIndexMilitary,
                                             localization.GetByLabel('UI/Map/StarMap/Military')),
         mapcommon.STARMODE_INDEX_INDUSTRY: (localization.GetByLabel('UI/Map/StarMap/Industry'),
                                             starModeHandler.ColorStarsByDevIndex,
                                             const.attributeDevIndexIndustrial,
                                             localization.GetByLabel('UI/Map/StarMap/Industry')),
         mapcommon.STARMODE_SOV_CHANGE: (localization.GetByLabel('UI/Map/StarMap/RecentSovereigntyChanges'), starModeHandler.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_ALL),
         mapcommon.STARMODE_SOV_GAIN: (localization.GetByLabel('UI/Map/StarMap/SovereigntyGain'), starModeHandler.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_SOV_GAIN),
         mapcommon.STARMODE_SOV_LOSS: (localization.GetByLabel('UI/Map/StarMap/SovereigntyLoss'), starModeHandler.ColorStarsBySovChanges, mapcommon.SOV_CHANGES_SOV_LOST),
         mapcommon.STARMODE_SOV_STANDINGS: (localization.GetByLabel('UI/Map/StarMap/Standings'), starModeHandler.ColorStarsByFactionStandings),
         mapcommon.STARMODE_FACTION: (localization.GetByLabel('UI/Map/StarMap/SovereigntyMap'), starModeHandler.ColorStarsByFaction),
         mapcommon.STARMODE_FACTIONEMPIRE: (localization.GetByLabel('UI/Map/StarMap/SovereigntyMap'), starModeHandler.ColorStarsByFaction),
         mapcommon.STARMODE_MILITIA: (localization.GetByLabel('UI/Map/StarMap/FactionalWarfare'), starModeHandler.ColorStarsByMilitia),
         mapcommon.STARMODE_REGION: (localization.GetByLabel('UI/Map/StarMap/ColorStarsByRegion'), starModeHandler.ColorStarsByRegion),
         mapcommon.STARMODE_CARGOILLEGALITY: (localization.GetByLabel('UI/Map/StarMap/MyCargoIllegality'), starModeHandler.ColorStarsByCargoIllegality),
         mapcommon.STARMODE_PLAYERCOUNT: (localization.GetByLabel('UI/Map/StarMap/ShowPilotsInSpace'), starModeHandler.ColorStarsByNumPilots),
         mapcommon.STARMODE_PLAYERDOCKED: (localization.GetByLabel('UI/Map/StarMap/ShowPilotsDocked'), starModeHandler.ColorStarsByNumPilots),
         mapcommon.STARMODE_STATIONCOUNT: (localization.GetByLabel('UI/Map/StarMap/ShowStationCount'), starModeHandler.ColorStarsByStationCount),
         mapcommon.STARMODE_DUNGEONS: (localization.GetByLabel('UI/Map/StarMap/ShowDeadspaceComplexes'), starModeHandler.ColorStarsByDungeons),
         mapcommon.STARMODE_DUNGEONSAGENTS: (localization.GetByLabel('UI/Map/StarMap/ShowAgentSites'), starModeHandler.ColorStarsByDungeons),
         mapcommon.STARMODE_JUMPS1HR: (localization.GetByLabel('UI/Map/StarMap/ShowRecentJumps'), starModeHandler.ColorStarsByJumps1Hour),
         mapcommon.STARMODE_SHIPKILLS1HR: (localization.GetByLabel('UI/Map/StarMap/ShowShipsDestroyed'),
                                           starModeHandler.ColorStarsByKills,
                                           const.mapHistoryStatKills,
                                           1),
         mapcommon.STARMODE_SHIPKILLS24HR: (localization.GetByLabel('UI/Map/StarMap/ShowShipsDestroyed'),
                                            starModeHandler.ColorStarsByKills,
                                            const.mapHistoryStatKills,
                                            24),
         mapcommon.STARMODE_MILITIAKILLS1HR: (localization.GetByLabel('UI/Map/StarMap/ShowMilitiaShipsDestroyed'),
                                              starModeHandler.ColorStarsByKills,
                                              const.mapHistoryStatFacWarKills,
                                              1),
         mapcommon.STARMODE_MILITIAKILLS24HR: (localization.GetByLabel('UI/Map/StarMap/ShowMilitiaShipsDestroyed'),
                                               starModeHandler.ColorStarsByKills,
                                               const.mapHistoryStatFacWarKills,
                                               24),
         mapcommon.STARMODE_PODKILLS1HR: (localization.GetByLabel('UI/Map/StarMap/ShowMilitiaShipsDestroyed'), starModeHandler.ColorStarsByPodKills),
         mapcommon.STARMODE_PODKILLS24HR: (localization.GetByLabel('UI/Map/StarMap/ShowMilitiaShipsDestroyed'), starModeHandler.ColorStarsByPodKills),
         mapcommon.STARMODE_FACTIONKILLS1HR: (localization.GetByLabel('UI/Map/StarMap/ShowFactionShipsDestroyed'), starModeHandler.ColorStarsByFactionKills),
         mapcommon.STARMODE_BOOKMARKED: (localization.GetByLabel('UI/Map/StarMap/ShowBookmarks'), starModeHandler.ColorStarsByBookmarks),
         mapcommon.STARMODE_CYNOSURALFIELDS: (localization.GetByLabel('UI/Map/StarMap/ActiveCynosuralFields'), starModeHandler.ColorStarsByCynosuralFields),
         mapcommon.STARMODE_CORPOFFICES: (localization.GetByLabel('UI/Map/StarMap/ShowAssets'),
                                          starModeHandler.ColorStarsByCorpAssets,
                                          'offices',
                                          localization.GetByLabel('UI/Map/StarMap/Offices')),
         mapcommon.STARMODE_CORPIMPOUNDED: (localization.GetByLabel('UI/Map/StarMap/ShowAssets'),
                                            starModeHandler.ColorStarsByCorpAssets,
                                            'impounded',
                                            localization.GetByLabel('UI/Map/StarMap/Impounded')),
         mapcommon.STARMODE_CORPPROPERTY: (localization.GetByLabel('UI/Map/StarMap/ShowAssets'),
                                           starModeHandler.ColorStarsByCorpAssets,
                                           'property',
                                           localization.GetByLabel('UI/Map/StarMap/Property')),
         mapcommon.STARMODE_CORPDELIVERIES: (localization.GetByLabel('UI/Map/StarMap/ShowAssets'),
                                             starModeHandler.ColorStarsByCorpAssets,
                                             'deliveries',
                                             localization.GetByLabel('UI/Map/StarMap/Deliveries')),
         mapcommon.STARMODE_CORPWRAPS: (localization.GetByLabel('UI/Map/StarMap/ShowAssetWraps'),
                                        starModeHandler.ColorStarsByCorpAssets,
                                        'assetwraps',
                                        localization.GetByLabel('UI/Corporations/Assets/AssetSafety')),
         mapcommon.STARMODE_FRIENDS_FLEET: (localization.GetByLabel('UI/Map/StarMap/FindAssociates'), starModeHandler.ColorStarsByFleetMembers),
         mapcommon.STARMODE_FRIENDS_CORP: (localization.GetByLabel('UI/Map/StarMap/FindAssociates'), starModeHandler.ColorStarsByCorpMembers),
         mapcommon.STARMODE_FRIENDS_AGENT: (localization.GetByLabel('UI/Map/StarMap/FindAssociates'), starModeHandler.ColorStarsByMyAgents),
         mapcommon.STARMODE_JUMP_CLONES: (localization.GetByLabel('UI/Map/StarMap/ShowJumpClones'), starModeHandler.ColorStarsByJumpClones),
         mapcommon.STARMODE_AVOIDANCE: (localization.GetByLabel('UI/Map/StarMap/AvoidanceSystems'), starModeHandler.ColorStarsByAvoidedSystems),
         mapcommon.STARMODE_REAL: (localization.GetByLabel('UI/Map/StarMap/ActualColor'), starModeHandler.ColorStarsByRealSunColor),
         mapcommon.STARMODE_SERVICE: (localization.GetByLabel('UI/Map/StarMap/FindStationServices'), starModeHandler.ColorStarsByServices),
         mapcommon.STARMODE_PISCANRANGE: (localization.GetByLabel('UI/Map/StarMap/PlanetScanRange'), starModeHandler.ColorStarsByPIScanRange),
         mapcommon.STARMODE_MYCOLONIES: (localization.GetByLabel('UI/Map/StarMap/MyColonies'), starModeHandler.ColorStarsByMyColonies),
         mapcommon.STARMODE_PLANETTYPE: (localization.GetByLabel('UI/Map/StarMap/ShowSystemsByPlanetTypes'), starModeHandler.ColorStarsByPlanetType),
         mapcommon.STARMODE_INCURSION: (localization.GetByLabel('UI/Map/StarMap/Incursions'), starModeHandler.ColorStarsByIncursions),
         mapcommon.STARMODE_SYSTEM_INTERFERENCE: (localization.GetByLabel('UI/Map/MapPallet/SolarSystemInterference'), starModeHandler.ColorStarsByInterference, self.solarsystemInterferenceSvc),
         mapcommon.STARMODE_ROAMING_WEATHER: (localization.GetByLabel('UI/Map/StarMap/RoamingWeather'), starModeHandler.ColorStarsByRoamingWeather),
         mapcommon.STARMODE_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, None),
         mapcommon.STARMODE_MANUFACTURING_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, industry.MANUFACTURING),
         mapcommon.STARMODE_RESEARCHTIME_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, industry.RESEARCH_TIME),
         mapcommon.STARMODE_RESEARCHMATERIAL_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, industry.RESEARCH_MATERIAL),
         mapcommon.STARMODE_COPY_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, industry.COPYING),
         mapcommon.STARMODE_INVENTION_JOBS24HOUR: (localization.GetByLabel('UI/Map/StarMap/JobsLast24Hours'), starModeHandler.ColorStarsByJobs24Hours, industry.INVENTION),
         mapcommon.STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX: (localization.GetByLabel('UI/Map/StarMap/IndustryCostModifer'), starModeHandler.ColorStarsByIndustryCostModifier, industry.MANUFACTURING),
         mapcommon.STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX: (localization.GetByLabel('UI/Map/StarMap/IndustryCostModifer'), starModeHandler.ColorStarsByIndustryCostModifier, industry.RESEARCH_TIME),
         mapcommon.STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX: (localization.GetByLabel('UI/Map/StarMap/IndustryCostModifer'), starModeHandler.ColorStarsByIndustryCostModifier, industry.RESEARCH_MATERIAL),
         mapcommon.STARMODE_INDUSTRY_COPY_COST_INDEX: (localization.GetByLabel('UI/Map/StarMap/IndustryCostModifer'), starModeHandler.ColorStarsByIndustryCostModifier, industry.COPYING),
         mapcommon.STARMODE_INDUSTRY_INVENTION_COST_INDEX: (localization.GetByLabel('UI/Map/StarMap/IndustryCostModifer'), starModeHandler.ColorStarsByIndustryCostModifier, industry.INVENTION),
         mapcommon.STARMODE_INSURGENCY: (localization.GetByLabel('UI/PirateInsurgencies/dashboardCaption'),
                                         starModeHandler.ColorStarsByInsurgencyInvolvement,
                                         self.insurgencyCampaignSvc,
                                         self.corruptionSuppressionSvc),
         mapcommon.STARMODE_INSURGENCY_CORRUPTION: (localization.GetByLabel('UI/PirateInsurgencies/dashboardCaption'),
                                                    starModeHandler.ColorStarsByInsurgencyCorruption,
                                                    self.insurgencyCampaignSvc,
                                                    self.corruptionSuppressionSvc),
         mapcommon.STARMODE_INSURGENCY_SUPPRESSION: (localization.GetByLabel('UI/PirateInsurgencies/dashboardCaption'),
                                                     starModeHandler.ColorStarsByInsurgencySuppression,
                                                     self.insurgencyCampaignSvc,
                                                     self.corruptionSuppressionSvc)}
        if session.role & ROLE_GML:
            self.starColorHandlers[mapcommon.STARMODE_INCURSIONGM] = (localization.GetByLabel('UI/Map/StarMap/IncursionsGm'), starModeHandler.ColorStarsByIncursionsGM)

    @telemetry.ZONE_METHOD
    def SetStarColorMode(self, starColorMode = None):
        if starColorMode is None:
            starColorMode = GetUserUiSetting('starscolorby', mapcommon.STARMODE_SECURITY)
        self.LogInfo('SetStarColorMode ', starColorMode)
        self.starData = {}
        self.starLegend = []
        mode = starColorMode[0] if isinstance(starColorMode, tuple) else starColorMode
        definition = self.starColorHandlers.get(mode, (localization.GetByLabel('UI/Map/StarMap/ActualColor'), starModeHandler.ColorStarsByRealSunColor))
        desc, colorFunc, args = definition[0], definition[1], definition[2:]
        self.StartLoadingBar('set_star_color', localization.GetByLabel('UI/Map/StarMap/GettingData'), desc, 2)
        blue.pyos.synchro.SleepWallclock(1)
        colorInfo = utillib.KeyVal(solarSystemDict={}, colorList=None, overglowFactor=0.0, legend=set())
        colorFunc(colorInfo, starColorMode, *args)
        self.starLegend = list(colorInfo.legend)
        self.UpdateLoadingBar('set_star_color', desc, localization.GetByLabel('UI/Map/StarMap/GettingData'), 1, 2)
        blue.pyos.synchro.SleepWallclock(1)
        self.HighlightSolarSystems(colorInfo.solarSystemDict, colorInfo.colorList, colorInfo.overglowFactor)
        self.StopLoadingBar('set_star_color')

    def _BuildWarFactionByOwner(self, stations):
        self.warFactionByOwner = {}
        for stationRow in stations:
            ownerID = stationRow.ownerID
            if ownerID not in self.warFactionByOwner:
                factionID = get_corporation_faction_id(ownerID)
                if factionID and IsAnyFWFaction(factionID):
                    self.warFactionByOwner[ownerID] = factionID

    def GetWarFactionByOwner(self, stations):
        if self.warFactionByOwner is None:
            self._BuildWarFactionByOwner(stations)
        return self.warFactionByOwner

    def GetRegionColor(self, regionID):
        if not hasattr(self, 'regionColorCache'):
            self.regionColorCache = {}
        if regionID not in self.regionColorCache:
            color = trinity.TriColor()
            color.SetHSV(float(regionID) * 21 % 360.0, 0.5, 0.8)
            color.a = 0.75
            self.regionColorCache[regionID] = color
        return self.regionColorCache[regionID]

    def GetColorCurve(self, colorList):
        colorCurve = trinity.Tr2CurveColor()
        colorListDivisor = float(len(colorList) - 1)
        for colorID, colorValue in enumerate(colorList):
            time = float(colorID) / colorListDivisor
            if isinstance(colorValue, trinity.TriColor):
                colorValue = (colorValue.r,
                 colorValue.g,
                 colorValue.b,
                 colorValue.a)
            colorCurve.AddKey(time, colorValue, trinity.Tr2CurveInterpolation.LINEAR)

        return colorCurve

    def GetColorCurveValue(self, colorCurve, time):
        return colorCurve.GetValueAt(time)

    @telemetry.ZONE_METHOD
    def HighlightSolarSystems(self, solarSystemDict, colorList = None, overglowFactor = 0.0):
        self.starData = {}
        colorCurve = self.GetColorCurve(colorList or self.GetDefaultColorList())
        self.overglowFactor.value = overglowFactor
        particleSizeToParticleIDs = defaultdict(list)
        particleColorToParticleIDs = defaultdict(list)
        for particleID, solarSystemID in self.particleIDToSystemIDMap.iteritems():
            starColor = NEUTRAL_COLOR
            starSize = SUNBASE
            if solarSystemID in solarSystemDict and solarSystemDict[solarSystemID] is not None:
                size, age, commentCallback, uniqueColor = solarSystemDict[solarSystemID]
                size *= SUNBASE
                if uniqueColor is None:
                    col = self.GetColorCurveValue(colorCurve, age)
                else:
                    col = uniqueColor
                if commentCallback:
                    self.starData[particleID] = commentCallback
                if isinstance(col, trinity.TriColor):
                    starColor = (col.r,
                     col.g,
                     col.b,
                     1.0)
                else:
                    starColor = col
                starSize = size
            particleSizeToParticleIDs[starSize].append(particleID)
            particleColorToParticleIDs[starColor].append(particleID)

        for starSize, particleIDs in particleSizeToParticleIDs.iteritems():
            self.SetStarParticleSize(starSize, tuple(particleIDs))

        for starColor, particleIDs in particleColorToParticleIDs.iteritems():
            self.SetStarParticleColor(starColor, tuple(particleIDs))

        self.starParticles.UpdateData()
        self.mapStars.display = 1

    def GetDefaultColorList(self):
        return [(1.0, 0.0, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0)]

    @telemetry.ZONE_METHOD
    def HighlightSolarSystemsBulk(self, solarSystemList, size, colorList = None):
        self.starData = {}
        if colorList is None:
            colorList = (1.0, 0.0, 0.0)
        else:
            colorList = (colorList[0].r, colorList[0].g, colorList[0].b)
        particles2highlight = []
        for solarSystemID, comment in solarSystemList:
            particleID = self.GetCloudNumFromItemID(solarSystemID)
            particles2highlight.append(particleID)
            if comment:
                if len(comment):
                    self.starData[particleID] = comment

        self.SetStarParticleColor(NEUTRAL_COLOR[:3])
        self.SetStarParticleColor(colorList, particles2highlight)
        self.starParticles.UpdateData()
        self.mapStars.display = 1

    def GetRegionLabel(self, labelID):
        return self.regionLabels[labelID]

    def GetRouteType(self, label = False):
        pfRouteType = GetUserUiSetting('pfRouteType', 'safe')
        if label:
            return {'shortest': localization.GetByLabel('UI/Map/StarMap/Shortest'),
             'safe': localization.GetByLabel('UI/Map/StarMap/Safest'),
             'unsafe': localization.GetByLabel('UI/Map/StarMap/LessSecure')}.get(pfRouteType, localization.GetByLabel('UI/Common/Unknown')).lower()
        return pfRouteType

    def _IsDestinationValid(self, destinationID):
        if idCheckers.IsStation(destinationID) and destinationID in cfg.stations:
            stationInfo = sm.GetService('ui').GetStationStaticInfo(destinationID)
            if IsDeprecatedStation(stationInfo.stationTypeID):
                return False
            destinationSolarSystemID = stationInfo.solarSystemID
            if IsTriglavianSystem(destinationSolarSystemID) and not IsTriglavianSystem(session.solarsystemid2):
                return False
            isDestinationInSameSolarSystem = destinationSolarSystemID == session.solarsystemid2
            isDestinationInKnownSpace = IsKnownSpaceSystem(destinationSolarSystemID)
            return bool(isDestinationInSameSolarSystem or isDestinationInKnownSpace)
        if IsTriglavianSystem(destinationID) and not IsTriglavianSystem(session.solarsystemid2):
            return False
        if destinationID in self.GetKnownUniverseSolarSystems():
            return True
        return sm.GetService('structureDirectory').GetStructureInfo(destinationID) is not None

    def OnDestinationChange(self, solarSystemID, clearOtherWaypoints, first):
        sm.GetService('autoPilot').SetOff('Waypoints set remotely.')
        self.SetWaypoint(solarSystemID, clearOtherWaypoints, first)

    @telemetry.ZONE_METHOD
    def SetWaypoint(self, destinationID, clearOtherWaypoints = False, first = False):
        waypoints = self.GetWaypoints()
        if not self._IsDestinationValid(destinationID):
            eve.Message('Command', {'command': localization.GetByLabel('UI/Map/StarMap/CantSetWaypoint')})
            return
        if clearOtherWaypoints:
            if len(waypoints):
                pass
            waypoints = []
        if destinationID in waypoints:
            eve.Message('WaypointAlreadySet')
            return
        if destinationID == session.constellationid:
            eve.Message('WaypointAlreadyInConstellation')
            return
        if destinationID == session.regionid:
            eve.Message('WaypointAlreadyInRegion')
            return
        if first:
            waypoints.insert(0, destinationID)
        else:
            waypoints.append(destinationID)
        SetCharUiSetting('autopilot_waypoints', waypoints)
        self.UpdateRoute()
        self.ShowWhereIAm()
        self.autoPilot.VerifyJumpGatesInRoute()
        if clearOtherWaypoints:
            sm.ScatterEvent('OnClientEvent_DestinationSet', destinationID)

    def SetWaypoints(self, waypoints):
        self.LogInfo('SetWaypoints')
        SetCharUiSetting('autopilot_waypoints', waypoints)
        self.UpdateRoute()
        self.autoPilot.VerifyJumpGatesInRoute()

    def GetWaypoints(self):
        waypoints = GetCharUiSetting('autopilot_waypoints', [])
        for waypoint in waypoints:
            if not self._IsDestinationValid(waypoint):
                return []

        return waypoints

    @telemetry.ZONE_METHOD
    def ClearWaypoints(self, locationID = None):
        self.LogInfo('Map: ClearWaypoints')
        if locationID is not None:
            waypoints = self.GetWaypoints()
            if locationID in waypoints:
                waypoints.remove(locationID)
                SetCharUiSetting('autopilot_waypoints', waypoints)
                self.UpdateRoute()
                self.ShowWhereIAm()
                self.UpdateLines(hint='ClearWaypoints', updateColor=True)
                sm.ScatterEvent('OnDestinationCleared')
                return
            self.LogError('Utried to remove waypoint %s  that was not in waypoint list %s ' % (locationID, waypoints))
        else:
            waypoints = []
            self.destinationPath = [None]
        SetCharUiSetting('autopilot_waypoints', waypoints)
        if not self.doingLogoff:
            sm.ScatterEvent('OnDestinationSet', self.destinationPath[0])
        if self.mapRoot:
            self.ClearRoute('autoPilotRoute')
            self.UpdateLines(hint='ClearWaypoints', updateColor=True)
            self.ShowDestination()
            self.CheckAllLabels('ClearWaypoints')
        sm.ScatterEvent('OnDestinationCleared')

    def RemoveWaypointIfFirst(self, locationID):
        waypoints = self.GetWaypoints()
        if waypoints and waypoints[0] == locationID:
            self.ClearWaypoints(locationID)

    @telemetry.ZONE_METHOD
    def GetRouteFromWaypoints(self, waypoints, startSystem = None):
        if startSystem is None:
            startSystem = session.solarsystemid2
        if not IsKnownSpaceSystem(startSystem):
            fullWaypointList = waypoints
        else:
            fullWaypointList = [startSystem] + waypoints
        if len(fullWaypointList) <= 1:
            return fullWaypointList
        self.LogInfo('Calling pathfinder with waypoint list', str(waypoints))
        destinationPath = self.clientPathfinderService.GetWaypointPath(fullWaypointList)
        return destinationPath or []

    @telemetry.ZONE_METHOD
    def GetRouteBetween(self, fromID, toID):
        self.LogInfo('Getting route between %s and %s', fromID, toID)
        route = self.clientPathfinderService.GetAutopilotPathBetween(fromID, toID)
        return route or []

    @telemetry.ZONE_METHOD
    def UpdateRoute(self, updateLabels = 1, fakeUpdate = 0, autopilotSaysRouteDone = False):
        if not updateLabels:
            if getattr(self, 'doingRouteUpdate', 0) == 1:
                return
        self.doingRouteUpdate = 1
        waypoints = self.GetWaypoints()
        self.LogInfo('UpdateRoute - waypoints ', waypoints)
        if len(waypoints):
            for each in [session.structureid,
             session.stationid,
             session.solarsystemid2,
             session.constellationid,
             session.regionid]:
                if waypoints[0] == each:
                    waypoints = waypoints[1:]
                    SetCharUiSetting('autopilot_waypoints', waypoints)
                    if GetUserUiSetting('autopilot_stop_at_each_waypoint', 0) == 0:
                        if self.autoPilot.GetState():
                            self.autoPilot.SetOff('  - waypoint reached')
                    break

        self.ClearRoute('autoPilotRoute')
        if not len(waypoints):
            self.destinationPath = [None]
            if self.viewState.IsViewActive('starmap'):
                self.UpdateLines(hint='UpdateRoute')
            self.ShowDestination()
            sm.ScatterEvent('OnDestinationSet', None)
            self.LogInfo('UpdateRoute done no wp')
            self.doingRouteUpdate = 0
            return
        if not fakeUpdate or not hasattr(self, 'destinationPath') or self.destinationPath[0] != session.solarsystemid:
            self.LogInfo('Getting route from waypoints')
            destinationPath = self.GetRouteFromWaypoints(waypoints)
        else:
            destinationPath = self.destinationPath[1:]
        if not len(destinationPath):
            if len(self.destinationPath) and (idCheckers.IsSolarSystem(self.destinationPath[0]) or self.destinationPath[0] is None or autopilotSaysRouteDone):
                self.destinationPath = [None]
                if self.viewState.IsViewActive('starmap'):
                    self.UpdateLines(hint='UpdateRoute2')
                self.ShowDestination()
                sm.ScatterEvent('OnDestinationSet', None)
                self.LogInfo('UpdateRoute done no route to wp')
                self.doingRouteUpdate = 0
                return
            destinationPath = self.destinationPath
        self.destinationPath = destinationPath
        if self.destinationPath[0] == session.solarsystemid2:
            self.LogWarn('self destination path 0 is own solarsystem, picking next node instead. Path: ', self.destinationPath)
            self.destinationPath = self.destinationPath[1:]
            if not len(self.destinationPath):
                self.destinationPath = [None]
        if self.viewState.IsViewActive('starmap'):
            if updateLabels:
                route = MapRoute()
                pathOnlySolarSystems = [ locationID for locationID in destinationPath if idCheckers.IsSolarSystem(locationID) ]
                route.DrawRoute([session.solarsystemid2] + pathOnlySolarSystems, flattened=self.flattened, rotationQuaternion=self.GetCurrentStarmapRotation())
                self.autoPilotRoute = route
                scene = self.sceneManager.GetRegisteredScene('starmap')
                scene.objects.append(route.model)
                self.ShowDestination()
                self.CheckAllLabels('UpdateRoute')
            self.UpdateLines(hint='UpdateRoute3', updateColor=True)
        if updateLabels:
            sm.ScatterEvent('OnDestinationSet', self.destinationPath[0])
        self.LogInfo('UpdateRoute done')
        self.doingRouteUpdate = 0

    def GetCurrentStarmapRotation(self):
        if len(self.mapRoot.rotationCurve.curve.keys) > 0:
            return self.mapRoot.rotationCurve.curve.keys[-1][1]
        else:
            return None

    @telemetry.ZONE_METHOD
    def SetTileMode(self, tileMode):
        SetUserUiSetting('map_tile_mode', tileMode)
        SetUserUiSetting('map_tile_no_tiles', 0)
        sm.ScatterEvent('OnLoadWMCPSettings', 'mapsettings_tiles')
        if not self.IsFlat() and GetUserUiSetting('map_tile_show_unflattened', 0) == 0:
            self.Flatten()
        self.UpdateHexMap()

    @telemetry.ZONE_METHOD
    def UpdateHexMap(self, isFlat = None):
        showHexMap = GetUserUiSetting('map_tile_no_tiles', 1) == 0
        showUnflattened = GetUserUiSetting('map_tile_show_unflattened', 0)
        self.tileLegend = []
        if isFlat is None:
            isFlat = self.IsFlat()
        if showHexMap and (showUnflattened or isFlat):
            systemToAllianceMap = self.GetAllianceSolarSystems()
            changeList = []
            if GetUserUiSetting('map_tile_activity', 0) == 1:
                changeList = sm.GetService('sov').GetRecentActivity()
            tileMode = GetUserUiSetting('map_tile_mode', TILE_MODE_SOVEREIGNTY)
            colorByStandings = tileMode == TILE_MODE_STANDIGS
            self.hexMap.LayoutTiles(HEX_TILE_SIZE, systemToAllianceMap, changeList, colorByStandings)
            self.hexMap.Enable()
            showOutlines = GetUserUiSetting('map_tile_show_outlines', 1) == 1
            self.hexMap.EnableOutlines(showOutlines)
            self.tileLegend = self.hexMap.legend
        else:
            self.hexMap.Enable(False)

    def HighlightTiles(self, dataList, colorList):
        self.hexMap.HighlightTiles(dataList, colorList)

    def GetLegend(self, name):
        return getattr(self, name + 'Legend', [])

    @telemetry.ZONE_METHOD
    def CreateLabels(self, labelids):
        self.LogInfo('Map Create ', len(labelids), ' labels')
        for labelID in labelids:
            if labelID in self.labels:
                continue
            if labelID in self.labels:
                label = self.labels[labelID]
                if label is not None and not label.destroyed:
                    continue
                else:
                    del self.labels[labelID]
            self.AddLabel(labelID)

    @telemetry.ZONE_METHOD
    def ClearLabels(self, labelids = 'all'):
        labels = getattr(self, 'labels', {})
        if labelids == 'all':
            labelids = labels.keys()
        for labelID in labelids:
            if labels.has_key(labelID):
                label = labels[labelID]
                if label is not None and not label.destroyed:
                    label.Close()
                del labels[labelID]
            if self.labeltrackers[labelID] in self.labeltrackersTF.children:
                self.labeltrackersTF.children.remove(self.labeltrackers[labelID])

    def AddLabel(self, itemID):
        if itemID > 0:
            iteminfo = self.map.GetItem(itemID)
            tracker = self.AddTracker(iteminfo.itemName, itemID, iteminfo.x, iteminfo.y, iteminfo.z)
            itemName = iteminfo.itemName
            itemID = iteminfo.itemID
            typeID = iteminfo.typeID
        else:
            lm = self.map.GetLandmark(itemID * -1)
            landmarkName = maputils.GetNameFromMapCache(lm.landmarkNameID, 'landmark')
            tracker = self.AddTracker(landmarkName, itemID, *lm.position)
            itemName = landmarkName
            itemID = itemID
            typeID = const.typeMapLandmark
        if not itemName:
            return
        label = MapLabel(parent=uicore.layer.starmap, name=itemName, align=uiconst.NOALIGN, state=uiconst.UI_PICKCHILDREN, dock=False, width=300, height=32)
        label.Startup(itemName, itemID, typeID, tracker, None)
        self.labels[itemID] = label

    @telemetry.ZONE_METHOD
    def AddTracker(self, name, itemID, x = 0.0, y = 0.0, z = 0.0, factor = None):
        if itemID in self.labeltrackers and self.labeltrackers[itemID] not in self.labeltrackersTF.children:
            self.labeltrackersTF.children.append(self.labeltrackers[itemID])
            return self.labeltrackers[itemID]
        tracker = trinity.EveTransform()
        trackPos = (x * STARMAP_SCALE, y * STARMAP_SCALE, z * STARMAP_SCALE)
        tracker.translation = trackPos
        self.labeltrackersTF.children.append(tracker)
        self.labeltrackers[itemID] = tracker
        return tracker

    def StartLoadingBar(self, key, tile, action, total):
        if getattr(self, 'loadingBarActive', None) is None:
            self.loading.ProgressWnd(tile, action, 0, total)
            self.loadingBarActive = key

    def UpdateLoadingBar(self, key, tile, action, part, total):
        if getattr(self, 'loadingBarActive', None) == key:
            self.loading.ProgressWnd(tile, action, part, total)

    def StopLoadingBar(self, key):
        if getattr(self, 'loadingBarActive', None) == key:
            self.loading.StopCycle()
            self.loadingBarActive = None

    def _IsOutsideKnownSpaceWithInsufficientWaypoints(self):
        return not IsKnownSpaceSystem(session.solarsystemid2) and len(self.destinationPath) == 1

    def GetAutopilotRoute(self):
        if self.destinationPath == [None] or self._IsOutsideKnownSpaceWithInsufficientWaypoints():
            return
        else:
            return self.destinationPath[:]

    def OnAutopilotUpdated(self):
        self.UpdateRoute()
