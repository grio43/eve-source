#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\tacticalCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz, CheckInvertZoom, GetPanVectorForZoomToCursor
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraAchievementEventTracker import CameraAchievementEventTracker
import evecamera
import carbonui.const as uiconst
from carbonui.uicore import uicore
import evespacemouse
from evespacemouse.controller import SpaceMouseController
import evegraphics.settings as gfxsettings
DIST_ORBIT_SWITCH = 20000

class TacticalCameraController(BaseCameraController):
    cameraID = evecamera.CAM_TACTICAL

    def __init__(self, *args, **kwargs):
        super(TacticalCameraController, self).__init__(*args, **kwargs)
        self.cameraAchievementEventTracker = CameraAchievementEventTracker()
        self.spaceMouseController = None

    def Activate(self):
        actions = evespacemouse.ActionSet('tacticalCamera', 'Tooltips/Hud/TacticalCamera', [evespacemouse.Action('track', 'UI/Commands/CmdToggleCameraTracking'), evespacemouse.Action('lookAt', 'UI/Commands/CmdToggleLookAtItem'), evespacemouse.Action('CmdHideUI', 'UI/Commands/CmdHideUI')])
        evespacemouse.StartListening(actions, self._OnSpaceMousePosition, self._OnSpaceMouseAction)
        if evespacemouse.IsEnabled():
            self.spaceMouseController = SpaceMouseController(gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT), gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT))
        sm.RegisterForNotifyEvent(self, 'OnSpaceMouseAccelerationCoefficientChanged')
        sm.RegisterForNotifyEvent(self, 'OnSpaceMouseSpeedCoefficientChanged')

    def Deactivate(self):
        evespacemouse.StopListening(self._OnSpaceMousePosition, self._OnSpaceMouseAction)
        self.spaceMouseController = None
        sm.UnregisterForNotifyEvent(self, 'OnSpaceMouseAccelerationCoefficientChanged')
        sm.UnregisterForNotifyEvent(self, 'OnSpaceMouseSpeedCoefficientChanged')

    def StopSpaceMouse(self):
        if self.spaceMouseController is not None:
            self.spaceMouseController.Stop()

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            self.StopSpaceMouse()
            if camera.IsAttached() and math.fabs(uicore.uilib.dx) > 1:
                camera.Orbit(0.01 * self.GetMouseDX(), 0.0)
            dz = CheckInvertZoom(uicore.uilib.dy)
            self._Zoom(dz, -0.005, zoomToCursor=False)
            self.RecordOrbitForAchievements()
        elif uicore.uilib.rightbtn:
            self.StopSpaceMouse()
            k = 3.0
            camera.Pan(-k * self.GetMouseDX(), k * self.GetMouseDY(), 0)
        elif uicore.uilib.leftbtn:
            self.StopSpaceMouse()
            k = evecamera.ORBIT_MOVE_DIST if camera.IsAttached() else 0.006
            camera.Orbit(k * self.GetMouseDX(), k * self.GetMouseDY())
            self.RecordOrbitForAchievements()

    def OnMouseWheel(self, *args):
        self.StopSpaceMouse()
        dz = GetZoomDz()
        k = 0.0005
        self._Zoom(dz, k, zoomToCursor=True)

    def _OnSpaceMousePosition(self, dt, translation, rotation):
        if self.spaceMouseController:
            translation, rotation = self.spaceMouseController.CalculateTranslationAndRotation(dt, translation, rotation)
        camera = self.GetCamera()
        if any(rotation):
            camera.OrbitImmediate(rotation[1], rotation[0])
        if any(translation):
            if camera.IsAttached() or camera.IsTracking():
                camera.Zoom(translation[2] * 0.01 * dt)
            else:
                camera.PanImmediate(*translation)

    def _GetActionItemID(self):
        _, pickobject = self.GetPick()
        if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            return pickobject.translationCurve.id

    def _OnSpaceMouseAction(self, name):
        camera = self.GetCamera()
        if name == 'track':
            itemID = self._GetActionItemID()
            if itemID:
                camera.Track(itemID)
            elif camera.IsTracking() or camera.IsAttached():
                camera.StopTracking()
                camera.Detach()
            self.StopSpaceMouse()
            raise evespacemouse.StopPropagation()
        elif name == 'lookAt':
            itemID = self._GetActionItemID()
            if itemID:
                camera.LookAt(itemID, smooth=True)
            elif camera.IsTracking() or camera.IsAttached():
                camera.StopTracking()
                camera.Detach()
            self.StopSpaceMouse()
            raise evespacemouse.StopPropagation()

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())

    def RecordZoomForAchievements(self, amount):
        self.cameraAchievementEventTracker.RecordZoomForAchievements(amount)

    def RecordOrbitForAchievements(self):
        camera = self.GetCamera()
        self.cameraAchievementEventTracker.RecordOrbitForAchievements(self, camera)

    def OnMouseUp(self, button, *args):
        super(TacticalCameraController, self).OnMouseUp(button, *args)
        self.cameraAchievementEventTracker.StopRecordingOrbitForAchievements()

    def _Zoom(self, dz, k, zoomToCursor):
        self.RecordZoomForAchievements(dz)
        camera = self.GetCamera()
        if uicore.uilib.Key(uiconst.VK_MENU):
            camera.FovZoom(k * dz)
        elif camera.IsAttached() or camera.IsTracking():
            camera.Zoom(k * dz)
        elif zoomToCursor:
            x, y, z = GetPanVectorForZoomToCursor(self.GetViewport(), camera.fov)
            k = 1.5 * dz
            camera.Pan(k * x, k * y, k * z)
        else:
            k = 20.0
            camera.Pan(0, 0, -k * dz)

    def OnSpaceMouseAccelerationCoefficientChanged(self):
        coefficient = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT, None)
        if coefficient is not None:
            self.spaceMouseController.SetAccelerationCoefficient(coefficient)

    def OnSpaceMouseSpeedCoefficientChanged(self):
        coefficient = gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT, None)
        if coefficient is not None:
            self.spaceMouseController.SetSpeedCoefficient(coefficient)
