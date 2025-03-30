#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\map\solarsystemscene.py
from carbonui.uianimations import animations
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.shared.mapView import mapViewUtil
from fsdBuiltData.common.graphicIDs import GetGraphicFile
import geo2
import logging
import math
import trinity
log = logging.getLogger(__name__)

class SolarSystemScene(SceneContainer):
    __notifyevents__ = SceneContainer.__notifyevents__ + ['OnProjectDiscoveryRescaled', 'OnDataLoaded']

    def ApplyAttributes(self, attributes):
        super(SolarSystemScene, self).ApplyAttributes(attributes)
        self._current_time = 0
        self._max_period = 30
        self._transit_selection_tool = attributes.get('transitSelectionTool')
        self.systemMapSvc = sm.GetService('systemmap')
        self.scene = trinity.EveSpaceScene()
        self._map_root = trinity.EveRootTransform()
        self._map_root.name = 'MapRoot'
        self.scene.objects.append(self._map_root)
        self.systemMapTransform = trinity.EveTransform()
        self.solarsystemID = 30002955
        self.solarsystemID = 30002353
        self.systemMapTransform.name = 'solarsystem_%s' % self.solarsystemID
        self._map_root.children.append(self.systemMapTransform)
        self.load_solar_system()
        self.DisplaySpaceScene(trinity.RM_ALPHA_ADDITIVE)
        if self._transit_selection_tool:
            self._transit_selection_tool.on_selection_change.connect(self.update_transits)
        self.update_transits()

    def OnDataLoaded(self, data):
        self._max_period = data[-1][0] - data[0][0]

    def Close(self):
        if self._transit_selection_tool:
            self._transit_selection_tool.on_selection_change.disconnect(self.update_transits)
        self.StopAnimations()
        super(SolarSystemScene, self).Close()

    def PrepareCamera(self):
        super(SolarSystemScene, self).PrepareCamera()
        self.camera.zoomDistance = 1000
        self.camera.pitch = 1.35

    def OnProjectDiscoveryRescaled(self, ratio):
        pass

    def load_solar_system(self):
        solarSystemData = self.systemMapSvc.GetSolarsystemData(self.solarsystemID)
        for celestialObject in solarSystemData:
            if celestialObject.groupID == const.groupSun:
                sunGraphicFilePath = GetGraphicFile(cfg.mapSystemCache[self.solarsystemID].sunFlareGraphicID)
                sunGraphicFile = trinity.Load(sunGraphicFilePath)
                self.create_sun(sunGraphicFile)

    def create_sun(self, sunGraphic):

        def GetEffectParameter(effect, parameterName):
            for name, value in effect.constParameters:
                if name == parameterName:
                    return value

        scaling = 1.0 / 0.01
        sunTransform = trinity.EveTransform()
        sunTransform.name = 'Sun'
        sunTransform.scaling = (scaling, scaling, scaling)
        self.systemMapTransform.children.append(sunTransform)
        for each in sunGraphic.mesh.additiveAreas:
            if 'flare' not in each.name.lower() and 'rainbow' not in each.name.lower():
                transform = trinity.EveTransform()
                size = GetEffectParameter(each.effect, 'Size')
                if size is None:
                    continue
                size = (size[0], size[1], size[2])
                transform.scaling = size
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
                effect.parameters.append(diffuseColor)
                diffuseColor = diffuseColor
                diffuseMap = trinity.TriTextureParameter()
                diffuseMap.name = 'DiffuseMap'
                diffuseMap.resourcePath = each.effect.resources[0].resourcePath
                effect.resources.append(diffuseMap)
                try:
                    color = GetEffectParameter(each.effect, 'Color')
                    diffuseColor.value = color
                except:
                    continue

                sunTransform.children.append(transform)

    def update_transits(self, *args, **kwargs):
        if not self.camera:
            return
        transit_selections = self._transit_selection_tool.get_selections()
        periods = self._get_placeholder_periods(transit_selections)
        for i in xrange(len(self.systemMapTransform.children) - 1):
            self.systemMapTransform.children.pop()

        self._orbits = []
        for transit, period in zip(transit_selections, periods):
            orbit = OrbitCircle(transit, self._current_time, (0, 0, 0), self.systemMapTransform, placeholder_period=period)
            self._orbits.append(orbit)

        max_orbit = max([ orbit.orbit_radius for orbit in self._orbits ]) * 3 if self._orbits else 1000
        animations.MorphScalar(self.camera, 'zoomDistance', self.camera.zoomDistance, max_orbit, duration=3)

    def _get_placeholder_periods(self, transit_selections):
        periods = []
        max_period = self._max_period
        for selection in transit_selections:
            period = selection.get_period_length()
            if period:
                periods.append(period)
            else:
                periods.append(max_period)
                max_period += 10

        return periods

    def update_time(self, current_time):
        self._current_time = current_time
        for orbit in self._orbits:
            orbit.update_time(current_time)


class OrbitCircle(object):

    def __init__(self, transit_selection, current_time, sun_position, parent_transform, placeholder_period = 30):
        self._place_holder_period = placeholder_period
        self._transit_selection = transit_selection
        self._sun_position = sun_position
        self._planet_transform = None
        self._parent_transform = parent_transform
        position = self.get_planet_position(current_time)
        self._line_set = mapViewUtil.CreateLineSet()
        parent_transform.children.append(self._line_set)
        mapViewUtil.DrawCircle(self._line_set, self._sun_position, self.radius, startColor=self._transit_selection.get_color(), endColor=self._transit_selection.get_color(), lineWidth=1.5)
        self._line_set.SubmitChanges()
        self.create_planet(position)

    def create_planet(self, position):
        self._planet_transform = trinity.EveTransform()
        self._planet_transform.name = 'Planet'
        self._planet_transform.translation = position
        self._planet_transform.scaling = (0.03, 0.03, 0.03)
        self._parent_transform.children.append(self._planet_transform)
        self._planet_transform.useDistanceBasedScale = True
        self._planet_transform.distanceBasedScaleArg1 = 1.0
        self._planet_transform.distanceBasedScaleArg2 = 0.0
        self._planet_transform.mesh = trinity.Tr2Mesh()
        self._planet_transform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        self._planet_transform.modifier = 1
        area = trinity.Tr2MeshArea()
        self._planet_transform.mesh.additiveAreas.append(area)
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

    def get_transit_selection(self):
        return self._transit_selection

    def update_time(self, current_time):
        self._planet_transform.translation = self.get_planet_position(current_time)

    def get_planet_position(self, current_time):
        start = self._transit_selection.get_center()
        length = self._transit_selection.get_period_length()
        length = length if length else self._place_holder_period
        t = (current_time - start) / length % 1
        degrees = t * 360
        length = (length + 5) * 20
        self.radius = length
        direction = geo2.Vec3Normalize((math.cos(math.radians(degrees)), 0, math.sin(math.radians(degrees))))
        direction = geo2.Vec3Scale(direction, self.radius)
        return geo2.Vec3Add(self._sun_position, direction)

    @property
    def orbit_radius(self):
        return self.radius
