#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPreviewScene.py
import math
import evetypes
import signals
import trinity
import blue
import mathext
import uthread2
import geo2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.ui.camera.sceneContainerCamera import SceneContainerCamera
from eve.client.script.ui.control.scenecontainer import SceneContainer
from eve.client.script.ui.shared.info.shipInfoConst import TALL_SHIP_POSITION_REPLACEMENTS, WIDE_SHIP_POSITION_REPLACEMENTS, SHIP_POSITIONS, FACTION_BACKGROUND_LOGOS_IDS, LIGHT_RIG_GRAPHIC_ID, get_faction_background
from eve.client.script.ui.shared.skins.controller import GetSkinnedShipModel
from fsdBuiltData.common.graphicIDs import GetGraphicFile
import evegraphics.utils as gfxutils
SCENE_GRAPHICID = 26811
ENVIRONMENT_VFX_GRAPHICID = 27580
SHIP_MATERIALIZATION_MULTIEFFECT_GRAPHICID = 27581
TRANSITION_ZOOM_DEFAULT = 0.2
MINIMUM_ZOOM_DISTANCE_DEFAULT = 5000
ZOOM_RANGE = [1.5, 3.5]
ZOOM_RANGES_BY_RATIO = [(1.0, [2.1, 4.5]), (1.35, [1.8, 3.5]), (1.5, [1.6, 3.5])]

