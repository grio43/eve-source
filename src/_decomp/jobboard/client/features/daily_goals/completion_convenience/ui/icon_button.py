#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\ui\icon_button.py
import eveicon
import eveui
import uthread2
from carbonui import Align, uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_GENERIC, TOOLTIP_DELAY_GENERIC
from jobboard.client.features.daily_goals.completion_convenience import completion_convenience_signals as cc_signals
import dailygoals.client.goalSignals as dailyGoalSignals
from eveui import animate, Mouse
from jobboard.client.features.daily_goals.completion_convenience.ui.tooltip_button import load_tooltip_with_button
from jobboard.client.features.daily_goals.completion_convenience.util import can_pay_for_completion

class CompletionConvenienceIcon(ContainerAutoSize):
    default_align = Align.TORIGHT
    default_state = uiconst.UI_NORMAL
    default_alignMode = Align.CENTERRIGHT
    ANIM_DURATION = 0.2

    def __init__(self, job, icon_size = 16, *args, **kwargs):
        super(CompletionConvenienceIcon, self).__init__(*args, **kwargs)
        self._job = job
        self._hover = False
        self._open = False
        self._glow_amount_idle = 0.0
        self._glow_amount_hover = 0.3
        self._glow_amount_click = 0.8
        self._em_icon = GlowSprite(name='em_icon', parent=self, state=uiconst.UI_DISABLED, align=Align.CENTERRIGHT, width=icon_size, height=icon_size, icon_size=icon_size, texturePath=eveicon.evermark, color=eveColor.EVERMARK_GREEN)
        self._register()

    def Close(self):
        super(CompletionConvenienceIcon, self).Close()
        self._unregister()

    def _register(self):
        dailyGoalSignals.on_completed.connect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.connect(self._on_pay_for_completion_successful)

    def _unregister(self):
        dailyGoalSignals.on_completed.disconnect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.disconnect(self._on_pay_for_completion_successful)

    def _update_icon_state(self):
        if self._hover or self._open:
            if Mouse.left.is_down:
                glow_amount = self._glow_amount_click
                self._em_icon.glowAmount = glow_amount
                return
            glow_amount = self._glow_amount_hover
        else:
            glow_amount = self._glow_amount_idle
        animate(self._em_icon, 'glowAmount', end_value=glow_amount, duration=0.2)

    def OnMouseEnter(self, *args):
        self._hover = True
        self._update_icon_state()

    def OnMouseExit(self, *args):
        self._hover = False
        self._update_icon_state()

    def OnMouseDown(self, *args):
        self._update_icon_state()

    def OnClick(self, *args):
        self._update_icon_state()
        self._open_tooltip()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_GENERIC, TOOLTIP_DELAY_GENERIC)

    def _open_tooltip_delayed(self, delayInSeconds):
        uthread2.Sleep(delayInSeconds)
        self._open_tooltip()

    def _open_tooltip(self):
        uicore.uilib.tooltipHandler.LoadTooltipImmediate()

    def LoadTooltipPanel(self, tooltip_panel, *args):
        load_tooltip_with_button(tooltip_panel, self._job)

    def OnTooltipPanelOpened(self):
        self._open = True

    def OnTooltipPanelClosed(self):
        if self.destroyed:
            return
        if not self._open:
            return
        self._open = False
        self._update_icon_state()

    def _on_daily_goal_completed(self, goal_id):
        if self._job.goal_id == goal_id or not can_pay_for_completion(self._job):
            self.Close()

    def _on_pay_for_completion_successful(self, goal_id):
        if self._job.goal_id == goal_id or not can_pay_for_completion(self._job):
            self.Close()
