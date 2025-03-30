#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\camera_facing_container.py
import weakref
import eveui
import trinity
import uthread2
from battleground_capture_point_ui.client.const import SCALING_BILLBOARD_THRESHOLD
from carbonui import uiconst
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.panel import BracketPanel, get_absolute_bounds

class CameraFacingUiContainer(BracketPanel):

    def __init__(self, parent, ball, camera, scene):
        self._transform = trinity.EveRootTransform()
        self._transform.translationCurve = ball
        scene.uiObjects.append(self._transform)
        self._scene_ref = weakref.ref(scene)
        self.run_camera_update_loop = True
        self._camera = camera
        self.is_showing = True
        self.cameraThresholdingEnabled = True
        super(CameraFacingUiContainer, self).__init__(name='camera_facing_ui_cont', transform=self._transform, layer=parent, camera=camera, collapse_at_camera_distance=100000.0, clipping_dead_zone=50)
        self._ui = Transform(name='mainCont', width=50, height=50, scalingCenter=(0.5, 0.5), align=uiconst.CENTER, state=uiconst.UI_HIDDEN)
        self.tracker.add(self._ui, offset=(-25, -25))
        uthread2.start_tasklet(self._camera_update_loop)

    def SetCameraThresholdingEnabled(self, enabled):
        self.cameraThresholdingEnabled = enabled

    def _show(self):
        if not self.is_showing:
            uicore.animations.Tr2DScaleIn(self._ui, duration=0.25)
        self._ui.state = uiconst.UI_DISABLED
        self.is_showing = True

    def _hide(self):
        if self.is_showing:
            uicore.animations.Tr2DScaleOut(self._ui, startScale=(1.0, 1.0), endScale=(0.0, 0.0), duration=0.25, sleep=True)
        self._ui.state = uiconst.UI_HIDDEN
        self.is_showing = False

    def _camera_update_loop(self):
        while self.run_camera_update_loop:
            if not self.cameraThresholdingEnabled:
                self._show()
            else:
                distance = self._camera.distance_from_transform(self._transform)
                if distance < SCALING_BILLBOARD_THRESHOLD and not self.is_showing:
                    self._show()
                elif distance > SCALING_BILLBOARD_THRESHOLD and self.is_showing:
                    self._hide()
            eveui.wait_for_next_frame()

    def remove_from_space(self):
        self.run_camera_update_loop = False
        scene = self._scene_ref()
        self.tracker.remove(self._ui)
        if scene is not None:
            scene.uiObjects.fremove(self._transform)

    @property
    def content_bounds(self):
        return get_absolute_bounds(self._ui)

    def expand(self):
        pass

    def collapse(self, lock = False):
        pass
