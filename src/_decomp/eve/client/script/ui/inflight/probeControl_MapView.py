#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\probeControl_MapView.py
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.mathUtil import ClampRotation
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE, MODIFY_POSITION, MODIFY_RANGE, MODIFY_SPREAD
import trinity
import carbonui.const as uiconst
import geo2
import random
import math
from eve.client.script.environment import nodemanager
import blue
BASE_PROBE_COLOR = (0.45098039215686275, 0.9411764705882353, 1.0, 0)
CURSOR_COLOR_PARAMETER_INDEX = 2
CURSOR_IDLE_COLOR = BASE_PROBE_COLOR
CURSOR_ACTIVE_COLOR = (2.0, 2.0, 2.0, 1.0)
TR2TM_LOOK_AT_CAMERA = 3
ANIM_DURATION = 0.15

class BaseProbeControl(object):
    formationCenter = None
    STATE_IDLE = 0
    STATE_ACTIVE = 1
    STATE_ACTIVE_SINGLE = 2
    spreadCursor = None
    rangeCursor = None
    _cursorState = None

    def __init__(self, uniqueID, parent):
        self.parent = parent
        locator = trinity.EveTransform()
        locator.name = 'spherePar_%s' % uniqueID
        try:
            self.parent.children.append(locator)
        except:
            self.parent.objects.append(locator)

        CURSOR_SCALE_ARG_1 = 2000000.0
        CURSOR_SCALE = SOLARSYSTEM_SCALE * 250000000000.0
        cursor = trinity.Load('res:/Model/UI/probeCursor.red')
        cursor.scaling = (CURSOR_SCALE, CURSOR_SCALE, CURSOR_SCALE)
        cursor.useDistanceBasedScale = True
        cursor.distanceBasedScaleArg1 = CURSOR_SCALE_ARG_1
        cursor.distanceBasedScaleArg2 = 0.0
        cursor.translation = (0.0, 0.0, 0.0)
        cursor.display = False
        self.arrowX0 = nodemanager.FindNode(cursor, 'cursorX_0', 'trinity.EveTransform')
        self.arrowX1 = nodemanager.FindNode(cursor, 'cursorX_1', 'trinity.EveTransform')
        self.arrowY0 = nodemanager.FindNode(cursor, 'cursorY_0', 'trinity.EveTransform')
        self.arrowY1 = nodemanager.FindNode(cursor, 'cursorY_1', 'trinity.EveTransform')
        self.arrowZ0 = nodemanager.FindNode(cursor, 'cursorZ_0', 'trinity.EveTransform')
        self.arrowZ1 = nodemanager.FindNode(cursor, 'cursorZ_1', 'trinity.EveTransform')
        for c in cursor.children:
            c.name += '_' + str(uniqueID)

        locator.children.append(cursor)
        self.uniqueID = uniqueID
        self.cursor = cursor
        self.locator = locator

    def SetFormationCenter(self, centerPosition):
        self.formationCenter = centerPosition
        q = geo2.QuaternionRotationArc((0.0, 0.0, 1.0), geo2.Vec3Normalize(geo2.Vec3Subtract(self.formationCenter, self.locator.translation)))
        if self.spreadCursor:
            self.spreadCursor.rotation = q
        if self.rangeCursor:
            self.rangeCursor.rotation = q

    def SetPosition(self, position, animate = False):
        position = geo2.Vector(*position)
        if animate:
            animations.MorphVector3(self.locator, 'translation', self.locator.translation, position, duration=ANIM_DURATION)
        else:
            self.locator.translation = position

    def GetPosition(self):
        return geo2.Vector(self.locator.translation)

    def GetWorldPosition(self):
        return geo2.Vector(self.locator.worldTransform[3][:3])

    def SetCursorState(self, cursorState, hiliteAxis = None):
        if self._cursorState == (cursorState, hiliteAxis):
            return
        self._cursorState = (cursorState, hiliteAxis)
        if cursorState == self.STATE_ACTIVE:
            PlaySound('msg_newscan_probe_feedback_play')
            color = CURSOR_ACTIVE_COLOR
        else:
            color = CURSOR_IDLE_COLOR
        for each in self.cursor.children:
            if hiliteAxis and cursorState == self.STATE_ACTIVE:
                cursorName, side, probeID = each.name.split('_')
                cursorAxis = cursorName[6:].lower()
                if hiliteAxis == cursorAxis:
                    each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = CURSOR_ACTIVE_COLOR
                else:
                    each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = CURSOR_IDLE_COLOR
            else:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color

        if self.spreadCursor:
            for each in self.spreadCursor.children:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color

        if self.rangeCursor:
            for each in self.rangeCursor.children:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color

    def UpdateArrowOrientation(self, camera):
        if not self.IsVisible():
            return
        yaw = camera.GetYaw()
        yaw = ClampRotation(yaw)
        self.arrowY0.rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, math.pi / 2, 0)
        self.arrowY1.rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, -math.pi / 2, 0)
        pitch = camera.GetPitch()
        if yaw < math.pi / 2 or yaw > 3 * math.pi / 2:
            pitch = math.pi - pitch
        quat = geo2.QuaternionRotationAxis((1, 0, 0), pitch)
        self.arrowX0.rotation = geo2.QuaternionMultiply((0.0, 0.7071068, 0.0, 0.7071068), quat)
        self.arrowX1.rotation = geo2.QuaternionMultiply((0.0, -0.7071068, 0.0, 0.7071068), quat)
        pitch = camera.GetPitch()
        if yaw > math.pi:
            pitch = math.pi - pitch
        quat = geo2.QuaternionRotationAxis((0, 0, 1), pitch)
        self.arrowZ0.rotation = geo2.QuaternionMultiply((0.0, 1.0, 0.0, 0.0), quat)
        self.arrowZ1.rotation = quat

    def IsVisible(self):
        return self.cursor.display

    def UpdateArrowVisibility(self, camera):
        if not self.IsVisible():
            return
        dir = geo2.Vec3Scale(camera.GetLookAtDirection(), -1)
        self.arrowX0.display = self._IsArrowVisible((1, 0, 0), dir)
        self.arrowX1.display = self._IsArrowVisible((-1, 0, 0), dir)
        self.arrowY1.display = self._IsArrowVisible((0, 1, 0), dir)
        self.arrowY0.display = self._IsArrowVisible((0, -1, 0), dir)
        self.arrowZ1.display = self._IsArrowVisible((0, 0, 1), dir)
        self.arrowZ0.display = self._IsArrowVisible((0, 0, -1), dir)

    def _IsArrowVisible(self, dir, camDir):
        try:
            return math.acos(geo2.Vec3Dot(dir, camDir)) < 2.9
        except ValueError:
            return True

    def Remove(self, *args):
        if self.locator in self.parent.children:
            self.parent.children.remove(self.locator)
        self.parent = None


