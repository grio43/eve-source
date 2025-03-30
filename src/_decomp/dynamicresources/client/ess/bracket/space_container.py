#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\space_container.py
import math
import eveui
import geo2
import mathext
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.ui3d import InSceneContainer
from carbonui.uicore import uicore

class EssSpaceContainer(InSceneContainer):
    __next_container_id = 0

    def __init__(self, transform, width, height, scene_manager = None, offset_y = 0.0, scale = 1.0):
        self._offset_y = float(offset_y)
        self._real_opacity = 1.0
        self._scale = float(scale)
        self._content = None
        self._scene_manager = scene_manager
        if self._scene_manager is None:
            self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        scene = self._scene_manager.GetRegisteredScene('default')
        super(EssSpaceContainer, self).__init__(name='EssSpaceContainer_{}'.format(self._get_next_id()), state=uiconst.UI_DISABLED, scene=scene, sceneParent=scene.uiObjects, trackType=self.TRACKTYPE_TRANSFORM, parentTransform=transform, width=width, height=height, clearBackground=True, backgroundColor=(0.0, 0.0, 0.0, 0.0), renderJob=uicore.uilib.GetRenderJob(), isFullscreen=False)
        self._opacity_wrapper = Container(parent=self, align=uiconst.TOALL, opacity=self._real_opacity)
        self._content = Container(parent=self._opacity_wrapper, align=uiconst.TOALL)
        self.transform.scaling = (self._scale, self._scale, self._scale)
        self.transform.translation = (0.0, self.offset_y, 0.0)
        self.transform.rotation = geo2.QuaternionRotationSetYawPitchRoll(0, -math.pi / 2.0, 0)
        self._start_update_loop()

    @property
    def content(self):
        return self._content

    @property
    def offset_y(self):
        return float(self._offset_y)

    @offset_y.setter
    def offset_y(self, offset_y):
        self._offset_y = offset_y

    @property
    def opacity(self):
        return self._real_opacity

    @opacity.setter
    def opacity(self, opacity):
        self._real_opacity = opacity
        if hasattr(self, '_opacity_wrapper'):
            self._opacity_wrapper.opacity = opacity

    @property
    def scale(self):
        return float(self._scale)

    @scale.setter
    def scale(self, scale):
        self._scale = scale

    def get_camera(self):
        return self._scene_manager.GetActiveCamera()

    @threadutils.threaded
    def _start_update_loop(self):
        while not self.destroyed:
            eveui.wait_for_next_frame()
            self.transform.scaling = (self._scale, self._scale, self._scale)
            self.transform.translation = (0.0, self.offset_y, 0.0)
            eye_position = self.get_camera().GetEyePosition()
            _, _, ess_position = geo2.MatrixDecompose(self.transform.worldTransform)
            eye_to_ess = geo2.Vec3Subtract(ess_position, eye_position)
            projected = (eye_to_ess[0], 0, eye_to_ess[2])
            dot = geo2.Vec3Dot(geo2.Vec3Normalize(eye_to_ess), geo2.Vec3Normalize(projected))
            angle = math.degrees(math.acos(mathext.clamp(dot, 0.0, 1.0)))
            opacity = mathext.lerp(0.0, 1.0, min(abs(max(angle - 1.0, 0.0)) / 3.0, 1.0))
            self.content.opacity = opacity

    @staticmethod
    def _get_next_id():
        container_id = EssSpaceContainer.__next_container_id
        EssSpaceContainer.__next_container_id += 1
        return container_id

    def Close(self):
        if self.parentTransform:
            self.parentTransform.children.fremove(self.transform)
        super(EssSpaceContainer, self).Close()


from dynamicresources.client.ess.bracket.debug import __reload_update__
