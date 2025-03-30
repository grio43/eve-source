#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\modularHangarCapitalCamera.py
import math
import evecamera
import uthread
import logging
import blue
import geo2
import random as rnd
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from gametime import GetSecondsSinceSimTime, GetSimTime
import eve.client.script.ui.view.hangarBehaviours.modularHangarBehavioursConstants as hc
from carbonui.uicore import uicore
import evegraphics.settings as gfxsettings
from evetypes import GetGroupID
logger = logging.getLogger(__name__)

class ModularHangarCapitalCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_MODULARHANGAR_CAPITAL
    isBobbingCamera = False
    name = 'ModularHangarCapitalCamera'
    minFov = 0.3
    maxFov = 1.0

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.model = None
        self.atPosition = (0.0, 0.0, 0.0)
        self.camStartPos = (0.0, 0.0, 0.0)
        self.camStartPoi = (0.0, 0.0, 0.0)
        self.poiTarget = (0.0, 0.0, 0.0)
        self.camStartAngle = [0.0, 0.0]
        self.typeID = 0
        self.camSpeed = 1.0
        self.fov = 1.0
        self.isRotating = 0
        self.kMinYaw = -100.0
        self.kMaxYaw = 100
        self.kMinPitch = -100.0
        self.kMaxPitch = 100
        self.maxFov = 2.0
        self.yawTargetMapped = 0.0
        self.pitchTargetMapped = 0.0
        self.lerpingIntoPosition = False
        self.firstShip = True

    def SetCurrentShipSizeClass(self, sizeClass):
        pass

    def SetRotating(self, isTrue):
        self.isRotating = isTrue

    def SetFlightValueMap(self, exit1, hallway1, hallway2, exit2, dockPos):
        pass

    def ClearRefs(self):
        self.model = None

    def SetShip(self, model, typeID):
        self.lerpingIntoPosition = True
        uicore.animations.StopAllAnimations(self)
        self.model = model
        self.typeID = typeID
        self._configureCameraStartLocations(typeID)
        if not self.orbitUpdateThread:
            self.orbitUpdateThread = uthread.new(self.CapitalOrbitUpdateThread)

    def _configureCameraStartLocations(self, typeID, wasOrbiting = False):
        pos = hc.CAPITAL_CAMERA_DEFAULT_START_POSITION
        startSettings = (pos, pos, 1.0)
        groupID = GetGroupID(typeID)
        if groupID in hc.CAPITAL_CAMERA_POSITION_MAP:
            settingsVector = hc.CAPITAL_CAMERA_POSITION_MAP[groupID]
            if not wasOrbiting:
                startSettings = rnd.choice(settingsVector)
            else:
                normalizedPointVectors = []
                modelPos = self.model.modelWorldPosition
                for each in settingsVector:
                    normalizedPointVectors.append(geo2.Vec3Normalize((each[0][0] - modelPos[0], each[0][1] - modelPos[1], 0.0)))

                closestDist = 10
                mouseTargetMapNormalized = geo2.Vec3Normalize((self.yawTargetMapped, self.pitchTargetMapped, 0.0))
                startSettingIndex = 0
                for i, each in enumerate(normalizedPointVectors):
                    dist = geo2.Vec3DistanceSq(mouseTargetMapNormalized, each)
                    if dist < closestDist:
                        closestDist = dist
                        startSettingIndex = i

                startSettings = settingsVector[startSettingIndex]
        pos = startSettings[0]
        poi = startSettings[1]
        self.SetFovTarget(startSettings[2])
        self.kFovSpeed = 1.5
        self.camStartPoi = poi
        self.poiTarget = poi
        self.camStartPos = pos
        self.orbitTarget = pos

    def PlaceShip(self, pos):
        pass

    def AnimEnterHangar(self, model, startPos, endPos, duration = 5.0):
        self.CalculateOrbitTarget()
        self.SetEyePosition(self.orbitTarget)

    def Orbit(self, dx = 0, dy = 0):
        self.lerpingIntoPosition = False
        if gfxsettings.Get(gfxsettings.UI_CAMERA_INVERT_Y):
            dy *= -1
        self.yawTargetMapped = max(min(self.yawTargetMapped - dx, 0.5), -1.0)
        self.pitchTargetMapped = max(min(self.pitchTargetMapped + dy / 2.0, 1.0), -0.5)
        self.orbitTarget = self.CalculateOrbitTarget()
        self.poiTarget = self.model.modelWorldPosition
        self.camSpeed = 1.0
        self.kFovSpeed = 5.0
        self.SetFovTarget(1.0)
        if not self.orbitUpdateThread:
            self.orbitUpdateThread = uthread.new(self.CapitalOrbitUpdateThread)

    def ResetRotate(self):
        if self.orbitUpdateThread:
            self._configureCameraStartLocations(self.typeID, wasOrbiting=True)
            self.lerpingIntoPosition = True
        self.yawTargetMapped = 0
        self.pitchTargetMapped = 0
        self.camSpeed = 0.1

    def CalculateOrbitTarget(self):
        boundingSphereSize = self.model.GetBoundingSphereRadius() or 5000.0
        offset = geo2.Vec3Add((0.0, 0.0, 1.4 * boundingSphereSize), (0.0, 0.0, 500.0))
        quaternionRotation = geo2.QuaternionRotationArc((0.0, 0.0, 1.0), geo2.Vec3Normalize((0.38 * self.yawTargetMapped, 0.26 * self.pitchTargetMapped, 1.0)))
        finalPos = geo2.QuaternionTransformVector(quaternionRotation, offset)
        camVector = geo2.Vec3Add(self.model.modelWorldPosition, finalPos)
        return camVector

    def CapitalOrbitUpdateThread(self):
        try:
            while True:
                if self.orbitTarget is None:
                    break
                lerpSpeed = 0.01 if self.lerpingIntoPosition else 0.1
                self.SetEyePosition(geo2.Vec3Lerp(self._eyePosition, self.orbitTarget, lerpSpeed))
                if not self.lerpingIntoPosition:
                    self.poiTarget = self.model.modelWorldPosition
                self.atPosition = geo2.Vec3Lerp(self.atPosition, self.poiTarget, lerpSpeed)
                dist1 = geo2.Vec3DistanceSqD(self.atPosition, self.poiTarget)
                dist2 = geo2.Vec3DistanceSqD(self._eyePosition, self.orbitTarget)
                if dist1 < 5.0 and dist2 < 5.0:
                    break
                blue.synchro.Yield()

        finally:
            self.orbitUpdateThread = None

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.model = None

    def Update(self):
        BaseSpaceCamera.Update(self)

    def SkipLerp(self):
        self.atPosition = self.poiTarget
        self.SetEyePosition(self.orbitTarget)

    def GetIsChangingShip(self):
        return False

    def SetMinMaxZoomDefaults(self, minZoom, maxZoom):
        pass

    def SetHangarAnimationParameters(self, yaw, pitch, zoom, fov):
        pass

    def Zoom(self, dz):
        pass

    def SetZoomTarget(self, proportion):
        pass

    def _AnimEnterHangarFOV(self, duration):
        pass

    def _AnimEnterHangarZoom(self, duration, model):
        pass

    def _AnimSwitchShipsZoom(self, duration, model):
        pass

    def _AnimZoom(self, duration, zoom0, zoom1):
        pass

    def UpdateMinMaxZoom(self):
        pass

    def SetZoom(self, proportion):
        pass

    def EnforceMaxZoom(self):
        pass

    def _AnimEnterHangarYaw(self, duration):
        pass

    def _AnimEnterHangarPitch(self, duration):
        pass

    def AnimSwitchShips(self, model, startPos, endPos, duration = 5.0):
        pass
