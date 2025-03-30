#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\linear_progress.py
import eveui
import threadutils
import trinity
import uthread2

class LinearProgress(eveui.Container):
    default_height = 2
    default_opacity = 0.75
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_background_color = (0.5, 0.5, 0.5, 1.0)

    def __init__(self, value = 0, color = None, background_color = None, **kwargs):
        self._color = color or self.default_color
        self._background_color = background_color or self.default_background_color
        super(LinearProgress, self).__init__(**kwargs)
        self._value = value
        self._layout()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        eveui.animate(self._progress_fill, 'width', end_value=value, duration=0.3)

    def _layout(self):
        self._progress_fill = eveui.Fill(parent=self, align=eveui.Align.to_left_prop, width=0, color=self._color)
        eveui.Fill(parent=self, color=self._background_color)

    @threadutils.threaded
    def pulse(self, duration):
        self._pulse_line.width = self._progress_fill.GetAbsoluteSize()[0]
        self._pulse_line.pulse(duration)

    @eveui.lazy
    def _pulse_line(self):
        return PulseLine(parent=self, align=eveui.Align.center_left, height=self.height, idx=0)


class PulseLine(eveui.Container):
    default_name = 'PulseLine'
    default_clipChildren = True

    def __init__(self, **kwargs):
        super(PulseLine, self).__init__(**kwargs)
        self.sprite = eveui.GradientSprite(parent=self, align=eveui.Align.to_left, alphaData=[(0, 0), (0.6, 1), (1, 0)], rgbData=[(0, (1, 1, 1))], width=40, left=-40, opacity=1.5, blendMode=trinity.TR2_SBM_ADD)

    @threadutils.threaded
    def pulse(self, duration):
        self.sprite.width = self.width * 0.7
        start = -self.sprite.width
        end = self.width
        eveui.animate(self.sprite, 'left', start_value=start, end_value=end, duration=duration)
        uthread2.sleep(duration - 0.1)
