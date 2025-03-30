#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\animatedtransmissionwindow.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.transform import Transform
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import FrameThemeColored
import log
from uthread2 import StartTasklet
from carbonui.uicore import uicore
OUT_TRANSFORM_SCALING = (1.0, 0.0)
IN_TRANSFORM_SCALING = (1.0, 1.0)
ANIMATION_TIME_SCALE = 1.0
FADE_IN_TRANSFORM_DURATION = 0.2
FADE_OUT_TRANSFORM_DURATION = 0.3
FADE_IN_START_FADE_VALUE = 0.2
FADE_IN_END_FADE_VALUE = 0.5
FADE_OUT_START_FADE_VALUE = 0.2
FADE_OUT_END_FADE_VALUE = 0.05
FADE_IN_START_COLOR = (1, 1, 1, 0.125)
FADE_IN_END_COLOR = (0, 0, 0, 0.25)
FADE_OUT_START_COLOR = (0, 0, 0, 0.1)
FADE_OUT_END_COLOR = (1, 1, 1, 0.1)

class WindowTransition(Container):
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        Frame(bgParent=self, color=(1, 1, 1, 0.1))
        self.cornerPoints = FrameThemeColored(name='bgFrame', colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, bgParent=self, texturePath='res:/UI/Texture/Shared/windowFrame.png', cornerSize=10, fillCenter=False, padding=1, opacity=0.5)
        self.whiteFill = Fill(bgParent=self, color=(1, 1, 1, 0))

    def Close(self):
        self.cornerPoints.Close()
        self.whiteFill.Close()
        super(WindowTransition, self).Close()


class AnimatedWindowFadeState:
    DEFAULT_FADE_STATE = 1
    FADING_IN = 2
    FADING_OUT = 3


class AnimatedTransmissionWindow(Window):
    _transmission_sound_effect = None
    _transmission_sound_duration_seconds = 2.0
    default_isOverlayed = True

    def ApplyAttributes(self, attributes):
        self.transform = None
        Window.ApplyAttributes(self, attributes)
        self.is_processing = True
        self.time_scale = ANIMATION_TIME_SCALE
        self.fade_state = AnimatedWindowFadeState.DEFAULT_FADE_STATE

    def InitializeStatesAndPosition(self, *args, **kwds):
        super(AnimatedTransmissionWindow, self).InitializeStatesAndPosition(*args, **kwds)
        self._fade_in()

    def notify_of_open(self):
        pass

    def notify_of_close(self):
        pass

    def _set_animation_transformation(self, scaling):
        l, t, w, h = self.GetAbsolute()
        idx = 0
        if self.parent is not None:
            idx = self.parent.children.index(self)
        self.transform = Transform(parent=self.parent, state=uiconst.UI_DISABLED, align=uiconst.TOALL, scalingCenter=(float(l + w / 2) / uicore.desktop.width, float(t + h / 2) / uicore.desktop.height), scaling=scaling, idx=idx)
        self.SetParent(self.transform)
        self.transitionBox = WindowTransition(parent=self.transform, pos=self.pos)

    def _fade_in(self):
        if self.fade_state != AnimatedWindowFadeState.DEFAULT_FADE_STATE:
            return
        StartTasklet(self._play_fade_in_transition)

    def _play_fade_in_transition(self):
        if self.transform:
            self.transform.Close()
        self.opacity = 0.0
        self._set_animation_transformation(OUT_TRANSFORM_SCALING)
        self._animate_show_static(FADE_IN_START_FADE_VALUE, FADE_IN_END_FADE_VALUE, FADE_IN_START_COLOR, FADE_IN_END_COLOR)
        self._animate_window_fade_in_from_static()
        self._animate_terminate_static()
        self.is_processing = False

    def Close(self, *args, **kwargs):
        if self.is_processing:
            return
        if self.IsMinimized():
            self.close_window()
        else:
            self.is_processing = True
            self._fade_out_and_close()

    def close_window(self):
        Window.Close(self)
        if self.transform:
            self.transform.Close()

    def _fade_out_and_close(self):
        if self.fade_state != AnimatedWindowFadeState.DEFAULT_FADE_STATE:
            return
        StartTasklet(self._play_fade_out_transition_and_close)

    def _play_fade_out_transition_and_close(self):
        try:
            self.fade_state = AnimatedWindowFadeState.FADING_OUT
            self._set_animation_transformation(IN_TRANSFORM_SCALING)
            self._animate_window_fade_to_static()
            self._animate_show_static(FADE_OUT_START_FADE_VALUE, FADE_OUT_END_FADE_VALUE, FADE_OUT_START_COLOR, FADE_OUT_END_COLOR)
            self._animate_terminate_window()
            self._animate_transform_static(IN_TRANSFORM_SCALING, OUT_TRANSFORM_SCALING, FADE_OUT_TRANSFORM_DURATION, sleep=True)
            self._animate_terminate_static()
        except Exception as e:
            log.LogException(extraText='Error playing AnimationWindow fadeout animation', exc=e)
        finally:
            self.notify_of_close()
            self.close_window()

    def _animate_window_fade_in_from_static(self):
        uicore.animations.BlinkIn(obj=self.transitionBox.cornerPoints, loops=5, duration=0.3 * self.time_scale)
        uicore.animations.FadeIn(obj=self, duration=0.3 * self.time_scale, sleep=True)

    def _animate_window_fade_to_static(self):
        uicore.animations.BlinkOut(self.transitionBox.cornerPoints, loops=5, duration=0.3 * self.time_scale)
        uicore.animations.FadeOut(self, duration=0.2 * self.time_scale, sleep=True)

    def _animate_show_static(self, start_fade_value, end_fade_value, start_color, end_color):
        uicore.animations.FadeTo(obj=self.transitionBox.whiteFill, startVal=start_fade_value, endVal=end_fade_value, duration=0.1 * self.time_scale, sleep=True)
        uicore.animations.SpColorMorphTo(obj=self.transitionBox.whiteFill, startColor=start_color, endColor=end_color, duration=0.1 * self.time_scale)

    def _animate_terminate_window(self):
        self.display = False

    def _animate_transform_static(self, start_scale, end_scale, duration, sleep):
        uicore.animations.Tr2DScaleTo(obj=self.transform, startScale=start_scale, endScale=end_scale, duration=duration * self.time_scale, sleep=sleep)

    def _animate_terminate_static(self):
        if not self.destroyed:
            self.SetParent(uicore.layer.alwaysvisible, idx=0)
        self.transform.Close()
        self.fade_state = AnimatedWindowFadeState.DEFAULT_FADE_STATE
