#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\widgets\timerwidget.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import uthread2
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
import gametime
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from localization.formatters import FormatTimeIntervalShort
from progression.client.const import COLOR_ATTENTION_FOREGROUND, COLOR_ATTENTION_BACKGROUND, COLOR_INFO_FOREGROUND, COLOR_INFO_BACKGROUND, COLOR_UI_HIGHLIGHTING, WIDGET_TEXT_BOLD_WHITE
from progression.client.widgets.basewidget import BaseWidget
from progression.common.widgets import TaskWidgetMode

def get_timer_colors(widget_mode):
    if widget_mode == TaskWidgetMode.TASK_WIDGET_MODE_ATTENTION:
        return (COLOR_ATTENTION_FOREGROUND, COLOR_ATTENTION_BACKGROUND)
    return (COLOR_INFO_FOREGROUND, COLOR_INFO_BACKGROUND)


class TimerWidget(BaseWidget):

    def ApplyAttributes(self, attributes):
        super(TimerWidget, self).ApplyAttributes(attributes)
        if attributes.widget_state:
            self.start_time, self.duration_seconds = attributes.widget_state
        else:
            self.start_time, self.duration_seconds = (None, None)
        self.text = attributes.static_data.text
        self.mode = attributes.static_data.mode
        self.mainContainer.Flush()
        self._ConstructGauge()
        self.textContainer = ContainerAutoSize(parent=self.mainContainer, align=uiconst.TOLEFT, height=16)
        self.labelContainer = ContainerAutoSize(parent=self.mainContainer, align=uiconst.TORIGHT, height=16)
        color_foreground, _ = get_timer_colors(self.mode)
        self.countdown_label = EveLabelMediumBold(parent=self.labelContainer, text='', align=uiconst.TOLEFT, padRight=10, color=color_foreground)
        self._ConstructText()
        self._UpdateTimerLabelUntilCountdownCompletes()

    def _GetRatio(self):
        time_remaining = gametime.GetSecondsUntilWallclockTime(self.start_time + self.duration_seconds * gametime.SEC)
        ratio = time_remaining / float(self.duration_seconds)
        ratio = min(1.0, max(0.0, ratio))
        return ratio

    def _ConstructText(self):
        if self.mode == TaskWidgetMode.TASK_WIDGET_MODE_ATTENTION:
            label_cls = EveLabelMediumBold
            color = COLOR_ATTENTION_FOREGROUND
        else:
            label_cls = EveLabelMedium
            color = WIDGET_TEXT_BOLD_WHITE
        self.label = label_cls(parent=self.textContainer, text=self.text, align=uiconst.TOLEFT, color=color)

    def _UpdateTimerLabelUntilCountdownCompletes(self):
        self.close_if_done()
        if self.start_time is None or self.duration_seconds is None:
            return
        time_remaining = gametime.GetSecondsUntilWallclockTime(self.start_time + self.duration_seconds * gametime.SEC)
        if time_remaining <= 0:
            return
        seconds_remaining = int(round(time_remaining)) * gametime.SEC
        text = FormatTimeIntervalShort(seconds_remaining, 'minute')
        self.countdown_label.SetText(text)
        now = gametime.GetSimTime()
        time_to_wait = gametime.SEC - now % gametime.SEC
        seconds_to_wait = float(time_to_wait) / gametime.SEC
        uthread2.call_after_simtime_delay(self._UpdateTimerLabelUntilCountdownCompletes, seconds_to_wait)

    def _ConstructGauge(self):
        if self.start_time is None or self.duration_seconds is None:
            return
        time_remaining = gametime.GetSecondsUntilWallclockTime(self.start_time + self.duration_seconds * gametime.SEC)
        if time_remaining <= 0:
            return
        color_foreground, color_background = get_timer_colors(self.mode)
        self.gaugeCircular = GaugeCircular(parent=self.mainContainer, radius=8, align=uiconst.TORIGHT, colorStart=color_foreground, colorEnd=color_foreground, colorBg=color_background, lineWidth=2.5, clockwise=True, showMarker=False, state=uiconst.UI_DISABLED)
        ratio = self._GetRatio()
        self.gaugeCircular.SetValue(ratio, animate=False)
        self.gaugeCircular.SetValueTimed(0, time_remaining)

    def get_time_remaining(self):
        if self.start_time is None or self.duration_seconds is None:
            return 0
        return gametime.GetSecondsUntilWallclockTime(self.start_time + self.duration_seconds * gametime.SEC)

    def close_if_done(self):
        if self.get_time_remaining() <= 0:
            if self.parent:
                self.parent.Close()

    def OnMouseEnter(self, *args):
        self.label.SetTextColor(COLOR_UI_HIGHLIGHTING)
        super(TimerWidget, self).OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        if self.mode == TaskWidgetMode.TASK_WIDGET_MODE_ATTENTION:
            self.label.SetTextColor(COLOR_ATTENTION_FOREGROUND)
        else:
            self.label.SetTextColor(WIDGET_TEXT_BOLD_WHITE)
        super(TimerWidget, self).OnMouseExit(*args)
