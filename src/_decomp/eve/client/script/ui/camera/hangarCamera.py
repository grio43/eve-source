#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\hangarCamera.py
import math
from eve.client.script.ui.camera.cameraUtil import GetInitialLookAtDistance
import evecamera
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import carbonui.const as uiconst
import geo2
from carbonui.uicore import uicore

class HangarCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_HANGAR
    isBobbingCamera = False
    name = 'HangarCamera'
    kMaxPitch = math.pi / 2.0 + math.pi / 50.0
    minFov = 0.3
    maxFov = 1.0
    hangarMinZoom = 2050.0
    hangarMaxZoom = 10.0

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.model = None
        self.HaAnimYaw = (14 * math.pi / 8, 9 * math.pi / 8)
        self.HaAnimPitch = (7 * math.pi / 16, self.kMaxPitch)
        self.HaAnimZoom = (1.2, 2.0)
        self.HaAnimFov = (0.7, self.default_fov)

    def SetShip(self, model, typeID):
        uicore.animations.StopAllAnimations(self)
        self.fov = 1.0
        self.model = model
        self.typeID = typeID
        self.UpdateMinMaxZoom()

    def PlaceShip(self, pos):
        self.atPosition = pos

    def AnimEnterHangar(self, model, startPos, endPos, duration = 5.0):
        self._AnimEnterHangarPitch(duration)
        self._AnimEnterHangarYaw(duration)
        self._AnimEnterHangarZoom(duration, model)
        self._AnimEnterHangarFOV(duration)

    def _AnimEnterHangarFOV(self, duration):
        self.fov = self.HaAnimFov[0]
        uicore.animations.MorphScalar(self, 'fov', self.HaAnimFov[0], self.HaAnimFov[1], duration=0.45 * duration, timeOffset=0.55 * duration)

    def _AnimEnterHangarZoom(self, duration, model):
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(self.HaAnimZoom[0] * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(self.HaAnimZoom[1] * dist)
        self.zoom = zoom0
        self._AnimZoom(duration, zoom0, zoom1)

    def _AnimSwitchShipsZoom(self, duration, model):
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(1.0 * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(1.2 * dist)
        self._AnimZoom(duration, zoom0, zoom1)

    def _AnimZoom(self, duration, zoom0, zoom1):
        zoom1 = min(zoom1, 1.0)
        self.zoom = zoom0
        cs = uicore.animations.MorphScalar(self, 'zoom', zoom0, zoom1, duration=duration, curveType=uiconst.ANIM_LINEAR)
        key = list(cs.curves[0].keys[0])
        key[3] = 0
        cs.curves[0].keys[0] = tuple(key)

    def UpdateMinMaxZoom(self):
        radius = self.model.boundingSphereRadius + geo2.Vec3Length(self.model.GetBoundingSphereCenter())
        maxZoom = max(self.hangarMaxZoom, 1.5 * radius)
        if maxZoom >= self.hangarMinZoom:
            maxZoom = 0.999 * self.hangarMinZoom
        minZoom = self.hangarMinZoom
        self.SetMinMaxZoom(minZoom, maxZoom)
        self.zoom = max(self.GetMinZoomProp(), min(self.zoom, 1.0))

    def _AnimEnterHangarYaw(self, duration):
        uicore.animations.MorphScalar(self, 'yaw', self.HaAnimYaw[0], self.HaAnimYaw[1], duration=duration, timeOffset=0)

    def _AnimEnterHangarPitch(self, duration):
        uicore.animations.MorphScalar(self, 'pitch', self.HaAnimPitch[0], self.HaAnimPitch[1], duration=duration)

    def AnimSwitchShips(self, model, startPos, endPos, duration = 5.0):
        self.atPosition = endPos
        uicore.animations.MorphScalar(self, 'yaw', 0.0, -math.pi / 10, duration=duration)
        uicore.animations.MorphScalar(self, 'pitch', math.pi / 2 + math.pi / 25, self.kMaxPitch, duration=duration)
        self._AnimSwitchShipsZoom(duration, model)
        uicore.animations.MorphScalar(self, 'fov', 0.7, self.default_fov, duration=duration)

    def Orbit(self, *args):
        BaseSpaceCamera.Orbit(self, *args)
        uicore.animations.StopAnimation(self, 'yaw')
        uicore.animations.StopAnimation(self, 'pitch')

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.model = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.model and self.model.translationCurve:
            atPos = self.model.translationCurve.currentValue
            diff = geo2.Vec3Subtract(atPos, self._atPosition)
            self.atPosition = atPos
            self.eyePosition = geo2.Vec3Add(self.eyePosition, diff)
            self.EnforceMaxZoom()

    def SetMinMaxZoomDefaults(self, minZoom, maxZoom):
        self.hangarMinZoom = minZoom
        self.hangarMaxZoom = maxZoom

    def SetHangarAnimationParameters(self, yaw, pitch, zoom, fov):
        self.HaAnimYaw = yaw
        self.HaAnimPitch = pitch
        self.HaAnimZoom = zoom
        self.HaAnimFov = (fov, self.HaAnimFov[1])