class ShipInfoPreviewSceneContainer(SceneContainer):

    def __init__(self, **kwargs):
        super(ShipInfoPreviewSceneContainer, self).__init__(**kwargs)
        self.environment = None
        self.shipReplacementMultiEffect = None
        self.model = None
        self.oldModel = None
        self.PrepareSpaceScene()
        self._targetCenterOffset = 0.0
        self._targetVerticalOffset = 0.0
        self._targetZoom = 0.0
        self._positionID = None
        self.radius = 1.0
        self._update_thread = uthread2.StartTasklet(self._update)
        self.additionalBackgroundTexture = None
        self.skin_state = None
        self._loaded = False
        self._lastBGType = -1.0
        self._pendingLoadData = None
        self._async_load_task = None
        self.on_load_complete = signals.Signal('ShipInfoPreviewSceneContainer_LoadComplete')

    def PrepareCamera(self):
        self.camera = ShipInfoPreviewCamera()
        self.camera.OnActivated()

    def PrepareSpaceScene(self, scenePath = None):
        if scenePath is None:
            scenePath = GetGraphicFile(SCENE_GRAPHICID)
        super(ShipInfoPreviewSceneContainer, self).PrepareSpaceScene(scenePath=scenePath)
        if not self.scene:
            return
        if not self.scene.postprocess:
            self.scene.postprocess = trinity.Tr2PostProcess2()
        self.bgEnvironment = blue.resMan.LoadObject('res:/dx9/scene/showinfo/showinfo_logo_background_01a.red')
        self.AddToScene(self.bgEnvironment, clear=0)
        self.bgEnvironment.StartControllers()

    def add_background_texture(self, texturePath):
        if self.additionalBackgroundTexture:
            self.remove_background_texture()
        self.additionalBackgroundTexture = blue.resMan.LoadObject('res:/dx9/scene/showinfo/showinfo_logo_background_01a.red')
        param = self.additionalBackgroundTexture.externalParameters.FindByName('Logo_resourcePath')
        param.SetValue(texturePath)
        child = self.additionalBackgroundTexture.effectChildren[0]
        trans = child.transformModifiers[2]
        trans.translation = (0, 0, -140000)
        self.AddToScene(self.additionalBackgroundTexture, clear=0)
        return self.additionalBackgroundTexture

    def remove_background_texture(self):
        if not self.additionalBackgroundTexture:
            return
        self.RemoveFromScene(self.additionalBackgroundTexture)
        self.additionalBackgroundTexture = None

    def _get_model_offset(self, model, typeID):
        modelOffset = getattr(model, 'shapeEllipsoidCenter', (0.0, 0.0, 0.0))
        locatorSets = getattr(model, 'locatorSets', None)
        if locatorSets:
            lookAtLocator = locatorSets.FindByName('camera_look_at')
            if lookAtLocator is not None and len(lookAtLocator.locators) > 0:
                modelOffset = lookAtLocator.locators[0][0]
        invertedModelOffset = geo2.Vec3Scale(modelOffset, -1.0)
        return invertedModelOffset

    def preview_ship(self, typeID, subSystems = [], skin_state = None, skip_repositioning = False, snap = True, skip_animation = False):
        if self._async_load_task:
            self._pendingLoadData = (self._load_ship,
             typeID,
             subSystems,
             skin_state,
             skip_repositioning,
             snap,
             skip_animation)
        else:
            self._async_load_task = uthread2.StartTasklet(self._load_ship, typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation)

    def preview_skin(self, typeID, subSystems = [], skin_state = None, skip_repositioning = False, snap = False, skip_animation = True):
        if self._async_load_task:
            self._pendingLoadData = (self._load_skin,
             typeID,
             subSystems,
             skin_state,
             skip_repositioning,
             snap,
             skip_animation)
        else:
            self._async_load_task = uthread2.StartTasklet(self._load_skin, typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation)

    def _load_complete(self, snap = True, skip_animation = False):
        if self._pendingLoadData:
            func, typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation = self._pendingLoadData
            self._pendingLoadData = None
            func(typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation)
        else:
            self.on_load_complete(snap, skip_animation)
            self._async_load_task = None

    def _load_ship(self, typeID, subSystems = [], skin_state = None, skip_repositioning = False, snap = True, skip_animation = False):
        self.set_faction_background(evetypes.GetFactionID(typeID))
        self._load(typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation)

    def _load_skin(self, typeID, subSystems = [], skin_state = None, skip_repositioning = False, snap = False, skip_animation = True):
        self._load(typeID, subSystems, skin_state, skip_repositioning, snap, skip_animation)

    def _load(self, typeID, subSystems = [], skin_state = None, skip_repositioning = False, snap = False, skip_animation = False):
        self._loaded = False
        if self.model and self.model in self.scene.objects:
            self.scene.objects.remove(self.model)
            self.model = None
        multiHullTypeIDList = None
        if subSystems and len(subSystems) > 0:
            multiHullTypeIDList = subSystems
        if skin_state is not None:
            self.model = GetSkinnedShipModel(skin=skin_state, typeID=typeID, multiHullTypeIDList=multiHullTypeIDList)
        self.skin_state = skin_state
        if not self.model:
            modelDNA = gfxutils.BuildSOFDNAFromTypeID(typeID, multiHullTypeIDList=multiHullTypeIDList)
            space_object_factory = GetSofService().spaceObjectFactory
            self.model = space_object_factory.BuildFromDNA(modelDNA)
        if self.destroyed:
            return
        self.model.rotationCurve = trinity.Tr2RotationAdapter()
        self.model.translationCurve = trinity.Tr2TranslationAdapter()
        self.model.translationCurve.value = self._get_model_offset(self.model, typeID)
        if self.model.boosters:
            self.model.boosters.alwaysOn = True
            self.model.boosters.alwaysOnIntensity = 0.7
        while len(self.model.observers) > 0:
            self.model.observers.pop()

        self.model.FreezeHighDetailMesh()
        if hasattr(self.model, 'dirtLevel'):
            self.model.dirtLevel = -1.5
        self.scene.objects.append(self.model)
        self.model.StartControllers()
        lightRigAsset = GetGraphicFile(LIGHT_RIG_GRAPHIC_ID)
        lightRig = trinity.Load(lightRigAsset)
        self.model.effectChildren.append(lightRig)
        trinity.WaitForResourceLoads()
        maxDelay = 5.0
        checkDelay = 50.0
        currentDelay = 0.0
        while not self.destroyed:
            if not self.model:
                return
            if max(self.model.generatedShapeEllipsoidRadius) != -1:
                break
            if currentDelay > maxDelay:
                break
            blue.synchro.SleepWallclock(checkDelay)
            currentDelay += checkDelay / 1000.0

        self._loaded = True
        if self.destroyed:
            self._pendingLoadData = None
            self._async_load_task = None
            return
        if not skip_repositioning:
            self._fit_model_in_view(self.model)
            self.camera.animate_camera_fov(0.8, 1.1)
        self._load_complete(snap, skip_animation)

    def _fit_model_in_view(self, model):
        if model is None or not self.camera:
            return
        self.radius = model.GetBoundingSphereRadius() + 1
        zoom_range = self._get_zoom_range_for_model()
        self.SetZoomRange(zoom_range)
        self.SetZoom(TRANSITION_ZOOM_DEFAULT)
        self._targetZoom = TRANSITION_ZOOM_DEFAULT
        self.camera.SetInnerBoundRadius(self.model.shapeEllipsoidRadius)
        self.camera.centerOffset = self._targetCenterOffset = 0.5
        self.camera.verticalOffset = self._targetVerticalOffset = 0
        self.camera.atPosition = (0.0, 0.0, 0.0)

    def _get_long_axis_ratio(self):
        shield = self.model.generatedShapeEllipsoidRadius
        longAxisIdx = shield.index(max(shield))
        longAxis = shield[longAxisIdx]
        total = 0.0
        for idx, axis in enumerate(shield):
            if idx == longAxisIdx:
                continue
            total += longAxis / axis

        return total / 2.0

    def _get_zoom_range_for_model(self):
        longAxisRatio = self._get_long_axis_ratio()
        chosen_zoom_range = [1.0, 1.0]
        for ratioStep, zoom_range in ZOOM_RANGES_BY_RATIO:
            if ratioStep > longAxisRatio:
                return chosen_zoom_range
            chosen_zoom_range = zoom_range

        return chosen_zoom_range

    def SetZoomRange(self, zoomRange):
        maxRenderDist = self.camera.farClip or 400000.0
        min_zoom = zoomRange[0] * self.radius
        max_zoom = min(zoomRange[1] * self.radius, maxRenderDist - 2 * self.radius)
        self.SetMinMaxZoom(min_zoom, max_zoom)

    def update_offset(self):
        self.camera.centerOffset = mathext.lerp(self.camera.centerOffset, self._targetCenterOffset, 0.3)
        self.camera.verticalOffset = mathext.lerp(self.camera.verticalOffset, self._targetVerticalOffset, 0.3)

    @property
    def loaded(self):
        return self._loaded

    @property
    def centerOffset(self):
        return self._targetCenterOffset

    @centerOffset.setter
    def centerOffset(self, value):
        self._targetCenterOffset = value

    def SetCenterOffset(self, value):
        self.camera.centerOffset = self._targetCenterOffset = value

    @property
    def verticalOffset(self):
        return self._targetVerticalOffset

    @verticalOffset.setter
    def verticalOffset(self, value):
        self._targetVerticalOffset = value

    def _update(self):
        while not self.destroyed:
            self.update_offset()
            uthread2.Sleep(0.001)

    def set_faction_background(self, factionID):
        newBGType = get_faction_background(factionID)
        if newBGType == self._lastBGType:
            self.bgEnvironment.Start()
            return
        self._lastBGType = newBGType
        self.bgEnvironment.SetControllerVariable('Faction', newBGType)
        while len(self.bgEnvironment.effectChildren) == 0:
            uthread2.Sleep(0.01)

        while len(self.bgEnvironment.effectChildren[0].objects) == 0:
            uthread2.Sleep(0.01)

        backgroundLogo = self.bgEnvironment.effectChildren[0].objects[0]
        trans = backgroundLogo.transformModifiers.Find('trinity.EveChildModifierSRT')[0]
        trans.translation = (28000.0, -12000.0, -99000.0)

    def set_ship_state(self, tabID):
        pass

    def position_ship(self, positionID, duration, initialize = False, sound = None, soundOffset = 0):
        if not self._loaded:
            return
        if self.is_tall() and positionID in TALL_SHIP_POSITION_REPLACEMENTS:
            positionID = TALL_SHIP_POSITION_REPLACEMENTS[positionID]
        elif self.is_wide() and positionID in WIDE_SHIP_POSITION_REPLACEMENTS:
            positionID = WIDE_SHIP_POSITION_REPLACEMENTS[positionID]
        if positionID == self._positionID:
            return
        self._positionID = positionID
        pitch, yaw = SHIP_POSITIONS[positionID]
        if initialize:
            self.set_camera_angle_deg(pitch, yaw)
        else:
            self.turn_camera_deg(pitch, yaw, duration)
            if sound:
                startSignal, stopSignal = sound
                PlaySound(startSignal)
                uthread2.StartTasklet(self._stop_sound, duration - soundOffset, stopSignal)

    def zoom_to(self, targetZoom, duration):
        animations.StopAllAnimations(self)
        animations.MorphScalar(self, 'zoom', self.zoom, targetZoom, duration)

    def _stop_sound(self, delay, signal):
        uthread2.Sleep(delay)
        PlaySound(signal)

    def is_tall(self):
        shield = self.model.generatedShapeEllipsoidRadius
        longAxis = shield.index(max(shield))
        if longAxis == 1:
            return True
        return False

    def is_wide(self):
        shield = self.model.generatedShapeEllipsoidRadius
        longAxis = shield.index(max(shield))
        if longAxis == 0:
            return True
        return False

    def get_bounding_sphere_radius(self):
        if self.model:
            return self.model.GetBoundingSphereRadius()
        return 0

    def turn_camera_deg(self, pitch, yaw, duration):
        pitchRad = math.radians(pitch)
        yawRad = math.radians(yaw)
        self.turn_camera(pitchRad, yawRad, duration)

    def turn_camera(self, pitch, yaw, duration):
        self.camera.turn_camera(pitch, yaw, duration, False)

    def set_camera_angle_deg(self, pitch, yaw):
        pitchRad = math.radians(pitch)
        yawRad = math.radians(yaw)
        self.set_camera_angle(pitchRad, yawRad)

    def set_camera_angle(self, pitch, yaw):
        self.camera.set_angle(pitch, yaw)


