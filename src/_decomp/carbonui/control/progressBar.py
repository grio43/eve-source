#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\progressBar.py
import math
import blue
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.themeColored import FillThemeColored

class ProgressBar(Container):
    default_name = 'ProgressBar'
    default_barWidth = 5
    default_duration = 3.0
    default_pauseTime = 1.0
    default_state = uiconst.UI_DISABLED
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.barWidth = attributes.get('barWidth', self.default_barWidth)
        self.duration = attributes.get('duration', self.default_duration)
        self.pauseTime = attributes.get('pauseTime', self.default_pauseTime)
        w, _ = self.GetAbsoluteSize()
        self.bars = []
        for i in xrange(w / self.barWidth + 1):
            bar = Bar(align=uiconst.TOLEFT, parent=self, opacity=0.75, width=self.barWidth, padLeft=0)
            self.bars.append(bar)

        uthread.new(self.Animate)

    def Animate(self):
        time = 0.0
        duration = 5.0
        numTotal = len(self.bars)
        n = 0
        while not self.destroyed:
            blue.synchro.Yield()
            if not self.display:
                continue
            time += 1.0 / blue.os.fps
            if time > duration:
                time -= duration
                n += 2
                if n > numTotal:
                    n = 0
            t = time / duration
            k = 2 * math.pi
            for i, bar in enumerate(self.bars):
                x = float(i) / (numTotal - 1)
                fT = 1.0
                fX = -1.0
                bar.value = 2.0 * math.sin(k * (fT * t - fX * x))
                fT = 2.0
                fX = 1.0
                bar.value += 0.5 * math.sin(k * (fT * t - fX * x))
                fT = 3.0
                fX = 2.0
                bar.value += 0.7 * math.sin(k * (fT * t - fX * x))
                fT = 3.0
                fX = -2.0
                bar.value += 0.7 * math.sin(k * (fT * t - fX * x))


class Bar(Container):
    default_name = 'Bar'

    def __init__(self, **kwargs):
        self._value = 0.0
        super(Bar, self).__init__(**kwargs)
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        value = max(0.25, value)
        self._value = value
        self.opacity = value
