#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScanHandler.py
import math
import weakref
import blue
import geo2
from eve.client.script.environment import nodemanager
import evecamera
import trinity
import uthread
from carbon.common.script.util.mathCommon import GetLesserAngleBetweenYaws
from carbonui.uianimations import animations
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import SCANMODE_CAMERA, IsDscanConeShown, GetScanAngle
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import COLOR_DSCAN
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.dockPanelConst import DOCKPANELID_SOLARSYSTEMMAP
from eve.client.script.ui.shared.mapView.mapViewUtil import CreatePlanarLineSet
from eve.common.lib.appConst import AU
from carbonui.uicore import uicore
LINE_WIDTH = 3500.0
MAX_SCANRANGE = 14.3 * const.AU
CONE_ROTATION_SPEED = math.pi / 2
CAMERAUPDATE_MAP_TO_SPACE = 1
CAMERAUPDATE_SPACE_TO_MAP = 2
TR2TM_NONE = 0
TR2TM_LOOK_AT_CAMERA = 3

class MapViewDirectionalScanHandler(object):
    __notifyevents__ = ['OnDirectionalScannerRangeChanged',
     'OnDirectionalScannerAngleChanged',
     'OnDirectionalScannerScanModeChanged',
     'OnDirectionalScannerShowCone',
     'OnDirectionalScanComplete']
    _systemMapHandler = None
    lineSetScaling = 1000000.0
    debugLineSet = None
    dScanTransform = None
    dScanSubTransform = None
    dScanLineSet = None

    def __init__(self, systemMapHandler):
        self.systemMapHandler = systemMapHandler
        sm.RegisterNotify(self)
        self.viewStateService = sm.GetService('viewState')
        self.sceneManager = sm.GetService('sceneManager')
        self.scanRange = settings.user.ui.Get('dir_scanrange', MAX_SCANRANGE / 1000.0) * 1000.0
        self.scanMode = None
        self.scanAngle = math.degrees(GetScanAngle())
        self.coneLineSets = []
        self.scanConeTransform = None
        self.scanConeHalfTransform = None
        self.scanConeFullTransform = None
        self._isConstructing = False
        uthread.new(self.DrawDirectionalScanCone)

    def StopHandler(self):
        sm.UnregisterNotify(self)
        if self.dScanTransform:
            uicore.animations.MorphVector3(self.dScanTransform, 'scaling', startVal=self.dScanTransform.scaling, endVal=(0, 0, 0), duration=0.2, callback=self._RemoveFromScene)
        else:
            self._RemoveFromScene()

    def ScanEffect(self):
        if not all((self.scanConeTransform, self.scanConeHalfTransform, self.scanConeFullTransform)):
            return
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectReturn)
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeHalfTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectHalfReturn)
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeFullTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectFullReturn)

    def _ScanEffectReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def _ScanEffectHalfReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeHalfTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def _ScanEffectFullReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeFullTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def _RemoveFromScene(self):
        if self.systemMapHandler:
            if self.dScanTransform in self.systemMapHandler.systemMapTransform.children:
                self.systemMapHandler.systemMapTransform.children.remove(self.dScanTransform)
        self.dScanTransform = None
        self.dScanSubTransform = None
        self.dScanUpdateTimer = None
        self.systemMapHandler = None

    def GetPosition(self):
        if self.dScanTransform:
            return self.dScanTransform.translation

    def OnDirectionalScannerRangeChanged(self, scanRange):
        self.scanRange = scanRange
        self.DrawDirectionalScanCone()

    def OnDirectionalScannerAngleChanged(self, scanAngle):
        self.scanAngle = math.degrees(scanAngle)
        self.DrawDirectionalScanCone()

    def OnDirectionalScannerScanModeChanged(self, newScanMode):
        if newScanMode != self.scanMode:
            self.scanMode = newScanMode
            self.DrawDirectionalScanCone()
            if newScanMode == SCANMODE_CAMERA:
                self._SetScanModeCamera()
            self.OnCameraUpdate()

    def _SetScanModeCamera(self):
        endRotation = self.GetSystemMapCameraRotation()
        duration = self.GetRotationDurationFromQuaternions(self.dScanTransform.rotation, endRotation)
        self.systemMapHandler.mapView.LookAtEgoMarker(duration)
        animations.MorphQuaternion(self.dScanTransform, 'rotation', startVal=self.dScanTransform.rotation, endVal=endRotation, duration=duration)

    def OnDirectionalScannerShowCone(self, displayState):
        if self.dScanSubTransform:
            self.dScanSubTransform.display = displayState

    def OnDirectionalScanComplete(self, *args):
        self.ScanEffect()

    def GetSystemMapCamera(self):
        return self.systemMapHandler.mapView.camera

    def GetSystemMapCameraRotation(self):
        camera = self.GetSystemMapCamera()
        return camera.GetRotationQuat()

    def GetSpaceCameraViewVector(self):
        spaceCamera = self.GetSpaceCamera()
        return spaceCamera.GetLookAtDirection()

    def GetPointOfInterestOverride(self):
        return self.dScanTransform.worldTransform[3][:3]

    def SetScanTarget(self, scanVector):
        oldScanVector = self.GetSpaceCameraViewVector()
        animations.StopAnimation(self.dScanTransform, 'rotation')
        duration = self.GetRotationDurationFromVectors(oldScanVector, scanVector)
        self.AlignSpaceCameraToViewVector(scanVector, duration)

    @apply
    def spaceCameraOrbit():

        def fget(self):
            spaceCamera = self.GetSpaceCamera()
            return (spaceCamera.GetYaw(), spaceCamera.GetPitch())

        def fset(self, yaw_pitch):
            y, p = yaw_pitch
            spaceCamera = self.GetSpaceCamera()
            spaceCamera.SetYaw(y)
            spaceCamera.SetPitch(p)

        return property(**locals())

    @apply
    def systemMapHandler():

        def fget(self):
            if self._systemMapHandler:
                return self._systemMapHandler()

        def fset(self, value):
            if value:
                self._systemMapHandler = weakref.ref(value)
            else:
                self._systemMapHandler = None

        return property(**locals())

    def DrawDirectionalScanCone(self):
        if self._isConstructing or not self.systemMapHandler:
            return
        scanAngle = self.scanAngle
        scanRange = float(self.scanRange)
        if self.dScanLineSet is None:
            self._ConstructConesAndLines()
        self.dScanLineSet.ClearLines()
        self.scanConeHalfTransform.display = False
        self.scanConeFullTransform.display = False
        self.scanConeTransform.display = False
        if scanAngle < 180.0:
            self.ShowCone(scanAngle, scanRange)
        elif scanAngle < 360.0:
            self.ShowHalfSphere(scanRange)
        else:
            self.ShowSphere(scanRange)
        self.dScanLineSet.SubmitChanges()

    def _ConstructConesAndLines(self):
        self._isConstructing = True
        self._ConstructCones()
        self._ConstructLineSet()
        blue.synchro.Yield()
        self._isConstructing = False

    def ShowSphere(self, scanRange):
        self.scanConeFullTransform.scaling = (-scanRange, -scanRange, -scanRange)
        self.scanConeFullTransform.display = True

    def ShowHalfSphere(self, scanRange):
        self.scanConeHalfTransform.scaling = (-scanRange, -scanRange, -scanRange)
        self.scanConeHalfTransform.display = True

    def ShowCone(self, scanAngle, scanRange):
        scanAngleRad = math.radians(scanAngle)
        scanAngleCos = math.cos(scanAngleRad * 0.5)
        centerLineDistance = AU
        while centerLineDistance < scanRange:
            step = centerLineDistance * scanAngleCos
            radius = math.tan(scanAngleRad * 0.5) * step
            mapViewUtil.DrawCircle(self.dScanLineSet, (0, step / self.lineSetScaling, 0), radius / self.lineSetScaling, arcSegments=2, lineWidth=LINE_WIDTH, startColor=COLOR_DSCAN, endColor=COLOR_DSCAN)
            centerLineDistance += 2 * AU

        self.DrawConeSphereLineSegments(scanAngleRad, scanRange)
        z = scanRange * scanAngleCos
        endCapAngle = scanAngleRad * 0.5
        radius = scanRange * math.sin(endCapAngle)
        self.scanConeTransform.scaling = (radius * 2, z, radius * 2)
        self.scanConeTransform.display = True

    def DrawConeSphereLineSegments(self, scanAngleRad, scanRange):
        pCenter = (0, scanRange / self.lineSetScaling, 0)
        mat = geo2.MatrixRotationZ(scanAngleRad * 0.45)
        p1 = geo2.Vec3Transform(pCenter, mat)
        mat = geo2.MatrixRotationZ(scanAngleRad * 0.25)
        p2 = geo2.Vec3Transform(pCenter, mat)
        mat = geo2.MatrixRotationZ(scanAngleRad * 0.04)
        p3 = geo2.Vec3Transform(pCenter, mat)
        lineWidth = LINE_WIDTH * scanAngleRad * 3.0 * (scanRange / MAX_SCANRANGE)
        numSegments = 8
        for i in xrange(numSegments):
            self.DrawSpheredLineRotated(p1, p2, p3, float(i) / numSegments, lineWidth)

    def DrawSpheredLineRotated(self, p1, p2, p3, angle, lineWidth):
        mat = geo2.MatrixRotationY(angle * 2 * math.pi)
        p1 = geo2.Vec3Transform(p1, mat)
        p2 = geo2.Vec3Transform(p2, mat)
        p3 = geo2.Vec3Transform(p3, mat)
        self.dScanLineSet.AddSpheredLineCrt(p1, (0, 0, 0, 0), p2, COLOR_DSCAN, (0, 0, 0), lineWidth)
        self.dScanLineSet.AddSpheredLineCrt(p2, COLOR_DSCAN, p3, (0, 0, 0, 0), (0, 0, 0), lineWidth)

    def _ConstructCones(self):
        self.dScanTransform = trinity.EveTransform()
        self.dScanTransform.name = 'dScanTransform'
        self.systemMapHandler.systemMapTransform.children.append(self.dScanTransform)
        self.systemMapHandler.SetupMyPositionTracker(self.dScanTransform)
        self.dScanSubTransform = trinity.EveTransform()
        self.dScanSubTransform.name = 'dScanSubTransform'
        self.dScanSubTransform.display = IsDscanConeShown()
        self.dScanTransform.children.append(self.dScanSubTransform)
        self.scanConeTransform = trinity.Load('res:/dx9/model/UI/scancone.red')
        self.scanConeTransform.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, -math.pi / 2, 0.0)
        self.dScanSubTransform.children.append(self.scanConeTransform)
        self.scanConeHalfTransform = trinity.Load('res:/dx9/model/UI/scanconehalfsphere.red')
        self.dScanSubTransform.children.append(self.scanConeHalfTransform)
        self.scanConeFullTransform = trinity.Load('res:/dx9/model/UI/scanconesphere.red')
        self.dScanSubTransform.children.append(self.scanConeFullTransform)

    def _ConstructLineSet(self):
        self.dScanLineSet = CreatePlanarLineSet(texturePath='res:/dx9/texture/ui/linePlanarSmoothAdditive.dds')
        self.dScanLineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
        self.dScanLineSet.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, -math.pi / 2, 0.0)
        self.dScanLineSet.additive = True
        self.dScanSubTransform.children.append(self.dScanLineSet)

    def GetSpaceCamera(self):
        cam = self.sceneManager.GetActiveSpaceCamera()
        if cam is None or cam.cameraID == evecamera.CAM_JUMP:
            return
        return cam

    def OnCameraUpdate(self):
        if not self.dScanTransform or not self.GetSpaceCamera():
            return
        isAnimatingCone = animations.IsAnimating(self.dScanTransform, 'rotation')
        if self.scanMode == SCANMODE_CAMERA:
            isDscanShortcutActive = uicore.cmd.IsCombatCommandLoaded('CmdRefreshDirectionalScan')
            isMapActive = self.IsSolarSystemMapActive()
            if not isDscanShortcutActive and (isMapActive or isAnimatingCone):
                viewVector = self.GetConeDirection()
                if viewVector:
                    self.AlignSpaceCameraToViewVector(viewVector)
            else:
                viewVector = self.GetSpaceCameraViewVector()
                mapCamera = self.GetSystemMapCamera()
                mapCamera.SetViewVector(viewVector)
            rotation = self.GetSystemMapCameraRotation()
        else:
            spaceCamera = self.GetSpaceCamera()
            rotation = spaceCamera.GetRotationQuat()
        if not isAnimatingCone:
            self.SetConeRotation(rotation)

    def GetConeDirection(self):
        quat = self.GetConeRotation()
        if quat:
            return geo2.QuaternionTransformVector(quat, (0, 0, 1))

    def IsSolarSystemMapActive(self):
        wnd = uicore.registry.GetActive()
        return wnd and wnd.name == DOCKPANELID_SOLARSYSTEMMAP

    def SetConeRotation(self, rotation):
        self.dScanTransform.rotation = rotation

    def GetConeRotation(self):
        if self.dScanTransform:
            return self.dScanTransform.rotation

    def AlignSpaceCameraToViewVector(self, viewVector, duration = None, callback = None, sleep = False):
        yaw1, pitch1 = self.GetYawPitchFromDirection(viewVector)
        cam = self.GetSpaceCamera()
        if duration:
            yaw0 = cam.GetYaw()
            pitch0 = cam.GetPitch()
            yawDiff = GetLesserAngleBetweenYaws(yaw0, yaw1)
            yaw1 = yaw0 + yawDiff
            animations.MorphScalar(cam, 'yaw', yaw0, yaw1, duration=duration)
            animations.MorphScalar(cam, 'pitch', pitch0, pitch1, duration=duration)
        else:
            animations.StopAnimation(cam, 'yaw')
            animations.StopAnimation(cam, 'pitch')
            cam.yaw = yaw1
            cam.pitch = pitch1

    def GetYawPitchFromDirection(self, viewVector):
        viewVector = geo2.Vec3Negate(viewVector)
        rotation = geo2.QuaternionRotationArc((0, 0, 1), viewVector)
        y, p, _ = geo2.QuaternionRotationGetYawPitchRoll(rotation)
        p = -p + math.pi / 2
        return (y, p)

    def GetRotationDurationFromVectors(self, startVec, endVec):
        dotProduct = geo2.Vec3Dot(startVec, endVec)
        try:
            angle = math.acos(dotProduct)
        except ValueError:
            angle = 0.5

        minTime = 0.2
        maxTime = 0.5
        return max(minTime, min(minTime + (maxTime - minTime) * angle / CONE_ROTATION_SPEED, maxTime))

    def GetRotationDurationFromQuaternions(self, startRotation, endRotation):
        startVec = geo2.QuaternionTransformVector(startRotation, (0, 0, 1))
        endVec = geo2.QuaternionTransformVector(endRotation, (0, 0, 1))
        return self.GetRotationDurationFromVectors(startVec, endVec)
