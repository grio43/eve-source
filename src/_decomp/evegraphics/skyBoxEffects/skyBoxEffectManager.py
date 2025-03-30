#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\skyBoxEffects\skyBoxEffectManager.py
import logging
import trinity
from carbon.common.script.util.mathUtil import Lerp
import fsdBuiltData.client.skyBoxEffects as skyBoxEffectData
import geo2
from eve.common.lib.appConst import LIGHTYEAR
log = logging.getLogger(__name__)
SKYBOX_EFFECT_MULTIPLIER = 5000

class SkyBoxEffectManager(object):

    def __init__(self, system_positions):
        self.system_positions = system_positions
        self.loaded_effects = []

    def ClearEffects(self, scene = None):
        if scene:
            for effect in self.loaded_effects:
                self.RemoveEffectFromScene(effect, scene)

    @staticmethod
    def RemoveEffectFromScene(effect, scene):
        if effect in scene.backgroundObjects:
            scene.backgroundObjects.fremove(effect)

    def EnterSolarSystem(self, current_solar_system_id, scene, force_load_effects = False):
        self.loaded_effects = []
        current = self.system_positions[current_solar_system_id]
        for sky_box_effect_id, sky_box_effect in skyBoxEffectData.GetSkyBoxEffects().iteritems():
            solar_system_id = skyBoxEffectData.GetSkyBoxEffectSourceSolarSystem(sky_box_effect_id)
            if current_solar_system_id == solar_system_id:
                continue
            if solar_system_id is not None:
                target = self.system_positions[solar_system_id]
            else:
                target = skyBoxEffectData.GetSkyBoxEffectWorldPosition(sky_box_effect_id)
            distance_in_ly = geo2.Vec3DistanceD(current, target) / LIGHTYEAR
            scale = SkyBoxEffectManager.CalculateScale(distance_in_ly, sky_box_effect_id) * SKYBOX_EFFECT_MULTIPLIER
            if scale > 0.0:
                direction = geo2.Vec3Normalize(geo2.Vec3SubtractD(current, target))
                position = (direction[0], direction[1], -direction[2])
                position = geo2.Vec3ScaleD(position, SKYBOX_EFFECT_MULTIPLIER)
                effect = trinity.Load(skyBoxEffectData.GetSkyBoxEffectPath(sky_box_effect_id), nonCached=not force_load_effects)
                try:
                    effect.SetControllerVariable('DistanceRatio', 1.0 - SkyBoxEffectManager.GetDistLerpRatio(distance_in_ly, sky_box_effect_id))
                    effect.StartControllers()
                except AttributeError:
                    pass

                self.loaded_effects.append(effect)
                self.PlaceEffect(effect, scene, position, scale)

    @staticmethod
    def PlaceEffect(effect, scene, direction, scale):
        effect.scaling = (scale, scale, scale)
        effect.translation = direction
        scene.backgroundObjects.append(effect)

    @staticmethod
    def CalculateScale(distance, effect_id):
        near_scale = skyBoxEffectData.GetSkyBoxEffectNearScale(effect_id)
        far_scale = skyBoxEffectData.GetSkyBoxEffectFarScale(effect_id)
        return Lerp(near_scale, far_scale, SkyBoxEffectManager.GetDistLerpRatio(distance, effect_id))

    @staticmethod
    def GetDistLerpRatio(distance, effect_id):
        near_dist = skyBoxEffectData.GetSkyBoxEffectNearDistInLightYears(effect_id)
        far_dist = skyBoxEffectData.GetSkyBoxEffectFarDistInLightYears(effect_id)
        return float(distance - near_dist) / float(far_dist - near_dist)