class ProbeControl(BaseProbeControl):

    def __init__(self, probeID, probe, parent):
        scanSvc = sm.GetService('scanSvc')
        BaseProbeControl.__init__(self, probeID, parent)
        sphere = trinity.Load('res:/dx9/model/UI/Scanbubbledoteffect.red')
        self.locator.children.append(sphere)
        self.sphere = sphere
        scanbubble = nodemanager.FindNode(sphere, 'Scanbubble', 'trinity.EveTransform')
        for each in scanbubble.children:
            each.scaling = tuple([ (100 if scaling > 0 else -100) for scaling in each.scaling ])

        self.spreadCursor = self.ConstructSpreadCursor(probeID)
        self.rangeCursor = self.ConstructRangeCursor(probeID)
        self.scanRanges = scanSvc.GetScanRangeStepsByTypeID(probe.typeID)
        self.probeID = probeID
        self.scanrangeCircles = None
        self._highlighted = True
        self.HighlightBorder(0)
        animations.MorphVector3(self.locator, 'scaling', startVal=(0.0, 0.0, 0.0), endVal=(1.0, 1.0, 1.0), duration=0.5, curveType=uiconst.ANIM_OVERSHOT, timeOffset=random.random() * 0.5)

    def ConstructRangeCursor(self, probeID):
        cursor = trinity.Load('res:/Model/UI/probeRangeCursor.red')
        for c in cursor.children:
            c.scaling = (250.0, 250.0, 250.0)
            c.name += '_' + str(probeID)
            c.mesh.geometryResPath = 'res:/Graphics/generic/vortex/Cone2.gr2'
            c.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi * 0.5, 0.0)

        cursor.display = False
        self.locator.children.append(cursor)
        return cursor

    def ConstructSpreadCursor(self, probeID):
        CURSOR_SCALE_ARG_1 = 2000000.0
        CURSOR_SCALE = SOLARSYSTEM_SCALE * 250000000000.0
        cursor = trinity.Load('res:/Model/UI/probeSpreadCursor.red')
        cursor.scaling = (CURSOR_SCALE, CURSOR_SCALE, CURSOR_SCALE)
        cursor.useDistanceBasedScale = True
        cursor.distanceBasedScaleArg1 = CURSOR_SCALE_ARG_1
        cursor.distanceBasedScaleArg2 = 0.0
        cursor.translation = (0.0, 0.0, 0.0)
        cursor.display = False
        for c in cursor.children:
            c.name += '_' + str(probeID)

        self.locator.children.append(cursor)
        return cursor

    def Remove(self, animate = False):
        uthread.new(self._Remove, animate)

    def _Remove(self, animate):
        if animate:
            self.SetRange(0.0, animate=True)
            blue.synchro.SleepWallclock(ANIM_DURATION * 1000)
        BaseProbeControl.Remove(self)

    def SetScanDronesState(self, state):
        scanEffectTf = nodemanager.FindNode(self.sphere, 'scanLines', 'trinity.EveTransform')
        if scanEffectTf:
            scanEffectTf.display = state
            if state:
                scanLinesCurveSet = nodemanager.FindNode(scanEffectTf, 'ScanCurveSet', 'trinity.TriCurveSet')
                if scanLinesCurveSet:
                    scanLinesCurveSet.Play()

    def SetRange(self, probeRange, animate = False):
        scaling = (probeRange, probeRange, probeRange)
        if animate:
            animations.MorphVector3(self.sphere, 'scaling', self.sphere.scaling, scaling, duration=ANIM_DURATION)
        else:
            self.sphere.scaling = scaling
        transform = self.rangeCursor.children[0]
        translation = (0.0, 0.0, -probeRange + 250.0)
        if animate:
            animations.MorphVector3(transform, 'translation', transform.translation, translation, duration=ANIM_DURATION)
        else:
            transform.translation = translation

    def ScaleRange(self, scale):
        scale = self.sphere.scaling[0] * scale
        self.SetRange((scale, scale, scale))

    def GetRange(self):
        return self.sphere.scaling[0]

    def HighlightBorder(self, on = 1):
        if bool(on) == self._highlighted:
            return
        self._highlighted = bool(on)
        curveSets = self.sphere.Find('trinity.TriCurveSet')
        curveSet = None
        for each in curveSets:
            if getattr(each, 'name', None) == 'Highlight':
                curveSet = each
                break

        if curveSet:
            curveSet.Stop()
            if on:
                curveSet.scale = 10.0
                curveSet.Play()
            else:
                curveSet.scale = -1.0
                curveSet.PlayFrom(curveSet.GetMaxCurveDuration())

    def HideScanRanges(self):
        if self.scanrangeCircles is not None:
            self.scanrangeCircles.display = False

    def ShowScanRanges(self):
        if self.scanrangeCircles is None:
            par = trinity.EveTransform()
            self.scanrangeCircles = par
            par.modifier = TR2TM_LOOK_AT_CAMERA
            self.locator.children.append(par)
            for r in self.scanRanges:
                r *= 100.0
                sr = trinity.Load('res:/Model/UI/probeRange.red')
                sr.scaling = (r, r, r)
                par.children.append(sr)

        self.scanrangeCircles.display = True

    def HighlightProbe(self):
        self.HighlightBorder(1)

    def StopHighlightProbe(self):
        self.HighlightBorder(0)

    def IsVisible(self):
        return BaseProbeControl.IsVisible(self) or self.rangeCursor.display or self.spreadCursor.display

    def SetEditMode(self, editMode):
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        self.spreadCursor.display = editMode == MODIFY_SPREAD
        self.cursor.display = editMode == MODIFY_POSITION and SHIFT
        self.rangeCursor.display = editMode == MODIFY_RANGE
