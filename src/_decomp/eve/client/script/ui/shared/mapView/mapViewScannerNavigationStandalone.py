#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewScannerNavigationStandalone.py
import blue
import geo2
import carbonui.const as uiconst
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ScaleDpi
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples, IsUnder
from eve.client.script.ui.camera.solarSystemMapCameraController import SolarSystemMapCameraController
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import IsDscanShortcutPressed, GetScanRange, SetScanRange
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation
from eve.client.script.ui.shared.mapView.mapViewProbeHandlerStandalone import MODIFY_POSITION, MODIFY_RANGE, MODIFY_SPREAD
X_AXIS = (1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)

class MapViewScannerNavigation(MapViewNavigation):
    __notifyevents__ = ['OnMarkerMouseDown', 'OnMarkerMouseUp']
    movingProbe = None
    rangeProbe = None
    activeManipAxis = None
    modifyHint = None
    borderPickedProbeControl = None
    cursorPickedProbeControl = None
    _keyState = None

    def ApplyAttributes(self, attributes):
        MapViewNavigation.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)

    def ToggleCameraView(self):
        self.cameraController.ToggleCameraView()

    def ConstructCameraController(self):
        self.cameraController = SolarSystemMapCameraController(self.mapView.mapViewID, self.mapView.cameraID)

    def PickScene(self, mouseX, mouseY):
        if uicore.uilib.mouseOver is self:
            self.mapView.OnMarkerHovered(None)
        if not (self.movingProbe or self.rangeProbe):
            probeHandler = self.GetProbeHandler()
            if probeHandler:
                picktype, pickobject = self.GetPick()
                if pickobject and pickobject.name.startswith('cursor'):
                    cursorName, side, probeID = pickobject.name.split('_')
                    probeControl = probeHandler.GetProbeControl(probeID)
                    cursorAxis = cursorName[6:]
                    axis = cursorAxis.lower()
                else:
                    probeControl = None
                    axis = None
                probeHandler.HighlightCursors(probeControl, axis)
                self.cursorPickedProbeControl = probeControl
                if self.IsProbePickingEnabled() and not probeControl and probeHandler.GetEditMode() not in (MODIFY_RANGE, MODIFY_SPREAD):
                    borderPickedProbeControl = self.PickProbes(pickBorder=True)
                else:
                    borderPickedProbeControl = None
                probeHandler.HighlightProbeBorder(borderPickedProbeControl)
                self.borderPickedProbeControl = borderPickedProbeControl
                scenePickActive = bool(self.borderPickedProbeControl or self.cursorPickedProbeControl)

    def IsProbePickingEnabled(self):
        return False

    def MapMarkerPickingOverride(self, *args, **kwds):
        self.PickScene(uicore.uilib.x, uicore.uilib.y)
        return bool(self.borderPickedProbeControl or self.cursorPickedProbeControl)

    def OnMouseWheel(self, wheelDelta, *args):
        self.UpdateCursor()
        if IsDscanShortcutPressed():
            range = GetScanRange()
            range += uicore.uilib.dz * const.AU / 100000
            PlaySound('msg_newscan_directional_shape_play')
            SetScanRange(range)
            return True
        if not uicore.uilib.leftbtn:
            probeHandler = self.GetProbeHandler()
            scanSvc = sm.GetService('scanSvc')
            if probeHandler and probeHandler.HasAvailableProbes():
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    scaling = 0.9
                    if wheelDelta > 0:
                        scaling = 1.0 / scaling
                    scanSvc.ScaleFormationSpread(scaling)
                    return True
                if uicore.uilib.Key(uiconst.VK_MENU):
                    scaling = 0.5
                    if wheelDelta > 0:
                        scaling = 1.0 / scaling
                    scanSvc.ScaleFormation(scaling)
                    return True
        return MapViewNavigation.OnMouseWheel(self, wheelDelta, *args)

    def OnMouseMove(self, *args):
        if uicore.IsDragging() or self.destroyed:
            return
        self.UpdateCursor()
        camera = self.mapView.camera
        if camera is None:
            return
        lib = uicore.uilib
        if lib.leftbtn and (self.movingProbe or self.rangeProbe):
            return
        return MapViewNavigation.OnMouseMove(self, *args)

    def OnMouseHover(self, *args):
        self.UpdateCursor()

    def OnMouseEnter(self, *args):
        self.UpdateCursor()

    def OnMouseExit(self, *args):
        self.UpdateCursor()

    def UpdateCursor(self):
        if IsDscanShortcutPressed():
            uicore.uilib.SetCursor(uiconst.UICURSOR_CCALLDIRECTIONS)
        else:
            uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)

    def OnDblClick(self, *args):
        if self.destroyed:
            return
        isEventConsumed = False
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            picktype, pickobject = self.GetPick()
            if pickobject and pickobject.name.startswith('cursor'):
                cursorName, side, probeID = pickobject.name.split('_')
                probeHandler.FocusOnProbe(probeID)
                isEventConsumed = True
            elif self.IsProbePickingEnabled():
                mouseInsideProbes = self.PickProbes()
                if mouseInsideProbes:
                    try:
                        probeHandler.FocusOnProbe(mouseInsideProbes[0].probeID)
                        isEventConsumed = True
                    except KeyError:
                        pass

        if not isEventConsumed:
            self.ToggleCameraView()
        self.ClickPickedObject()

    def CheckDragThread(self):
        while True:
            if not uicore.uilib.leftbtn:
                self.OnMouseUpLeftBtn()
                return
            blue.synchro.Yield()

    def GetModifyHint(self):
        if self.modifyHint is None or self.modifyHint.destroyed:
            self.modifyHint = EveLabelMedium(parent=self)
        return self.modifyHint

    def CloseModifyHint(self):
        if self.modifyHint and not self.modifyHint.destroyed:
            self.modifyHint.Close()
            self.modifyHint = None

    def UpdateModifyHintPosition(self):
        if self.modifyHint and not self.modifyHint.destroyed:
            left, top = self.GetAbsolutePosition()
            self.modifyHint.left = uicore.uilib.x + 10 - left
            self.modifyHint.top = uicore.uilib.y + 16 - top

    def OnMarkerMouseDown(self, button):
        self.OnMouseDown(button)

    def OnMarkerMouseUp(self, button):
        self.OnMouseUp(button)

    def OnMouseDown(self, button):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            if button == uiconst.MOUSELEFT:
                picktype, pickobject = self.GetPick()
                rangeProbe = None
                if pickobject and pickobject.name[:6] == 'cursor':
                    cursorName, side, probeID = pickobject.name.split('_')
                    if probeID:
                        pickedProbeControl = probeHandler.GetProbeControl(probeID)
                        if pickedProbeControl and probeHandler.GetEditMode() in (MODIFY_POSITION, MODIFY_SPREAD):
                            cursorAxis = cursorName[6:]
                            self.movingProbe = pickedProbeControl
                            uthread.new(self.CheckDragThread)
                            self.activeManipAxis = cursorAxis.lower()
                            self.activeTargetPlaneNormal = self.GetAxisTargetPlaneNormal()
                            self.initProbeScenePosition = pickedProbeControl.GetWorldPosition()
                            self.initCenterScenePosition = probeHandler.GetWorldPositionCenterOfActiveProbes()
                            probeHandler.InitProbeMove(self.initProbeScenePosition, self.initCenterScenePosition, self.GetDotInAxisAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInAxisAlignedPlaneFromPosition(self.initCenterScenePosition))
                            self.scalingOrMoveTimer = AutoTimer(1, self.ScaleOrMoveActiveProbe)
                            return
                        if pickedProbeControl and probeHandler.GetEditMode() == MODIFY_RANGE:
                            rangeProbe = pickedProbeControl
                if self.IsProbePickingEnabled() and not rangeProbe and self.borderPickedProbeControl:
                    pickedProbeControl = self.PickProbes(pickBorder=True)
                    if pickedProbeControl is self.borderPickedProbeControl:
                        rangeProbe = pickedProbeControl
                if rangeProbe:
                    self.rangeProbe = pickedProbeControl
                    self.initProbeScenePosition = pickedProbeControl.GetWorldPosition()
                    self.initCenterScenePosition = probeHandler.GetWorldPositionCenterOfActiveProbes()
                    probeHandler.InitProbeScaling(self.initProbeScenePosition, self.initCenterScenePosition, self.GetDotInCameraAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInCameraAlignedPlaneFromPosition(self.initCenterScenePosition))
                    pickedProbeControl.ShowScanRanges()
                    self.scalingOrMoveTimer = AutoTimer(1, self.ScaleOrMoveActiveProbe)
                    return
            if probeHandler.GetActiveEditMode():
                return
        self.cameraController.OnMouseDown()
        self.mouseDownPick = self.GetPickInfo()

    def OnMouseUp(self, button):
        if button == uiconst.MOUSERIGHT:
            return self.OnMouseUpRightBtn()
        if button == uiconst.MOUSELEFT:
            self.OnMouseUpLeftBtn()
        return MapViewNavigation.OnMouseUp(self, button)

    def OnMouseUpRightBtn(self):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            if uicore.uilib.leftbtn and (self.movingProbe or self.rangeProbe):
                probeHandler.CancelProbeMoveOrScaling()
                self.movingProbe = None
                self.rangeProbe = None
                self.scalingOrMoveTimer = None
                self.CloseModifyHint()

    def OnMouseUpLeftBtn(self):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            if self.rangeProbe:
                probeHandler.RegisterProbeScale(self.rangeProbe)
                self.scalingOrMoveTimer = None
                self.rangeProbe = None
            if self.movingProbe:
                probeHandler.RegisterProbeMove(self.movingProbe)
                self.scalingOrMoveTimer = None
                self.movingProbe = None
            self.CloseModifyHint()

    def GetMenu(self, *args):
        mouseInsideProbes = self.PickProbes()
        if mouseInsideProbes:
            return sm.StartService('scanSvc').GetProbeMenu(mouseInsideProbes[0].probeID)

    def GetDotInCameraAlignedPlaneFromPosition(self, targetPlanePos, offsetMouse = (0, 0), debug = False):
        targetPlaneNormal = self.mapView.camera.GetZAxis()
        return self.GetDotOnTargetPlaneFromPosition(targetPlanePos, targetPlaneNormal, offsetMouse)

    def GetDotInAxisAlignedPlaneFromPosition(self, targetPlanePos, offsetMouse = (0, 0)):
        if not self.activeTargetPlaneNormal:
            return None
        return self.GetDotOnTargetPlaneFromPosition(targetPlanePos, self.activeTargetPlaneNormal, offsetMouse)

    def GetDotOnTargetPlaneFromPosition(self, targetPlanePos, targetPlaneNormal, offsetMouse = (0, 0)):
        ray, start = self.GetPickVector(offsetMouse)
        pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
        return pos

    def GetRayToPlaneDenominator(self, targetPlaneNormal, offsetMouse = (0, 0)):
        ray, _ = self.GetPickVector(offsetMouse)
        denom = geo2.Vec3Dot(targetPlaneNormal, ray)
        return denom

    def GetPickVector(self, offsetMouse):
        oX, oY = offsetMouse
        x, y = ScaleDpi(uicore.uilib.x + oX), ScaleDpi(uicore.uilib.y + oY)
        ray, start = self.cameraController.GetPickVector(x, y)
        return (ray, start)

    def PickProbes(self, pickBorder = False):
        mouseInsideProbes = []
        borderPick = []
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            probeData = sm.StartService('scanSvc').GetProbeData()
            cameraPosition = geo2.Vec3Add(self.mapView.camera._atPosition, self.mapView.camera._eyePosition)
            probes = probeHandler.GetProbeControls()
            for probeID, probeControl in probes.iteritems():
                if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                    continue
                targetPlanePos = probeControl.GetWorldPosition()
                cameraDistance = geo2.Vec3Length(geo2.Vec3Subtract(cameraPosition, targetPlanePos))
                rad = probeControl.GetRange() * SOLARSYSTEM_SCALE
                mousePositionOnCameraPlane = self.GetDotInCameraAlignedPlaneFromPosition(targetPlanePos)
                distanceFromCenter = geo2.Vec3Length(geo2.Vec3Subtract(targetPlanePos, mousePositionOnCameraPlane))
                if pickBorder:
                    pickRadiusPos = self.GetDotInCameraAlignedPlaneFromPosition(targetPlanePos, offsetMouse=(-10, 0))
                    pickRadius = geo2.Vec3Length(geo2.Vec3Subtract(pickRadiusPos, mousePositionOnCameraPlane))
                    if rad + pickRadius > distanceFromCenter > rad - pickRadius:
                        borderPick.append((abs(rad - distanceFromCenter), probeControl))
                elif distanceFromCenter <= rad:
                    mouseInsideProbes.append((cameraDistance, probeControl))

        if pickBorder:
            if borderPick:
                return SortListOfTuples(borderPick)[0]
            else:
                return None
        return SortListOfTuples(mouseInsideProbes)

    def GetPick(self):
        scene = self.mapView.scene
        if scene:
            x, y = uicore.uilib.x, uicore.uilib.y
            return self.cameraController.GetPick(x, y, scene)
        return (None, None)

    def GetProbeHandler(self):
        if self.mapView:
            solarSystemHander = self.mapView.currentSolarsystem
            if solarSystemHander and solarSystemHander.solarsystemID == session.solarsystemid2:
                return solarSystemHander.probeHandler

    def ScaleOrMoveActiveProbe(self, *args):
        probeHandler = self.GetProbeHandler()
        if not probeHandler:
            return
        if not IsUnder(uicore.uilib.mouseOver, self.parent):
            return
        if self.movingProbe:
            probeHandler.MoveProbe(self.movingProbe, self.activeManipAxis, self.GetDotInAxisAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInAxisAlignedPlaneFromPosition(self.initCenterScenePosition))
        elif self.rangeProbe:
            probeHandler.ScaleProbe(self.rangeProbe, self.GetDotInCameraAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInCameraAlignedPlaneFromPosition(self.initCenterScenePosition))

    def GetAxisTargetPlaneNormal(self):
        axisThreshold = 0.15
        planeThreshold = 0.2
        if self.activeManipAxis == 'z':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) >= axisThreshold:
                return Y_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= axisThreshold:
                return X_AXIS
            else:
                return Z_AXIS
        elif self.activeManipAxis == 'x':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) >= axisThreshold:
                return Y_AXIS
            elif abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= axisThreshold:
                return Z_AXIS
            else:
                return X_AXIS
        elif self.activeManipAxis == 'y':
            if abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= axisThreshold:
                return Z_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= axisThreshold:
                return X_AXIS
            else:
                return Y_AXIS
        elif self.activeManipAxis == 'xz':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) <= planeThreshold:
                return None
            else:
                return Y_AXIS
        elif self.activeManipAxis == 'xy':
            if abs(self.GetRayToPlaneDenominator(Z_AXIS)) <= planeThreshold:
                return None
            else:
                return Z_AXIS
        elif self.activeManipAxis == 'yz':
            if abs(self.GetRayToPlaneDenominator(X_AXIS)) <= planeThreshold:
                return None
            else:
                return X_AXIS
