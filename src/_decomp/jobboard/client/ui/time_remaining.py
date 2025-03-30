#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\time_remaining.py
import gametime
import datetimeutils
from carbonui.primitives.container import Sprite
import carbonui
import eveicon
from eve.client.script.ui import eveColor
from carbonui.util.color import Color
import eveui
import uthread2
import localization
from eve.client.script.ui.control.tooltips import TooltipPanel
TIME_REMAINING_NEUTRAL_COLOR = carbonui.TextColor.NORMAL
TIME_REMAINING_DANGER_COLOR = list(eveColor.DANGER_RED[:3]) + [carbonui.TextColor.NORMAL.opacity]
TIME_REMAINING_WARNING_COLOR = list(eveColor.WARNING_ORANGE[:3]) + [carbonui.TextColor.NORMAL.opacity]

class TimeRemaining(eveui.ContainerAutoSize):
    default_align = carbonui.Align.TORIGHT
    default_alignMode = carbonui.Align.TOPLEFT

    def __init__(self, job, icon_size = 16, get_text = None, *args, **kwargs):
        super(TimeRemaining, self).__init__(*args, **kwargs)
        self._job = job
        self._get_text = get_text or _get_job_expiration_text
        self._expiration_icon = Sprite(name='time_remaining_icon', parent=self, state=eveui.State.disabled, align=carbonui.Align.CENTERLEFT, width=icon_size, height=icon_size, texturePath=eveicon.hourglass, opacity=carbonui.TextColor.HIGHLIGHT.opacity)
        self._expiration_label = carbonui.TextBody(parent=self, align=carbonui.Align.TOPLEFT, left=icon_size + 4, color=_get_time_color_text(self._job.expiration_time))
        uthread2.start_tasklet(self._time_remaining_routine)

    def _time_remaining_routine(self):
        while not self.destroyed:
            if self._job.is_expired:
                self.Close()
                break
            self._expiration_icon.color = _get_time_color_icon(self._job.expiration_time)
            self._expiration_label.color = _get_time_color_text(self._job.expiration_time)
            self._expiration_label.text = self._get_text(self._job)
            uthread2.sleep(1)


class TimeRemainingIcon(eveui.ContainerAutoSize):
    default_align = carbonui.Align.TORIGHT
    default_state = eveui.State.normal

    def __init__(self, job, icon_size = 16, get_text = None, *args, **kwargs):
        super(TimeRemainingIcon, self).__init__(*args, **kwargs)
        self._job = job
        self._get_text = get_text or _get_job_expiration_text
        self._expiration_icon = Sprite(name='time_remaining_icon', parent=self, state=eveui.State.disabled, align=carbonui.Align.CENTER, width=icon_size, height=icon_size, texturePath=eveicon.hourglass, color=_get_time_color_icon(self._job.expiration_time), opacity=carbonui.TextColor.NORMAL.opacity)
        uthread2.start_tasklet(self._time_remaining_routine)

    def _time_remaining_routine(self):
        while not self.destroyed:
            self._refresh_color()
            if self._job.is_expired:
                break
            uthread2.sleep(5)

    def _refresh_color(self):
        color = _get_time_color_icon(self._job.expiration_time)
        self._expiration_icon.color = color

    def OnMouseEnter(self, *args):
        super(TimeRemainingIcon, self).OnMouseEnter(*args)
        self._refresh_color()

    def ConstructTooltipPanel(self):
        return TimeRemainingTooltip(self._job, self._get_text)


class TimeRemainingTooltip(TooltipPanel):

    def __init__(self, job, get_text = None):
        super(TimeRemainingTooltip, self).__init__()
        self._job = job
        self._get_text = get_text or _get_job_expiration_text

    def ApplyAttributes(self, attributes):
        super(TimeRemainingTooltip, self).ApplyAttributes(attributes)
        self.LoadGeneric1ColumnTemplate()
        self._timer_label = self.AddLabelMedium()
        uthread2.start_tasklet(self._time_remaining_routine)

    def _time_remaining_routine(self):
        while not self.destroyed:
            color = _get_time_color_text(self._job.expiration_time)
            self._timer_label.color = color
            self._timer_label.text = self._get_text(self._job)
            if self._job.is_expired:
                break
            uthread2.sleep(1)


def _get_job_expiration_text(job):
    time_now = gametime.GetWallclockTime()
    time_remaining = job.expiration_time - time_now
    if time_remaining <= 0:
        return localization.GetByLabel('UI/Generic/Expired')
    else:
        return localization.GetByLabel('UI/Generic/ExpiresIn', color=_get_time_color_time(job.expiration_time), remaining=time_remaining)


def _get_time_color_icon(timestamp):
    if timestamp is None:
        return carbonui.TextColor.DISABLED
    remaining_hours = _get_hours_until(timestamp)
    if remaining_hours < 6:
        return eveColor.CHERRY_RED
    if remaining_hours < 24:
        return eveColor.DUSKY_ORANGE
    return carbonui.TextColor.DISABLED


def _get_time_color_text(timestamp):
    if timestamp is None:
        return carbonui.TextColor.SECONDARY
    remaining_hours = _get_hours_until(timestamp)
    if remaining_hours < 6:
        return eveColor.CHERRY_RED
    if remaining_hours < 24:
        return eveColor.DUSKY_ORANGE
    return carbonui.TextColor.SECONDARY


def _get_time_color_time(timestamp):
    if timestamp is None:
        return Color.RGBtoHex(*carbonui.TextColor.NORMAL)
    remaining_hours = _get_hours_until(timestamp)
    if remaining_hours < 6:
        return eveColor.DANGER_RED_HEX
    if remaining_hours < 24:
        return eveColor.WARNING_ORANGE_HEX
    return Color.RGBtoHex(*carbonui.TextColor.NORMAL)


def _get_hours_until(timestamp):
    timestamp_datetime = datetimeutils.filetime_to_datetime(timestamp)
    remaining_time_delta = timestamp_datetime - gametime.now()
    remaining_seconds = remaining_time_delta.total_seconds()
    return int(float(remaining_seconds) / 3600)
