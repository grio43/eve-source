#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\page\base.py
import signals
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations

class Page(Container):
    default_align = uiconst.TOALL
    default_state = uiconst.UI_DISABLED
    default_left = 24
    default_opacity = 0.0
    ANIMATION_DURATION = 0.3

    def __init__(self):
        self.on_back = signals.Signal()
        super(Page, self).__init__()

    def load(self):
        pass

    def unload(self):
        self.Flush()

    def reload(self):
        self.unload()
        self.load()

    def go_back(self):
        self.on_back()

    def show_immediately(self):
        self.opacity = 1.0
        self.left = 0
        self.state = uiconst.UI_PICKCHILDREN

    def disable(self):
        self.state = uiconst.UI_DISABLED

    def enable(self):
        self.state = uiconst.UI_PICKCHILDREN

    def animate_popped_out(self, callback = None):
        self._animate('out', 'right', callback)

    def animate_pushed_in(self, callback = None):
        self._animate('in', 'right', callback)

    def animate_pushed_out(self, callback = None):
        self._animate('out', 'left', callback)

    def animate_popped_in(self, callback = None):
        self._animate('in', 'left', callback)

    def _animate(self, direction, side, callback = None):

        def resolve(on_value, off_value):
            value = on_value if direction == 'in' else off_value
            modifier = -1.0 if side == 'right' else 1.0
            return value * modifier

        animations.MorphScalar(self, 'left', startVal=self.left, endVal=resolve(0, -24), duration=self.ANIMATION_DURATION)
        animations.MorphScalar(self, 'padRight', startVal=self.padRight, endVal=resolve(0, 24), duration=self.ANIMATION_DURATION)
        animations.FadeTo(self, startVal=self.opacity, endVal=abs(resolve(1.0, 0.0)), duration=self.ANIMATION_DURATION, callback=callback)
