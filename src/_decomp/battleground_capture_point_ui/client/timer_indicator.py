#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\timer_indicator.py
import eveui
import threadutils
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.ui3d import InSceneContainer
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.label import Header

class TimerIndicator(InSceneContainer):

    def __init__(self, name, transform, width, height, scale, color, on_update, visible = True):
        self._root_transform = transform
        self._color = color
        self._on_update = on_update
        self._visible = visible
        self._real_opacity = 1.0
        scene_manager = ServiceManager.Instance().GetService('sceneManager')
        scene = scene_manager.GetRegisteredScene('default')
        super(TimerIndicator, self).__init__(name='{}_{}'.format(name, id(self)), state=uiconst.UI_DISABLED, scene=scene, sceneParent=scene.uiObjects, trackType=self.TRACKTYPE_TRANSFORM, parentTransform=transform, width=width, height=height, clearBackground=True, backgroundColor=(0.0, 0.0, 0.0, 0.0), renderJob=uicore.uilib.GetRenderJob(), isFullscreen=False, faceCamera=True)
        self.scale = scale
        self.transform.sortValueMultiplier = 0.1
        self._opacity_wrapper = Container(parent=self, align=uiconst.TOALL, opacity=1.0 if self._visible else 0.0)
        self._content = Container(parent=self._opacity_wrapper, align=uiconst.TOALL, opacity=self._real_opacity)
        self._label = Header(parent=self._content, align=uiconst.CENTERLEFT, left=self.width / 2.0 + 8, top=-40)
        Fill(parent=self._content, align=uiconst.CENTER, top=-26, width=2, height=52, color=self._color)

    @property
    def scale(self):
        return self.transform.scaling[0]

    @scale.setter
    def scale(self, scale):
        self.transform.scaling = (scale, scale, scale)

    @property
    def opacity(self):
        return self._real_opacity

    @opacity.setter
    def opacity(self, opacity):
        self._real_opacity = opacity
        if hasattr(self, '_content'):
            self._content.opacity = opacity

    def show(self, time_offset = 0.0):
        if not self._visible:
            self._visible = True
            self._start_timer_loop()
            animations.FadeIn(self._opacity_wrapper, duration=0.3, timeOffset=time_offset)

    def hide(self):
        if self._visible:
            self._visible = False
            animations.BlinkOut(self._opacity_wrapper)

    def set_text(self, text):
        self._label.text = text

    @threadutils.threaded
    def _start_timer_loop(self):
        while not self.destroyed and self._visible:
            self._on_update(self)
            eveui.wait_for_next_frame()


from dynamicresources.client.ess.bracket.debug import __reload_update__
