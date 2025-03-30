#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\addictionwarningtimer.py
import carbonui.const as uiconst
from carbonui.uicore import uicore
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbon.common.script.util.timerstuff import AutoTimer
from eve.common.script.util.notificationconst import notificationTypeAddictionWarning
from gametime import HOUR, MSEC
from globalConfig import GetHoursBetweenAddictionWarnings
from notifications.client.notificationUIConst import NOTIFICATION_CENTER_WIDTH
from regionalui.addictionwarningcontainer import AddictionWarningContainer, FramedAddictionWarningContainer, AddictionWarningExpander
from regionalui.addictionwarningnotification import AddictionWarningNotificationEntry
from regionalui.const import get_ratings_width
from regionalui.utils import get_addiction_warning_text, get_playtime_text
from uthread2 import call_after_wallclocktime_delay

class AddictionWarningTimer(object):
    SECONDS_DISPLAYING_WARNING = 4
    TOLERANCE_TIMER_CHANGES = 0.0001
    POPUP_WIDTH = NOTIFICATION_CENTER_WIDTH
    POPUP_TOP = 60
    POPUP_LEFT = 22
    RATINGS_TOP = 4
    RATINGS_LEFT = 4
    __notifyevents__ = ['OnSettingsOpened', 'OnSettingsCloseStarted', 'OnGlobalConfigChanged']

    def __init__(self):
        sm.RegisterNotify(self)
        self.hours_between_warnings = self.get_hours_between_warnings()
        self.ui_service = sm.GetService('ui')
        self.notification_service = sm.GetService('notificationSvc')
        self.notification_ui_service = sm.GetService('notificationUIService')
        self.notification_ui_service.SetNotificationsAlwaysEnabled(True)
        self.build_time_warnings()
        self.build_ratings()
        self.start_timed_warnings()

    def build_ratings(self):
        self.ratings = AddictionWarningController(parent=uicore.layer.infoBubble, align=uiconst.TOPRIGHT, width=get_ratings_width(), top=self.RATINGS_TOP, left=self.RATINGS_LEFT)

    def show_ratings(self):
        self.ratings.show()

    def close_ratings(self):
        self.ratings.close()

    def build_time_warnings(self):
        self.timed_popups = AddictionWarningNotificationController(parent=uicore.layer.infoBubble, align=uiconst.BOTTOMRIGHT, width=self.POPUP_WIDTH, top=self.POPUP_TOP, left=self.POPUP_LEFT, seconds_displaying_warning=self.SECONDS_DISPLAYING_WARNING)

    def start_timed_warnings(self):
        self.timer = AutoTimer(self.hours_between_warnings * HOUR / MSEC, self.show_timed_warning)

    def show_timed_warning(self):
        if self.ui_service.IsUiVisible() and self.ui_service.IsNotificationCenterAvailable():
            self.notification_service.MakeAndScatterNotification(type=notificationTypeAddictionWarning, data={'subject': get_playtime_text(),
             'subtext': get_addiction_warning_text()})
        else:
            self.timed_popups.show()

    def OnSettingsOpened(self):
        self.show_ratings()

    def OnSettingsCloseStarted(self):
        self.close_ratings()

    def get_hours_between_warnings(self):
        return GetHoursBetweenAddictionWarnings(machoNet=sm.GetService('machoNet'))

    def should_restart_timed_warnings(self, old_timer_value, new_timer_value):
        return not FloatCloseEnough(old_timer_value, new_timer_value, epsilon=self.TOLERANCE_TIMER_CHANGES)

    def OnGlobalConfigChanged(self, *args, **kwargs):
        old_timer_value = self.hours_between_warnings
        new_timer_value = self.get_hours_between_warnings()
        self.hours_between_warnings = new_timer_value
        if self.should_restart_timed_warnings(old_timer_value, new_timer_value):
            self.start_timed_warnings()


class AddictionWarningController(object):
    WARNING_CLASS = AddictionWarningContainer

    def __init__(self, parent, align, width, top, left, seconds_displaying_warning = None):
        self.parent = parent
        self.warning = None
        self.align = align
        self.width = width
        self.top = top
        self.left = left
        self.seconds_displaying_warning = seconds_displaying_warning

    def is_shown(self):
        return self.warning and not self.warning.destroyed

    def show(self):
        self.close()
        self.build_warning()
        if self.seconds_displaying_warning:
            call_after_wallclocktime_delay(self.close, self.seconds_displaying_warning)

    def close(self):
        if self.is_shown():
            self.warning.Close()

    def build_warning(self):
        self.warning = self.WARNING_CLASS(name='AddictionWarning', parent=self.parent, align=self.align, top=self.top, left=self.left, width=self.width, idx=0)


class AddictionWarningNotificationController(AddictionWarningController):
    WARNING_CLASS = AddictionWarningNotificationEntry


class AddictionWarningCollapsibleController(AddictionWarningController):
    WARNING_CLASS = FramedAddictionWarningContainer
    EXPANDER_CLASS = AddictionWarningExpander
    EXPANDER_WIDTH = 40

    def __init__(self, *args, **kwargs):
        self.is_collapsed = True
        self.expander = None
        super(AddictionWarningCollapsibleController, self).__init__(*args, **kwargs)

    def show(self):
        self.is_collapsed = True
        super(AddictionWarningCollapsibleController, self).show()

    def close(self):
        super(AddictionWarningCollapsibleController, self).close()
        if self.expander and not self.expander.destroyed:
            self.expander.Close()

    def build_warning(self):
        self.warning = self.WARNING_CLASS(name='AddictionWarning_Ratings', parent=self.parent, align=self.align, state=uiconst.UI_NORMAL, width=self.width, top=self.top, left=self.left, display=False)
        self.expander = self.EXPANDER_CLASS(name='AddictionWarning_Expander', parent=self.parent, align=self.align, state=uiconst.UI_NORMAL, height=self.warning.get_total_height(), top=self.top, left=self.left, display=False)
        self.update_visibility()
        self.warning.OnMouseExit = lambda : self.update_collapsibility(is_collapsed=True)
        self.expander.OnMouseEnter = lambda : self.update_collapsibility(is_collapsed=False)

    def update_collapsibility(self, is_collapsed):
        if self.is_collapsed == is_collapsed:
            return
        self.is_collapsed = is_collapsed
        self.update_visibility()

    def update_visibility(self):
        self.warning.display = not self.is_collapsed
        self.expander.display = self.is_collapsed
