#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\personal_progress_bar.py
import eveicon
import trinity
from carbonui import Align, uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from jobboard.client.ui.progress_bar import ProgressGauge

class PersonalProgressGauge(ProgressGauge):

    def __init__(self, radius = 25, innerRadius = 11, show_label = False, value = 0, innerValue = 0, disabled = False, bg_opacity = 0.2, state_info = None, line_width = 3, *args, **kwargs):
        self._innerRadius = innerRadius
        self._innerValue = innerValue
        super(PersonalProgressGauge, self).__init__(radius, show_label, value, disabled, bg_opacity, state_info, line_width, *args, **kwargs)
        self.set_inner_value(innerValue, animate=False)

    def construct_layout(self):
        self.innerContainer = Container(parent=self, align=Align.TOALL, state=uiconst.UI_DISABLED)
        self.innerGauge = GaugeCircular(parent=self.innerContainer, align=Align.CENTER, state=uiconst.UI_DISABLED, radius=self._innerRadius, showMarker=False, lineWidth=self._line_width, colorBg=eveColor.BLACK, glow=True, glowBrightness=0.3)
        super(PersonalProgressGauge, self).construct_layout()

    def set_inner_value(self, value, animate = True):
        if value > 0:
            self.innerContainer.Show()
            self.innerGauge.SetValue(value, animate)
        else:
            self.innerContainer.Hide()

    def _update_state(self):
        if not self._state_icon:
            return
        if self._state_info:
            self._state_icon.texturePath = self._state_info['icon']
            self._state_icon.color = self._state_info['icon_color']
            self._state_icon.hint = self._state_info.get('text', '')
            self._state_icon.display = True
            if self._progress_label:
                self._progress_label.display = False
            if 'inner_display' in self._state_info:
                self.innerGauge.display = self._state_info['inner_display']
            else:
                self.innerGauge.display = True
        else:
            self._state_icon.display = False
            self.innerGauge.display = True
            if self._progress_label:
                self._progress_label.display = True

    def _update_color(self):
        super(PersonalProgressGauge, self)._update_color()
        if self._state_info and 'inner_color' in self._state_info:
            color = self._state_info['inner_color']
        elif self.innerGauge.value >= 1:
            color = eveColor.SUCCESS_GREEN
        elif self.disabled:
            color = eveColor.GUNMETAL_GREY
        else:
            color = eveThemeColor.THEME_FOCUS
        self.innerGauge.SetColor(color, color)
