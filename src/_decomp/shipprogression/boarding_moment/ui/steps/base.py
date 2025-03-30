#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\base.py
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from shipprogression.boarding_moment.ui.sounds import get_typing_sound_service, CINEMATIC_SHIP_INTRO_TEXT_1, CINEMATIC_SHIP_INTRO_TEXT_2

class _BoardingUIStepBase(Container):
    default_opacity = 0
    default_state = uiconst.UI_DISABLED
    FADE_IN_DELAY = 0.2
    FADE_IN_DURATION = 0.7
    FADE_OUT_DURATION = 0.7
    LIFE_TIME = 3
    MARGIN_LEFT = 250
    MARGIN_TOP = 250
    MARGIN_BOTTOM = 250

    def ApplyAttributes(self, attributes):
        super(_BoardingUIStepBase, self).ApplyAttributes(attributes)
        self.sound_service = get_typing_sound_service()

    def Start(self, data, duration = 3, delay = 0.2, duration_offset = 0.0):
        self.typeID = data['typeID']
        self.data = data
        self.LIFE_TIME = duration
        self.delay = delay
        self.duration_offset = duration_offset
        self._construct_layout()
        uthread2.StartTasklet(self._sequence)

    def _construct_layout(self):
        pass

    def _sequence(self):
        self.FadeIn()
        self._update()
        self._lifetime()
        self._kill()
        self.FadeOut()
        uthread2.Sleep(self.FADE_OUT_DURATION)
        self.Close()

    def _update(self):
        pass

    def _kill(self):
        pass

    def _lifetime(self):
        uthread2.Sleep(self.LIFE_TIME - self.duration_offset)

    def FadeOut(self):
        animations.FadeOut(self, duration=self.FADE_OUT_DURATION)

    def FadeIn(self):
        animations.FadeIn(self, duration=self.FADE_IN_DURATION, timeOffset=self.FADE_IN_DELAY + self.delay)

    def on_start_typing_1(self):
        self.sound_service.play_sound(CINEMATIC_SHIP_INTRO_TEXT_1)

    def on_stop_typing_1(self):
        self.sound_service.stop_sound(CINEMATIC_SHIP_INTRO_TEXT_1)

    def on_start_typing_2(self):
        self.sound_service.play_sound(CINEMATIC_SHIP_INTRO_TEXT_2)

    def on_stop_typing_2(self):
        self.sound_service.stop_sound(CINEMATIC_SHIP_INTRO_TEXT_2)