class ShipInfoPreviewCamera(SceneContainerCamera):

    def __init__(self):
        super(ShipInfoPreviewCamera, self).__init__()
        self.kFovSpeed = 1.0
        self.originalPitch = 0.0
        self.originalYaw = 0.0
        self.lastAnimDuration = 0.0
        self.allowFreeInspection = True

    def UpdateViewportSize(self, width, height):
        if height:
            self._aspectRatio = float(width) / height

    def return_to_original_angle(self):
        self._turn_camera(self.originalPitch, self.originalYaw, self.lastAnimDuration)

    def turn_camera(self, pitch, yaw, duration, allowFreeInspection):
        self.originalPitch = pitch
        self.originalYaw = yaw
        self.lastAnimDuration = duration
        self.allowFreeInspection = allowFreeInspection
        self._turn_camera(pitch, yaw, duration)

    def _turn_camera(self, pitch, yaw, duration):
        self.StopUpdateThreads(skipFov=True)
        self.StopAnimations()
        yawDist = self.yaw - yaw
        if math.fabs(yawDist) > math.pi:
            if yawDist < 0:
                yaw = yaw - 2 * math.pi
            else:
                yaw = yaw + 2 * math.pi
        if math.fabs(self.pitch - pitch) > math.pi:
            pitch = pitch - 2 * math.pi
        animations.MorphScalar(self, 'yaw', self.yaw, yaw, duration=duration)
        animations.MorphScalar(self, 'pitch', self.pitch, pitch, duration=duration)

    def set_angle(self, pitch, yaw):
        self.StopUpdateThreads(skipFov=True)
        self.StopAnimations()
        self.pitch = pitch
        self.yaw = yaw

    def animate_camera_fov(self, finalValue, startValue = None):
        if startValue is not None:
            self.fov = startValue
        self.SetFovTarget(finalValue)
