#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\analysisbeacon\client\beacon_ui_container.py
import math
import weakref
import eveui
import geo2
import trinity
import uthread2
from analysisbeacon.client.const import SCALING_BILLBOARD_THRESHOLD
from carbonui import uiconst
from carbonui.primitives.transform import Transform
from carbonui.ui3d import InSceneContainer
from carbonui.uicore import uicore

class BeaconUiContainer(InSceneContainer):

    def __init__(self, ball, scene, camera):
        self._scale = 10000
        self._scene_ref = weakref.ref(scene)
        self.run_camera_update_loop = True
        self._camera = camera
        self.transform = trinity.EveRootTransform()
        self.transform.translationCurve = ball
        scene.uiObjects.append(self.transform)
        self.is_showing = True
        super(BeaconUiContainer, self).__init__(name='CrabTimerRing', state=uiconst.UI_DISABLED, scene=scene, sceneParent=scene.uiObjects, parentTransform=self.transform, trackType=self.TRACKTYPE_TRANSFORM, width=500, height=500, clearBackground=True, backgroundColor=(0.0, 0.0, 0.0, 0.0), renderJob=uicore.uilib.GetRenderJob(), isFullscreen=False)
        self.transform.scaling = (self._scale, self._scale, self._scale)
        self.transform.translation = (0.0, 0.0, 0.0)
        self.transform.rotation = geo2.QuaternionRotationSetYawPitchRoll(0, -math.pi / 2.0, 0)
        self.mainCont = Transform(parent=self, name='mainCont', scalingCenter=(0.5, 0.5), align=uiconst.TOALL)
        uthread2.start_tasklet(self._camera_update_loop)

    def _update_loop(self):
        counter = 0.0
        while not self.destroyed:
            eveui.wait_for_next_frame()
            self.transform.translation = (0.0, 100 * math.sin(counter), 0.0)
            counter += 0.01

    def _camera_update_loop(self):
        while self.run_camera_update_loop:
            distance = self._camera.distance_from_transform(self.transform)
            if distance > SCALING_BILLBOARD_THRESHOLD and self.is_showing:
                uicore.animations.Tr2DScaleOut(self.mainCont, startScale=(1.0, 1.0), endScale=(0.0, 0.0), duration=0.25, sleep=True)
                self.mainCont.Hide()
                self.is_showing = False
            elif distance < SCALING_BILLBOARD_THRESHOLD and not self.is_showing:
                self.mainCont.Show()
                uicore.animations.Tr2DScaleIn(self.mainCont, duration=0.25, sleep=True)
                self.is_showing = True
            eveui.wait_for_next_frame()

    @property
    def scale(self):
        return float(self._scale)

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    def remove_from_space(self):
        self.run_camera_update_loop = False
        scene = self._scene_ref()
        if scene is not None:
            scene.uiObjects.fremove(self.transform)
        self.Close()

    def __del__(self):
        scene = self._scene_ref()
        if scene is not None:
            scene.uiObjects.fremove(self.transform)
