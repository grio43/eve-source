#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\distance_thresholded_camera_facing_ui_container.py
import eveui
import uthread2
from battleground_capture_point_ui.client.camera_facing_container import CameraFacingUiContainer
from battleground_capture_point_ui.client.const import SCALING_BILLBOARD_THRESHOLD
from carbonui import uiconst
from carbonui.uicore import uicore

class DistanceThreasholdedCameraFacingUiContainer(CameraFacingUiContainer):

    def __init__(self, parent, ball, camera, scene):
        super(DistanceThreasholdedCameraFacingUiContainer, self).__init__(parent, ball, camera, scene)
        self._ui.state = uiconst.UI_HIDDEN
        self.cameraThresholdingEnabled = True
        uthread2.start_tasklet(self._camera_update_loop)

    def SetCameraThresholdingEnabled(self, enabled):
        self.cameraThresholdingEnabled = enabled

    def hide_gauge(self):
        if self.is_showing:
            uicore.animations.Tr2DScaleOut(self._ui, startScale=(1.0, 1.0), endScale=(0.0, 0.0), duration=0.25, sleep=True)
        self._ui.state = uiconst.UI_HIDDEN
        self.is_showing = False

    def show_gauge(self):
        if not self.is_showing:
            uicore.animations.Tr2DScaleIn(self._ui, duration=0.25)
        self._ui.state = uiconst.UI_DISABLED
        self.is_showing = True

    def _camera_update_loop(self):
        while self.run_camera_update_loop:
            if not self.cameraThresholdingEnabled:
                self.hide_gauge()
            else:
                distance = self._camera.distance_from_transform(self._transform)
                if distance > SCALING_BILLBOARD_THRESHOLD and not self.is_showing:
                    self.show_gauge()
                elif distance < SCALING_BILLBOARD_THRESHOLD and self.is_showing:
                    self.hide_gauge()
            eveui.wait_for_next_frame()
