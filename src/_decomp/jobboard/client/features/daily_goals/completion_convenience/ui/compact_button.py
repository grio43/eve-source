#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\completion_convenience\ui\compact_button.py
import eveicon
import eveui
import uthread2
from carbonui import TextColor, Align, uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from chroma import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.tooltips.tooltipHandler import TOOLTIP_SETTINGS_GENERIC, TOOLTIP_DELAY_GENERIC
from eveui import Sprite
from jobboard.client.features.daily_goals.completion_convenience import completion_convenience_signals as cc_signals
import dailygoals.client.goalSignals as dailyGoalSignals
from jobboard.client.features.daily_goals.completion_convenience.const import TEXT_COLOR_EVERMARK_GREEN
from jobboard.client.features.daily_goals.completion_convenience.ui.tooltip_button import load_tooltip_with_button
from jobboard.client.features.daily_goals.completion_convenience.util import can_pay_for_completion

class CompactCompletionConvenienceButton(Container):
    MINIMIZED_BG_OPACITY = 0.5
    EXPANDED_BG_OPACITY = 1
    DOT_OPACITY = TextColor.NORMAL.opacity
    EM_OPACITY = TextColor.HIGHLIGHT.opacity
    MINIMIZED_SIZE = 16
    EXPANDED_SIZE = 22
    CLICKED_SIZE = 18
    ANIM_DURATION = 0.2
    default_align = Align.CENTER
    default_width = MINIMIZED_SIZE
    default_height = MINIMIZED_SIZE
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self._open = False
        self._block = False
        self._expanded = False
        self._hover = False
        super(CompactCompletionConvenienceButton, self).ApplyAttributes(attributes)
        self.job = attributes.job
        self._dot = Sprite(name='ptc_em_icon', parent=self, align=Align.CENTER, color=TextColor.NORMAL, texturePath=eveicon.dot, width=16, height=16, state=uiconst.UI_DISABLED)
        self._em_icon = Sprite(name='ptc_em_icon', parent=self, align=Align.CENTER, color=TextColor.HIGHLIGHT, texturePath=eveicon.evermark, width=16, height=16, opacity=0, state=uiconst.UI_DISABLED)
        Sprite(name='ptc_bg', parent=self, align=Align.TOALL, color=eveColor.BLACK, texturePath='res:/UI/Texture/shared/bg_circle.png', state=uiconst.UI_DISABLED)
        self._register()

    def Close(self):
        super(CompactCompletionConvenienceButton, self).Close()
        self._unregister()

    def _register(self):
        cc_signals.buttons_blocked.connect(self._purchase_started)
        dailyGoalSignals.on_completed.connect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.connect(self._on_pay_for_completion_successful)

    def _unregister(self):
        cc_signals.buttons_blocked.disconnect(self._purchase_started)
        dailyGoalSignals.on_completed.disconnect(self._on_daily_goal_completed)
        dailyGoalSignals.on_pay_for_completion_successful.disconnect(self._on_pay_for_completion_successful)

    def expand(self):
        self._expanded = True
        animations.MorphScalar(self, 'width', self.width, self.EXPANDED_SIZE, self.ANIM_DURATION)
        animations.MorphScalar(self, 'height', self.height, self.EXPANDED_SIZE, self.ANIM_DURATION)
        fadeDuration = self.ANIM_DURATION / 2.0
        animations.FadeOut(self._dot, duration=fadeDuration)
        animations.FadeIn(self._em_icon, endVal=self.EM_OPACITY, duration=fadeDuration, timeOffset=fadeDuration)

    def minimize(self):
        self._expanded = False
        if self._open:
            return
        animations.MorphScalar(self, 'width', self.width, self.MINIMIZED_SIZE, self.ANIM_DURATION)
        animations.MorphScalar(self, 'height', self.height, self.MINIMIZED_SIZE, self.ANIM_DURATION)
        fadeDuration = self.ANIM_DURATION / 2.0
        animations.FadeOut(self._em_icon, duration=fadeDuration)
        animations.FadeIn(self._dot, endVal=self.DOT_OPACITY, duration=fadeDuration, timeOffset=fadeDuration)

    def highlight(self):
        animations.SpColorMorphTo(obj=self._em_icon, startColor=self._em_icon.GetRGB(), endColor=Color(*TEXT_COLOR_EVERMARK_GREEN).rgb, duration=self.ANIM_DURATION)

    def unhighlight(self):
        animations.SpColorMorphTo(obj=self._em_icon, startColor=self._em_icon.GetRGB(), endColor=TextColor.HIGHLIGHT.rgb, duration=self.ANIM_DURATION)

    def OnMouseEnter(self, *args):
        self._hover = True
        self.highlight()

    def OnMouseExit(self, *args):
        self._hover = False
        if not self._open:
            self.unhighlight()

    def OnClick(self, *args):
        animations.MorphScalar(self, 'width', self.CLICKED_SIZE, self.EXPANDED_SIZE, 0.1)
        animations.MorphScalar(self, 'height', self.CLICKED_SIZE, self.EXPANDED_SIZE, 0.1)
        animations.MorphScalar(self._em_icon, 'width', 14, self._em_icon.width, 0.1)
        animations.MorphScalar(self._em_icon, 'height', 14, self._em_icon.height, 0.1)
        self._open_tooltip()

    def GetTooltipDelay(self):
        return settings.user.ui.Get(TOOLTIP_SETTINGS_GENERIC, TOOLTIP_DELAY_GENERIC)

    def LoadTooltipPanel(self, tooltip_panel, *args):
        load_tooltip_with_button(tooltip_panel, self.job)

    def OnTooltipPanelOpened(self):
        self._open = True

    def OnTooltipPanelClosed(self):
        if self.destroyed:
            return
        if not self._open:
            return
        self._open = False
        if not self._hover:
            self.unhighlight()
        if not self._expanded:
            self.minimize()

    def _open_tooltip_delayed(self, delayInSeconds):
        uthread2.Sleep(delayInSeconds)
        self._open_tooltip()

    def _open_tooltip(self):
        uicore.uilib.tooltipHandler.LoadTooltipImmediate()

    def _purchase_started(self, goal_id):
        if self.job.goal_id == goal_id:
            return

    def _on_daily_goal_completed(self, goal_id):
        if self.job.goal_id == goal_id or not can_pay_for_completion(self.job):
            self.Close()

    def _on_pay_for_completion_successful(self, goal_id):
        if self.job.goal_id == goal_id or not can_pay_for_completion(self.job):
            self.Close()
