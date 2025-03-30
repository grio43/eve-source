#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\progress_bar.py
import carbonui
import eveui
from carbonui import PickState
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui import eveColor, eveThemeColor
import eveicon

class ProgressGauge(eveui.Container):

    def __init__(self, radius = 25, show_label = True, value = 0, disabled = False, bg_opacity = 0.2, state_info = None, line_width = 2, *args, **kwargs):
        kwargs['height'] = kwargs['width'] = radius * 2
        self._disabled = disabled
        self._state_info = state_info
        self._radius = radius
        self._show_label = show_label
        self._bg_opacity = bg_opacity
        self._line_width = line_width
        super(ProgressGauge, self).__init__(*args, **kwargs)
        self.construct_layout()
        self.set_value(value, animate=False)

    def construct_layout(self):
        self.gauge = GaugeCircular(parent=self, align=eveui.Align.center, state=eveui.State.disabled, radius=self._radius - 5, showMarker=False, lineWidth=self._line_width, colorBg=eveColor.BLACK, glow=True, glowBrightness=0.3)
        eveui.Sprite(bgParent=self, texturePath='res:/UI/Texture/circle_full.png', color=eveColor.BLACK, opacity=self._bg_opacity, state=eveui.State.disabled)
        if self._show_label:
            self._progress_label = carbonui.TextDetail(parent=self, align=eveui.Align.center, color=carbonui.TextColor.SECONDARY, state=eveui.State.disabled)
        else:
            self._progress_label = None
            self._state_icon = None
        self._state_icon = eveui.Sprite(parent=self, align=eveui.Align.center, width=16, height=16, texturePath=eveicon.checkmark, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, display=False, pickState=PickState.OFF)
        self._update_state()

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        if self._disabled == value:
            return
        self._disabled = value
        self._update_color()

    def set_value(self, value, animate = True):
        self.gauge.SetValue(value, animate)
        if self._progress_label:
            self._progress_label.SetText(u'{value}%'.format(value=int(value * 100)))
            if not self._state_info:
                is_complete = value >= 1
                self._progress_label.display = not is_complete
                self._state_icon.display = is_complete
        self._update_color()

    def set_state_info(self, state_info):
        self._state_info = state_info
        self._update_state()

    def OnColorThemeChanged(self):
        super(ProgressGauge, self).OnColorThemeChanged()
        self._update_color()

    def _update_state(self):
        if not self._state_icon:
            return
        if self._state_info:
            self._state_icon.texturePath = self._state_info['icon']
            self._state_icon.color = self._state_info['color']
            self._state_icon.hint = self._state_info.get('text', '')
            self._state_icon.display = True
            if self._progress_label:
                self._progress_label.display = False
        else:
            self._state_icon.display = False
            if self._progress_label:
                self._progress_label.display = True

    def _update_color(self):
        if self._state_info and 'color' in self._state_info:
            color = self._state_info['color']
        elif self.gauge.value >= 1:
            color = eveColor.SUCCESS_GREEN
        elif self.disabled:
            color = eveColor.GUNMETAL_GREY
        else:
            color = eveThemeColor.THEME_FOCUS
        self.gauge.SetColor(color, color)
