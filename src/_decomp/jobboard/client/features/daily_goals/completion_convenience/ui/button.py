#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\ui\button.py
import eveicon
from carbonui import Align, ButtonVariant, uiconst
from carbonui.control.button import Button
from carbonui.uianimations import animations
from eve.client.script.ui.control.infoIcon import WarningGlyphIcon
from jobboard.client.features.daily_goals.completion_convenience.button_blocker import get_button_blocker
from jobboard.client.features.daily_goals.completion_convenience.const import ERROR_MESSAGES
from jobboard.client.features.daily_goals.completion_convenience.ui.tooltip import load_tooltip
from jobboard.client.features.daily_goals.completion_convenience.util import can_afford_completion_convenience, pay_for_completion, can_pay_for_completion
from localization import GetByLabel
import dailygoals.client.goalSignals as dailyGoalSignals
from jobboard.client.features.daily_goals.completion_convenience import completion_convenience_signals as cc_signals
BUTTON_STATE_INITIAL = 1
BUTTON_STATE_CONFIRM = 2
BUTTON_STATE_PROCESSING = 3
BUTTON_STATE_COMPLETE = 4
BUTTON_STATE_DISABLED = 5
BUTTON_STATE_ERROR = 6

class _CompletionConvenienceButtonBase(Button):
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']

    def ApplyAttributes(self, attributes):
        self._button_state = None
        self._error_code = None
        self._error_icon = None
        super(_CompletionConvenienceButtonBase, self).ApplyAttributes(attributes)
        self.job = attributes.job
        self.func = self.on_click
        self._set_state(self.get_initial_state())
        self._error_icon = WarningGlyphIcon(parent=self, align=Align.TOPRIGHT, hint=GetByLabel('UI/DailyGoals/CompletionConvenienceErrorMessage'), top=-4, left=-4)
        self._error_icon.Hide()
        self._register()

    def Close(self):
        super(_CompletionConvenienceButtonBase, self).Close()
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)
        cc_signals.buttons_blocked.connect(self._buttons_blocked)
        cc_signals.buttons_unblocked.connect(self._buttons_unblocked)
        dailyGoalSignals.on_completed.connect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.connect(self._on_pay_for_completion_successful)
        dailyGoalSignals.on_pay_for_completion_failed.connect(self._on_pay_for_completion_failed)

    def _unregister(self):
        sm.UnregisterNotify(self)
        cc_signals.buttons_blocked.disconnect(self._buttons_blocked)
        cc_signals.buttons_unblocked.disconnect(self._buttons_unblocked)
        dailyGoalSignals.on_completed.disconnect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.disconnect(self._on_pay_for_completion_successful)
        dailyGoalSignals.on_pay_for_completion_failed.disconnect(self._on_pay_for_completion_failed)

    def get_initial_state(self):
        if not can_afford_completion_convenience():
            return BUTTON_STATE_DISABLED
        if get_button_blocker().is_blocked:
            if get_button_blocker().current_goal_id == self.job.goal_id:
                return BUTTON_STATE_PROCESSING
            return BUTTON_STATE_DISABLED
        return BUTTON_STATE_INITIAL

    def on_click(self, *args):
        if self._button_state is BUTTON_STATE_INITIAL:
            self._set_state(BUTTON_STATE_CONFIRM)
        elif self._button_state is BUTTON_STATE_CONFIRM:
            self._set_state(BUTTON_STATE_PROCESSING)
            self._process()

    def _set_state(self, buttonState):
        if buttonState == self._button_state:
            return
        self._button_state = buttonState
        animations.StopAllAnimations(self)
        if buttonState is BUTTON_STATE_INITIAL:
            self._set_state_initial()
        elif buttonState is BUTTON_STATE_CONFIRM:
            self._set_state_confirm()
        elif buttonState is BUTTON_STATE_PROCESSING:
            self._set_state_processing()
        elif buttonState is BUTTON_STATE_COMPLETE:
            self._set_state_complete()
        elif buttonState is BUTTON_STATE_DISABLED:
            self._set_state_disabled()
        elif buttonState is BUTTON_STATE_ERROR:
            self._set_state_error()

    def _set_error(self, error_code):
        self._error_code = error_code
        self._set_state(BUTTON_STATE_ERROR)

    def _set_state_initial(self):
        self.enable()
        self.texturePath = eveicon.evermark
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonInitial')
        self.busy = False
        self.variant = ButtonVariant.GHOST
        animations.FadeTo(self, startVal=self.opacity, endVal=1, duration=0.2)
        if self._error_icon:
            self._error_icon.Hide()

    def _set_state_confirm(self):
        self.texturePath = None
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonConfirm')
        self.busy = False
        self.variant = ButtonVariant.PRIMARY
        animations.FadeTo(self, startVal=1, endVal=1.7, duration=0.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        if self._error_icon:
            self._error_icon.Hide()

    def _set_state_processing(self):
        self.texturePath = None
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonProcessing')
        self.busy = True
        self.opacity = 1
        animations.FadeTo(self, startVal=self.opacity, endVal=1, duration=0.2)
        if self._error_icon:
            self._error_icon.Hide()

    def _set_state_complete(self):
        self.disable()
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonComplete')
        self.busy = False
        animations.FadeTo(self, startVal=self.opacity, endVal=1, duration=0.2)
        if self._error_icon:
            self._error_icon.Hide()

    def _set_state_disabled(self):
        self.disable()
        self.texturePath = eveicon.evermark
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonInitial')
        self.busy = False
        self.variant = ButtonVariant.NORMAL
        animations.FadeTo(self, startVal=self.opacity, endVal=1, duration=0.2)
        if self._error_icon:
            self._error_icon.Hide()

    def _set_state_error(self):
        self.disable()
        self.label = GetByLabel('UI/DailyGoals/CompletionConvenienceButtonError')
        self.busy = False
        self.variant = ButtonVariant.NORMAL
        animations.FadeTo(self, startVal=self.opacity, endVal=1, duration=0.2)
        if self._error_code in ERROR_MESSAGES:
            error_text = GetByLabel(ERROR_MESSAGES[self._error_code])
            self._error_icon.SetHint(error_text)
        else:
            self._error_icon.SetHint(GetByLabel('UI/DailyGoals/CompletionConvenienceErrorMessage'))
        if self._error_icon:
            self._error_icon.Show()

    def _process(self):
        pay_for_completion(self.job)

    def OnCharacterLPBalanceChange_Local(self, issuerCorpID, _lpBefore, _lpAfter):
        if self.busy:
            return
        self._update()
        if can_afford_completion_convenience(_lpAfter):
            self._set_state(BUTTON_STATE_INITIAL)
        else:
            self._set_state(BUTTON_STATE_DISABLED)

    def _buttons_blocked(self, goal_id):
        if self.job.goal_id == goal_id:
            return
        self._set_state(BUTTON_STATE_DISABLED)

    def _buttons_unblocked(self, goal_id):
        if self.job.goal_id == goal_id:
            return
        self._set_state(self.get_initial_state())

    def _on_daily_goal_completed(self, goal_id):
        if self.job.goal_id == goal_id or not can_pay_for_completion(self.job):
            if self._button_state != BUTTON_STATE_COMPLETE:
                self._set_state(BUTTON_STATE_DISABLED)
            self._update()

    def _on_pay_for_completion_successful(self, goal_id):
        if self.job.goal_id == goal_id:
            self._set_state(BUTTON_STATE_COMPLETE)
            self._update()

    def _on_pay_for_completion_failed(self, goal_id, status_code):
        if self.job.goal_id == goal_id:
            self._set_error(status_code)

    def _update(self):
        if not can_pay_for_completion(self.job):
            self.Close()


class CompletionConvenienceTooltipButton(_CompletionConvenienceButtonBase):
    default_variant = ButtonVariant.GHOST


class CompletionConvenienceButton(_CompletionConvenienceButtonBase):

    def __init__(self, get_menu_entry_data_func = None, **kwargs):
        self.WIDTH = None
        super(CompletionConvenienceButton, self).__init__(get_menu_entry_data_func=get_menu_entry_data_func, **kwargs)

    def _set_state(self, buttonState):
        if not can_pay_for_completion(self.job):
            self.Hide()
            return
        super(CompletionConvenienceButton, self)._set_state(buttonState)
        if self.WIDTH is None:
            self.WIDTH = self.get_intrinsic_width()
        self.width = self.WIDTH

    def _set_state_complete(self):
        super(CompletionConvenienceButton, self)._set_state_complete()
        self._close(0.15)

    def _close(self, duration):
        animations.FadeOut(self, duration=duration)
        animations.MorphScalar(self, 'width', startVal=self.WIDTH, endVal=0, duration=duration, timeOffset=duration / 2.0, callback=self._on_close_complete)

    def _on_close_complete(self, *args):
        self.Hide()

    def GetTooltipDelay(self):
        return 0

    def LoadTooltipPanel(self, tooltip_panel, *args):
        load_tooltip(tooltip_panel)

    def _update(self):
        pass
