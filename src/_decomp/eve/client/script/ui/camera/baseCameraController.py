#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\baseCameraController.py
from carbon.common.script.sys import service
import trinity
import carbonui.const as uiconst
from eve.client.script.ui.camera.cameraUtil import GetCameraSensitivityMultiplier
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.client.script.parklife import states
from eve.common.script.sys.eveCfg import InSpace
import geo2
import uthread
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService

class BaseCameraController(object):
    enablePickTransparent = False
    cameraID = None

    def __init__(self, *args):
        self.mouseDownPos = None
        self.isMovingSceneCursor = None

    def Activate(self):
        pass

    def Deactivate(self):
        pass

    def OnMouseEnter(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def OnMouseDown(self, *args):
        _, pickobject = self.GetPick()
        self.mouseDownPos = (uicore.uilib.x, uicore.uilib.y)
        self.CheckInSceneCursorPicked(pickobject)
        return pickobject

    def OnMouseUp(self, button, *args):
        isLeftBtn = button == 0
        if isLeftBtn and not uicore.uilib.rightbtn:
            self.cameraStillSpinning = False
            if not self.IsMouseDragged():
                self.TryClickSceneObject()
        self.CheckReleaseSceneCursor()
        isRightBtn = button == 1
        if isRightBtn:
            uthread.new(sm.GetService('target').CancelTargetOrder)
        self.mouseDownPos = None

    def IsMouseDragged(self):
        mt = self.GetMouseTravel()
        return mt is not None and mt >= 5

    def OnMouseMove(self, *args):
        pass

    def OnDblClick(self, *args):
        pass

    def OnMouseWheel(self, *args):
        pass

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(self.cameraID)

    @property
    def camera(self):
        return self.GetCamera()

    def GetPick(self, x = None, y = None, scene = None):
        if not trinity.app.IsActive():
            return (None, None)
        if scene is None:
            scene = self._GetScene()
        if scene:
            x = x or uicore.uilib.x
            y = y or uicore.uilib.y
            x, y = uicore.ScaleDpi(x), uicore.ScaleDpi(y)
            camera = self.GetCamera()
            pickTransparent = trinity.Tr2PickType.PICK_TYPE_TRANSPARENT if self.enablePickTransparent else 0
            filter = trinity.Tr2PickType.PICK_TYPE_PICKING | trinity.Tr2PickType.PICK_TYPE_OPAQUE | pickTransparent
            pickResult = scene.PickObjectAndAreaID(x, y, camera.projectionMatrix, camera.viewMatrix, self.GetViewport(), filter)
            if pickResult is not None:
                pickObj, areaID = pickResult
                areaName = self.GetAreaName(areaID)
                return (areaName, pickObj)
        return (None, None)

    def _GetScene(self):
        sceneMgr = sm.GetService('sceneManager')
        if sceneMgr.IsLoadingScene('default'):
            return None
        else:
            return sceneMgr.GetActiveScene()

    def GetAreaName(self, areaID):
        return 'scene'

    def GetPickVector(self, x = None, y = None):
        if x is None:
            x = int(uicore.uilib.x * uicore.desktop.dpiScaling)
        if y is None:
            y = int(uicore.uilib.y * uicore.desktop.dpiScaling)
        camera = self.GetCamera()
        viewport = self.GetViewport()
        view = camera.viewMatrix.transform
        projection = camera.projectionMatrix.transform
        direction, startPos = trinity.device.GetPickRayFromViewport(x, y, viewport, view, projection)
        return (direction, startPos)

    def GetViewport(self):
        return trinity.device.viewport

    def ProjectWorldToScreen(self, vec3):
        cam = self.GetCamera()
        viewport = self.GetViewport()
        viewport = (viewport.x,
         viewport.y,
         viewport.width,
         viewport.height,
         viewport.minZ,
         viewport.maxZ)
        x, y, z, w = geo2.Vec3Project(vec3, viewport, cam.projectionMatrix.transform, cam.viewMatrix.transform, geo2.MatrixIdentity())
        return (x, y)

    def TryClickSceneObject(self):
        _, pickobject = self.GetPick()
        if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            slimItem = GetBallparkRecord(pickobject.translationCurve.id)
            if slimItem and slimItem.groupID not in const.nonTargetableGroups:
                itemID = pickobject.translationCurve.id
                sm.GetService('stateSvc').SetState(itemID, states.selected, 1)
                GetMenuService().TacticalItemClicked(itemID)
                return True
        elif uicore.cmd.IsCombatCommandLoaded('CmdToggleLookAtItem'):
            uicore.cmd.ExecuteCombatCommand(session.shipid, uiconst.UI_KEYUP)
        elif uicore.cmd.IsCombatCommandLoaded('CmdToggleCameraTracking'):
            uicore.cmd.ExecuteCombatCommand(session.shipid, uiconst.UI_KEYUP)
        return False

    def GetMouseTravel(self):
        if self.mouseDownPos:
            x, y = uicore.uilib.x, uicore.uilib.y
            v = trinity.TriVector(float(x - self.mouseDownPos[0]), float(y - self.mouseDownPos[1]), 0.0)
            return int(v.Length())
        else:
            return None

    def CheckInSceneCursorPicked(self, pickobject):
        if not InSpace():
            return
        if sm.IsServiceRunning('scenario') and sm.GetService('scenario').IsActive():
            self.isMovingSceneCursor = sm.GetService('scenario').GetPickAxis()
        elif pickobject and sm.IsServiceRunning('posAnchor') and sm.GetService('posAnchor').IsActive() and pickobject.name[:6] == 'cursor':
            self.isMovingSceneCursor = pickobject

    def CheckReleaseSceneCursor(self):
        if self.isMovingSceneCursor:
            self.isMovingSceneCursor = None
            if sm.GetService('posAnchor').IsActive():
                sm.GetService('posAnchor').StopMovingCursor()
            return True
        return False

    def CheckMoveSceneCursor(self):
        if not self.isMovingSceneCursor or not uicore.uilib.leftbtn:
            return False
        if sm.GetService('posAnchor').IsActive():
            sm.GetService('posAnchor').MoveCursor(self.isMovingSceneCursor, self.GetMouseDX(), self.GetMouseDY(), self.GetCamera())
            return True
        if session.role & service.ROLE_CONTENT:
            sm.GetService('scenario').MoveCursor(self.isMovingSceneCursor, self.GetMouseDX(), self.GetMouseDY(), self.GetCamera())
            return True
        return False

    def GetMouseDY(self):
        return uicore.uilib.dy * GetCameraSensitivityMultiplier()

    def GetMouseDX(self):
        return uicore.uilib.dx * GetCameraSensitivityMultiplier()
