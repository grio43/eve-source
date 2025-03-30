#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\systemMapHandler.py
import eveui
from carbon.common.script.util.format import FmtDist, FmtAmt
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.environment.spaceObject.planet import Planet
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.inflight.scannerFiles.directionalScanHandler import MapViewDirectionalScanHandler
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import IsDscanConeShown
from eve.client.script.ui.shared.mapView import mapViewUtil
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_SOLARSYSTEM_CELESTIAL, VIEWMODE_MARKERS_SETTINGS, MARKERID_PROBE
from eve.client.script.ui.shared.mapView.markers.mapMarkerCelestial import MarkerSpaceObject
from eve.client.script.ui.shared.mapView.markers.mapMarkerProbe import MarkerProbe
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos, ScaleSolarSystemValue
from eve.client.script.ui.shared.maps.label import TransformableLabel
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from localization import GetByLabel
import trinity
import uthread
import evegraphics.settings as gfxsettings
import geo2
import math
import weakref
import inventorycommon.typeHelpers
from carbonui.uicore import uicore
PLANET_TEXTURE_SIZE = 512

class SystemMapHandler(object):
    scene = None
    probeHandler = None
    directionalScanHandler = None
    localMarkerIDs = None
    cameraTranslationFromParent = None
    solarSystemRadius = None
    sunID = None
    rangeIndicator = None
    _mapView = None

    def __init__(self, mapView, solarsystemID, scaling = 1.0, position = None, loadBookmarks = True):
        if mapView:
            self.mapView = mapView
            self.scene = mapView.scene
        self.solarsystemID = solarsystemID
        self.scaling = scaling
        self.systemMapSvc = sm.GetService('systemmap')
        self.loadBookmarks = loadBookmarks
        self.localMarkerIDs = set()
        self._closed = False
        parent = trinity.EveTransform()
        parent.name = 'solarsystem_%s' % solarsystemID
        self.systemMapTransform = parent
        if mapView:
            mapView.mapRoot.children.append(self.systemMapTransform)
        if position:
            self.SetPosition(position)

    def Close(self):
        self._closed = True
        if self.scene:
            self._RemoveAllMarkers()
            uthread.new(self._AnimClose)
        else:
            self.RemoveFromScene()

    def _AnimClose(self):
        uicore.animations.MorphVector3(self.systemMapTransform, 'scaling', self.systemMapTransform.scaling, (0.0, 0.0, 0.0), duration=0.5, sleep=True)
        self.RemoveFromScene()

    def RemoveFromScene(self):
        mapView = self.mapView
        self._RemoveAllMarkers()
        self.StopProbeHandler()
        self.StopDirectionalScanHandler()
        if mapView and mapView.mapRoot and self.systemMapTransform in mapView.mapRoot.children:
            mapView.mapRoot.children.remove(self.systemMapTransform)
        self.systemMapTransform = None
        self.scene = None
        self.localMarkerIDs = None

    def _RemoveAllMarkers(self):
        if self.mapView and self.mapView.markersHandler and self.localMarkerIDs:
            for markerID in self.localMarkerIDs:
                self.mapView.markersHandler.RemoveMarker(markerID)

        self.localMarkerIDs = set()

    def OnCameraUpdate(self):
        if self.directionalScanHandler:
            self.directionalScanHandler.OnCameraUpdate()
        if self.directionalScanHandler and IsDscanConeShown():
            direction = self.directionalScanHandler.GetConeDirection()
            egoPos = self.mapView.GetEgoPosition()
            self.markersHandler.UpdateDscanHilite(direction, egoPos)

    def EnableProbeHandlerStandalone(self):
        if self.probeHandler:
            return
        self.StopProbeHandler()
        from eve.client.script.ui.shared.mapView.mapViewProbeHandlerStandalone import MapViewProbeHandlerStandalone
        self.probeHandler = MapViewProbeHandlerStandalone(self)
        self.LoadProbeMarkers()

    def StopProbeHandler(self):
        if self.probeHandler:
            self.probeHandler.StopHandler()
        self.probeHandler = None

    def EnableDirectionalScanHandler(self):
        if self.directionalScanHandler:
            return
        self.StopDirectionalScanHandler()
        self.directionalScanHandler = MapViewDirectionalScanHandler(self)

    def StopDirectionalScanHandler(self):
        if self.directionalScanHandler:
            self.directionalScanHandler.StopHandler()
        if self.markersHandler:
            self.markersHandler.HideAllDscanHilite()
        self.directionalScanHandler = None

    @apply
    def mapView():

        def fget(self):
            if self._mapView:
                return self._mapView()

        def fset(self, value):
            if value:
                self._mapView = weakref.ref(value)
            else:
                self._mapView = None

        return property(**locals())

    @apply
    def markersHandler():

        def fget(self):
            mapView = self.mapView
            if mapView:
                return mapView.markersHandler

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def bookmarkHandler():

        def fget(self):
            mapView = self.mapView
            if mapView:
                return mapView.bookmarkHandler

        def fset(self, value):
            pass

        return property(**locals())

    def RegisterCameraTranslationFromParent(self, cameraTranslationFromParent):
        self.cameraTranslationFromParent = cameraTranslationFromParent
        if self.probeHandler and self.solarSystemRadius:
            radius = ScaleSolarSystemValue(self.solarSystemRadius)
            camangle = 0.5
            translationFromParent = radius / math.sin(camangle) * math.cos(camangle) * 16
            if cameraTranslationFromParent > translationFromParent:
                self.probeHandler.Hide()
            else:
                self.probeHandler.Show()

    def SetPosition(self, position):
        self.position = position
        if self.systemMapTransform:
            self.systemMapTransform.translation = self.position

    def LoadCelestials(self):
        uthread.new(self._LoadCelestials)
        groups, solarsystemData = self.systemMapSvc.GetSolarsystemHierarchy(self.solarsystemID)
        for transform in self.systemMapTransform.children:
            try:
                itemID = int(transform.name)
                itemData = solarsystemData[itemID]
            except:
                continue

            if itemData.groupID == const.groupPlanet:
                planetTransform = self.LoadPlanet(itemData.typeID, itemID)
                scaling = self.scaling * 1.0 / mapViewConst.SOLARSYSTEM_SCALE
                planetTransform.scaling = (scaling, scaling, scaling)
                planetTransform.translation = transform.translation

    def ShowRangeIndicator(self):
        self.LoadRangeIndicator()

    def HideRangeIndicator(self):
        if self.rangeIndicator:
            uicore.animations.MorphVector3(self.rangeIndicator.rootTransform, 'scaling', startVal=self.rangeIndicator.rootTransform.scaling, endVal=(0, 0, 0), duration=0.2, callback=self._RemoveRangeIndicator)

    def _RemoveRangeIndicator(self):
        if self.rangeIndicator and self.rangeIndicator.rootTransform in self.systemMapTransform.children:
            self.rangeIndicator.systemMapTransform.children.remove(self.rangeIndicator.rootTransform)
        self.rangeIndicator = None

    def LoadRangeIndicator(self):
        self.HideRangeIndicator()
        rangeIndicator = RangeIndicator(self.systemMapTransform, contextScaling=1.0 / const.AU)
        uicore.animations.MorphVector3(rangeIndicator.rootTransform, 'scaling', startVal=(0, 0, 0), endVal=(const.AU, const.AU, const.AU), duration=0.4)
        self.rangeIndicator = rangeIndicator
        self.SetupMyPositionTracker(rangeIndicator.rootTransform)

    def LoadPlanet(self, planetTypeID, planetID):
        planet = Planet()
        graphicFile = inventorycommon.typeHelpers.GetGraphicFile(planetTypeID)
        planet.typeData['graphicFile'] = graphicFile
        planet.typeID = planetTypeID
        planet.LoadPlanet(planetID, forPhotoService=True, rotate=False, hiTextures=True)
        if planet.model is None or planet.model.highDetail is None:
            return
        planetTransform = trinity.EveTransform()
        planetTransform.name = 'planet'
        planetTransform.children.append(planet.model.highDetail)
        planet.SetEffectParameters()
        trinity.WaitForResourceLoads()
        for t in planet.model.highDetail.children:
            if t.mesh is not None:
                if len(t.mesh.transparentAreas) > 0:
                    t.sortValueMultiplier = 2.0

        self.systemMapTransform.children.append(planetTransform)
        return planetTransform

    def LoadSolarSystemMap(self):
        self.maxRadius = 0.0
        solarsystemID = self.solarsystemID
        solarSystemData = self.systemMapSvc.GetSolarsystemData(solarsystemID)
        planets = []
        childrenToParentByID = {}
        sunID = None
        maxRadius = 0.0
        for celestialObject in solarSystemData:
            if celestialObject.groupID == const.groupPlanet:
                planets.append((celestialObject.itemID, geo2.Vector(celestialObject.x, celestialObject.y, celestialObject.z)))
                maxRadius = max(maxRadius, geo2.Vec3Length((celestialObject.x, celestialObject.y, celestialObject.z)))
            elif celestialObject.groupID == const.groupSun:
                sunID = celestialObject.itemID
                sunGraphicFilePath = GetGraphicFile(cfg.mapSystemCache[solarsystemID].sunFlareGraphicID)
                sunGraphicFile = trinity.Load(sunGraphicFilePath)
                self.CreateSun(sunGraphicFile)

        self.sunID = sunID
        objectPositions = {}
        for each in solarSystemData:
            objectPositions[each.itemID] = (each.x, each.y, each.z)
            if each.groupID in (const.groupPlanet, const.groupStargate):
                childrenToParentByID[each.itemID] = sunID
                continue
            closest = []
            eachPosition = geo2.Vector(each.x, each.y, each.z)
            maxRadius = max(maxRadius, geo2.Vec3Length(eachPosition))
            for planetID, planetPos in planets:
                diffPos = planetPos - eachPosition
                diffVector = geo2.Vec3Length(diffPos)
                closest.append((diffVector, planetID))

            if closest:
                closest.sort()
                childrenToParentByID[each.itemID] = closest[0][1]

        self.maxRadius = maxRadius
        for each in solarSystemData:
            if each.itemID == each.locationID:
                continue
            if each.groupID == const.groupSecondarySun:
                continue
            if each.groupID == const.groupPlanet:
                self.CreatePlanet((each.x, each.y, each.z), each.itemID)
                OrbitCircle(each.itemID, (each.x, each.y, each.z), objectPositions[sunID], self.systemMapTransform)
            elif each.groupID == const.groupMoon:
                parentID = childrenToParentByID.get(each.itemID, None)
                if parentID:
                    self.CreatePlanet((each.x, each.y, each.z), each.itemID)
                    OrbitCircle(each.itemID, (each.x, each.y, each.z), objectPositions[parentID], self.systemMapTransform)

        self.solarSystemRadius = maxRadius
        cfg.evelocations.Prime(objectPositions.keys(), 0)

    def CreatePlanet(self, planetPosition, itemID = None):
        scaling = 0.01 / mapViewConst.SOLARSYSTEM_SCALE
        planetTransform = trinity.EveTransform()
        planetTransform.name = str(itemID) or 'planetTransform'
        planetTransform.scaling = (scaling, scaling, scaling)
        planetTransform.translation = planetPosition
        self.systemMapTransform.children.append(planetTransform)
        planetTransform.useDistanceBasedScale = True
        planetTransform.distanceBasedScaleArg1 = 1.0
        planetTransform.distanceBasedScaleArg2 = 0.0
        planetTransform.mesh = trinity.Tr2Mesh()
        planetTransform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        planetTransform.modifier = 1
        area = trinity.Tr2MeshArea()
        planetTransform.mesh.additiveAreas.append(area)
        effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        area.effect = effect
        diffuseColor = trinity.Tr2Vector4Parameter()
        diffuseColor.name = 'DiffuseColor'
        effect.parameters.append(diffuseColor)
        diffuseMap = trinity.TriTextureParameter()
        diffuseMap.name = 'DiffuseMap'
        diffuseMap.resourcePath = 'res:/UI/Texture/Classes/MapView/spotSprite.dds'
        effect.resources.append(diffuseMap)

    def CreateSun(self, sunGraphic):

        def GetEffectParameter(effect, parameterName):
            for paramName, value in effect.constParameters:
                if paramName == parameterName:
                    return value

            for parameter in effect.parameters:
                if parameter.name == parameterName:
                    return parameter.value

        if not self.systemMapTransform:
            return
        scaling = 1.0 / mapViewConst.SOLARSYSTEM_SCALE * 5
        sunTransform = trinity.EveTransform()
        sunTransform.name = 'Sun'
        sunTransform.scaling = (scaling, scaling, scaling)
        self.systemMapTransform.children.append(sunTransform)
        ignoredSunMeshAreas = ['flare', 'rainbow', 'tg_added']
        triglavianSystem = IsTriglavianSystem(self.solarsystemID)
        for each in sunGraphic.mesh.additiveAreas:
            onIgnoreList = any([ areaName in each.name.lower() for areaName in ignoredSunMeshAreas ])
            if not each.display or onIgnoreList:
                continue
            scale = GetEffectParameter(each.effect, 'Size')
            if scale is None:
                continue
            if triglavianSystem:
                color = mapViewConst.TRIGLAVIAN_SUN_FLARE_COLOR
            else:
                color = GetEffectParameter(each.effect, 'Color')
            if color is None:
                continue
            textureParameter = each.effect.resources.FindByName('TexMap')
            if textureParameter is None:
                continue
            transform = trinity.EveTransform()
            transform.scaling = (scale[0], scale[1], scale[2])
            transform.mesh = trinity.Tr2Mesh()
            transform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
            transform.modifier = 1
            transform.name = each.name
            area = trinity.Tr2MeshArea()
            transform.mesh.additiveAreas.append(area)
            effect = trinity.Tr2Effect()
            effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
            area.effect = effect
            diffuseColor = trinity.Tr2Vector4Parameter()
            diffuseColor.name = 'DiffuseColor'
            diffuseColor.value = color
            effect.parameters.append(diffuseColor)
            diffuseMap = trinity.TriTextureParameter()
            diffuseMap.name = 'DiffuseMap'
            diffuseMap.resourcePath = textureParameter.resourcePath
            effect.resources.append(diffuseMap)
            sunTransform.children.append(transform)

    def LoadMarkers(self, showChanges = False):
        mapView = self.mapView
        if not mapView or not mapView.markersHandler:
            return
        loadedCelestialMarkers = set()
        loadMarkerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, mapView.mapViewID)
        if self.solarsystemID == session.solarsystemid:
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark:
                for itemID, ball in ballpark.balls.iteritems():
                    if ballpark is None:
                        break
                    slimItem = ballpark.GetInvItem(itemID)
                    if not slimItem:
                        continue
                    markerID = (MARKERID_SOLARSYSTEM_CELESTIAL, slimItem.itemID)
                    if slimItem.groupID in loadMarkerGroups:
                        pos = SolarSystemPosToMapPos((ball.x, ball.y, ball.z))
                        pos = geo2.Vec3ScaleD(pos, self.scaling)
                        mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerSpaceObject, celestialData=slimItem, solarSystemID=self.solarsystemID, highlightOnLoad=showChanges, mapPositionLocal=pos, mapPositionSolarSystem=self.position, distanceFadeAlphaNearFar=None)
                        loadedCelestialMarkers.add(markerID)

        solarSystemData = self.systemMapSvc.GetSolarsystemData(self.solarsystemID)
        for each in solarSystemData:
            markerID = (MARKERID_SOLARSYSTEM_CELESTIAL, each.itemID)
            if markerID in loadedCelestialMarkers:
                continue
            if each.groupID in loadMarkerGroups:
                pos = SolarSystemPosToMapPos((each.x, each.y, each.z))
                pos = geo2.Vec3ScaleD(pos, self.scaling)
                mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerSpaceObject, celestialData=each, solarSystemID=self.solarsystemID, highlightOnLoad=showChanges, mapPositionLocal=pos, mapPositionSolarSystem=self.position, distanceFadeAlphaNearFar=None)
                loadedCelestialMarkers.add(markerID)

        for markerID in self.localMarkerIDs.copy():
            if markerID[0] != MARKERID_SOLARSYSTEM_CELESTIAL:
                continue
            if markerID not in loadedCelestialMarkers:
                mapView.markersHandler.RemoveMarker(markerID, fadeOut=showChanges)
                self.localMarkerIDs.remove(markerID)

        self.localMarkerIDs.update(loadedCelestialMarkers)
        mapView.markersHandler.UpdateGateMarkerYellowIfNextJump()
        self.LoadProbeMarkers()
        if self.loadBookmarks:
            uthread.new(self.LoadBookmarkMarkers, showChanges)

    def GetMarkerIDs(self):
        return self.localMarkerIDs or set()

    def GetProbeMarkerIDs(self):
        return [ markerID for markerID in self.localMarkerIDs if markerID[0] == MARKERID_PROBE ]

    def LoadBookmarkMarkers(self, showChanges = False):
        if self.bookmarkHandler:
            loadedMarkerIDs = self.bookmarkHandler.LoadBookmarkMarkers(loadSolarSystemID=self.solarsystemID, showChanges=showChanges)
            self.localMarkerIDs = self.localMarkerIDs.union(loadedMarkerIDs)

    def LoadProbeMarkers(self, *args):
        if not self.probeHandler or self.mapView:
            return
        currentProbeMarkers = self.GetProbeMarkerIDs()
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetProbeData()
        loadMarkerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, self.mapView.mapViewID)
        showProbes = const.groupScannerProbe in loadMarkerGroups
        if showProbes and probes is not None and len(probes) > 0:
            for probe in probes.itervalues():
                markerID = (MARKERID_PROBE, probe.probeID)
                markerObject = self.mapView.markersHandler.GetMarkerByID(markerID)
                if markerObject:
                    markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(probe.pos), animate=True)
                else:
                    self.mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerProbe, probeData=probe, solarSystemID=self.solarsystemID, mapPositionLocal=SolarSystemPosToMapPos(probe.pos), mapPositionSolarSystem=self.position, trackObjectID=probe.probeID, distanceFadeAlphaNearFar=None)
                self.localMarkerIDs.add(markerID)
                if markerID in currentProbeMarkers:
                    currentProbeMarkers.remove(markerID)

        for markerID in currentProbeMarkers:
            self.mapView.markersHandler.RemoveMarker(markerID)
            self.localMarkerIDs.remove(markerID)

    def CreateRenderTarget(self):
        textureQuality = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        size = PLANET_TEXTURE_SIZE >> textureQuality
        rt = None
        while rt is None or not rt.isValid:
            rt = trinity.Tr2RenderTarget(2 * size, size, 0, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
            if not rt.isValid:
                if size < 2:
                    return
                size = size / 2
                rt = None

        return (rt, size)

    def SetupMyPositionTracker(self, transform):
        done = False
        while not done and not self._closed:
            ballpark = sm.GetService('michelle').GetBallpark(doWait=True)
            if ballpark is None:
                eveui.wait_for_next_frame()
                continue
            ball = ballpark.GetBall(self.sunID)
            if ball is None:
                eveui.wait_for_next_frame()
                continue
            vectorCurve = trinity.Tr2CurveVector3()
            vectorCurve.AddKey(0, (-1.0, -1.0, -1.0))
            vectorSequencer = trinity.TriVectorSequencer()
            vectorSequencer.operator = trinity.TRIOP_MULTIPLY
            vectorSequencer.functions.append(ball)
            vectorSequencer.functions.append(vectorCurve)
            binding = trinity.TriValueBinding()
            binding.sourceAttribute = 'value'
            binding.destinationAttribute = 'translation'
            binding.scale = 1.0
            binding.sourceObject = vectorSequencer
            binding.destinationObject = transform
            curveSet = trinity.TriCurveSet()
            curveSet.name = 'translationCurveSet'
            curveSet.playOnLoad = True
            curveSet.curves.append(vectorSequencer)
            curveSet.bindings.append(binding)
            transform.curveSets.append(curveSet)
            curveSet.Play()
            done = True


class OrbitCircle(object):
    lineSetScaling = 1000000.0

    def __init__(self, orbitID, position, parentPosition, parentTransform):
        self.orbitID = orbitID
        dirVec = geo2.Vec3Subtract(position, parentPosition)
        radius = geo2.Vec3Length(dirVec)
        dirVec = geo2.Vec3Normalize(dirVec)
        fwdVec = (-1.0, 0.0, 0.0)
        rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
        radius = radius / self.lineSetScaling
        lineSet = mapViewUtil.CreateLineSet()
        lineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
        lineSet.translation = parentPosition
        lineSet.rotation = rotation
        parentTransform.children.append(lineSet)
        self.pixelLineSet = lineSet
        orbitLineColor = (1, 1, 1, 0.1)
        mapViewUtil.DrawCircle(lineSet, (0, 0, 0), radius, startColor=orbitLineColor, endColor=orbitLineColor, lineWidth=2.5)
        lineSet.SubmitChanges()
        lineSet = mapViewUtil.CreatePlanarLineSet()
        lineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
        lineSet.translation = parentPosition
        lineSet.rotation = rotation
        parentTransform.children.append(lineSet)
        self.planarLineSet = lineSet
        orbitLineColor = orbitLineColor
        self.planarLineIDs = mapViewUtil.DrawCircle(lineSet, (0, 0, 0), radius, startColor=orbitLineColor, endColor=orbitLineColor, lineWidth=radius / 150.0)
        lineSet.SubmitChanges()


class RangeIndicator(object):
    circleColor = (0.065, 0.065, 0.065, 0.7)
    labelColor = (0.5, 0.5, 0.5, 0.7)
    defaultRangeSteps = [ each * const.AU for each in (30, 25, 20, 15, 10, 5) ]

    def __init__(self, parentTransform = None, rangeSteps = None, contextScaling = 1.0):
        rangeCircles = trinity.EveTransform()
        rangeCircles.name = 'RangeIndicator'
        if parentTransform:
            parentTransform.children.append(rangeCircles)
        self.rootTransform = rangeCircles
        self.contextScaling = contextScaling
        rangeSteps = rangeSteps or self.defaultRangeSteps
        color = self.circleColor
        for i, radius in enumerate(rangeSteps):
            drawRadius = radius * self.contextScaling
            if i == 0:
                label = GetByLabel('UI/Inflight/Scanner/UnitAU')
            else:
                if radius >= const.AU:
                    label = FmtAmt(radius / const.AU)
                else:
                    label = FmtDist(radius, maxdemicals=0)
                baseAngle = math.pi / 2
                circum = drawRadius * baseAngle
                gapSize = 0.8 / circum
                gapAngle = gapSize * baseAngle
                for startAngle in (0.0,
                 math.pi * 0.5,
                 math.pi,
                 math.pi * 1.5):
                    lineSet = mapViewUtil.CreatePlanarLineSet()
                    rangeCircles.children.append(lineSet)
                    mapViewUtil.DrawCircularArc(lineSet, (0.0, 0.0, 0.0), drawRadius, startAngle=startAngle + gapAngle, angle=baseAngle - gapAngle * 2, lineWidth=0.1, startColor=color, endColor=color)
                    lineSet.SubmitChanges()

            self.AddRangeLabel(label, drawRadius)

        lineSet.SubmitChanges()

    def AddRangeLabel(self, text, radius):
        for x, z in [(0.0, radius),
         (radius, 0.0),
         (0.0, -radius),
         (-radius, 0.0)]:
            label = TransformableLabel(text, self.rootTransform, size=64, shadow=0, hspace=0)
            label.transform.translation = (x, 0.0, z)
            sx, sy, sz = label.transform.scaling
            label.transform.scaling = (sx / sy, 1.0, 0.0)
            label.SetDiffuseColor(self.labelColor)
            label.transform.useDistanceBasedScale = False
            label.transform.modifier = 0
            label.transform.rotation = geo2.QuaternionRotationSetYawPitchRoll(math.pi, -math.pi / 2, 0)


class SolarSystemInfoBox(LayoutGrid):
    default_columns = 2
    default_cellPadding = (0, 1, 6, 1)

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.nameLabel = EveLabelLarge(bold=True)
        self.AddCell(cellObject=self.nameLabel, colSpan=self.columns)
        EveLabelMedium(parent=self, text=GetByLabel('UI/Map/StarMap/SecurityStatus'))
        self.securityValue = EveLabelMedium(parent=self, bold=True, color=(1, 0, 0, 1))

    def LoadSolarSystemID(self, solarSystemID):
        self.nameLabel.text = cfg.evelocations.Get(solarSystemID).name
        securityStatus, color = FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(solarSystemID), True)
        self.securityValue.color = color
        self.securityValue.text = securityStatus
