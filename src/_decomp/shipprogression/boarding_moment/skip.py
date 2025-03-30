#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\skip.py
import uthread2
from carbonui import uiconst, Align, TextHeadline, TextHeader
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from localization import GetByLabel

def get_skip_controller(skip_func):
    return SkipController(skip_func)


KEYS_THAT_TRIGGER_SKIPPING = [uiconst.VK_SPACE, uiconst.VK_ESCAPE]

class SkipController(object):

    def __init__(self, skip_func):
        self._skip_func = skip_func
        self._skipped = False
        self._instructions = None
        self._layer = None

    def Start(self, layer):
        self._layer = layer
        self._key_up_cookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.on_key_up)

    def Stop(self):
        if self._instructions:
            self._instructions.Close()
            self._instructions = None
        uicore.event.UnregisterForTriuiEvents(self._key_up_cookie)

    def on_key_up(self, _window, _event_id, key_data, *args):
        key, _ = key_data
        if self._skipped:
            return True
        if key in KEYS_THAT_TRIGGER_SKIPPING:
            self._skipped = True
            self._skip_func()
        else:
            self.show_instructions()
        return True

    def show_instructions(self):
        if not self._instructions:
            self._instructions = SkipInstructions(parent=self._layer)
        self._instructions.show_instructions()


class SkipInstructions(Container):
    default_align = Align.TOALL
    default_opacity = 0.0
    FADE_IN_DURATION = 0.5
    FADE_OUT_DURATION = 0.5
    LIFETIME = 2.0

    def ApplyAttributes(self, attributes):
        super(SkipInstructions, self).ApplyAttributes(attributes)
        self._visible = False
        outerCont = ContainerAutoSize(parent=self, align=Align.CENTERBOTTOM, bgColor=(0, 0, 0, 0.7), top=65)
        instructionContainer = ContainerAutoSize(parent=outerCont, align=Align.CENTER, padding=(30, 10, 30, 10))
        TextHeader(parent=instructionContainer, align=Align.CENTER, text=GetByLabel('UI/ShipProgression/Skip'))

    def show_instructions(self):
        if self._visible:
            return
        self._visible = True
        animations.FadeIn(self, duration=self.FADE_IN_DURATION)
        uthread2.StartTasklet(self._delayed_hide)

    def _delayed_hide(self):
        uthread2.Sleep(self.LIFETIME)
        animations.FadeOut(self, duration=self.FADE_OUT_DURATION)
        self._visible = False
