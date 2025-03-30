#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\milestoneTimer\milestoneTimer.py
import gametime
import math
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.shared.infoPanels.milestoneTimer.tooltip import MilestoneTooltip, MilestoneRewardTooltip
from milestones.common.constants import MILESTONE_REWARD_NUMBER_OF_MINUTES

class MilestoneTimer(Transform):
    default_name = 'MilestoneTimer'
    default_align = uiconst.TOPLEFT
    default_width = 32
    default_height = 32
    default_state = uiconst.UI_NORMAL
    default_scalingCenter = (0.5, 0.5)
    gauge_alpha = 0.2
    update_interval_ms = 1000
    animate_interval_ms = 2000
    default_color = Color.HextoRGBA('#31C4A1')
    default_animation_loop_sound = 'isk_animation_loop_play'
    default_animation_loop_stop = 'isk_animation_loop_stop'
    default_claim_sound = 'isk_animation_claim_play'
    __notifyevents__ = ['OnLoginMilestoneAchieved', 'OnAirNpeStateChanged']

    def ApplyAttributes(self, attributes):
        super(MilestoneTimer, self).ApplyAttributes(attributes)
        self.iconPath = attributes.get('iconPath', '')
        self.iconColor = attributes.get('iconColor', self.default_color)
        self.gaugeColorStart = attributes.get('gaugeColorStart', self.default_color)
        self.gaugeColorEnd = attributes.get('gaugeColorEnd', self.default_color)
        self.milestoneID = attributes.get('milestoneID', None)
        self.animation_loop_sound = attributes.get('animationSoundStart', self.default_animation_loop_sound)
        self.animation_loop_stop = attributes.get('animationSoundStop', self.default_animation_loop_stop)
        self.claim_reward_sound = attributes.get('claimRewardSound', self.default_claim_sound)
        self.updateThread = None
        self.animateThread = None
        self.ConstructLayout()
        timeLeft = attributes.get('timeLeft', gametime.MIN)
        self.secondsLeft = gametime.GetSecondsUntilWallclockTime(timeLeft)
        totalTime = attributes.get('totalTime', gametime.MIN)
        self.totalSeconds = gametime.GetSecondsUntilWallclockTime(gametime.GetWallclockTime() + totalTime)
        self.updateThread = AutoTimer(interval=self.update_interval_ms, method=self._UpdateGauge)
        self.tooltipPanelClassInfo = MilestoneTooltip(self.milestoneID, self.totalSeconds, self.GetSecondsPassed)
        sm.RegisterNotify(self)

    def Close(self):
        PlaySound(self.animation_loop_stop)
        self.updateThread = None
        self.animateThread = None
        super(MilestoneTimer, self).Close()

    def ConstructLayout(self):
        self.icon = Sprite(parent=self, align=uiconst.CENTER, width=16, height=16, color=self.iconColor, state=uiconst.UI_DISABLED, texturePath=self.iconPath)
        self.gauge = GaugeCircular(parent=self, radius=16, align=uiconst.CENTER, colorStart=self.gaugeColorStart, colorEnd=self.gaugeColorEnd, colorBg=Color(*self.iconColor).SetAlpha(self.gauge_alpha).GetRGBA(), lineWidth=2.5, clockwise=False, showMarker=False, state=uiconst.UI_DISABLED)

    def _UpdateGauge(self):
        self.secondsLeft -= 1
        ratio = self.GetSecondsPassed() / float(self.totalSeconds)
        ratio = min(1.0, max(0.0, ratio))
        self.gauge.SetValue(ratio)

    def GetSecondsPassed(self):
        return self.totalSeconds - self.secondsLeft

    def OnLoginMilestoneAchieved(self, milestoneID, iskAmount):
        self.updateThread.KillTimer()
        shouldStartAnimating = self.display
        if shouldStartAnimating:
            self.StartAnimateLoop()
        self.tooltipPanelClassInfo = MilestoneRewardTooltip(milestoneID, iskAmount, lambda x: self._ClaimRewards(milestoneID), MILESTONE_REWARD_NUMBER_OF_MINUTES)

    def StartAnimateLoop(self):
        PlaySound(self.animation_loop_sound)
        self.AnimateNotification()
        self.animateThread = AutoTimer(interval=self.animate_interval_ms, method=self.AnimateNotification)

    def _ClaimRewards(self, milestoneID):
        PlaySound(self.claim_reward_sound)
        sm.GetService('milestoneSvc').ClaimRewards(milestoneID)
        self.Close()

    def AnimateNotification(self):
        animations.Tr2DRotateTo(self.icon, duration=0.75, endAngle=2 * math.pi)
        animations.Tr2DScaleTo(self, startScale=(1.0, 1.0), endScale=(1.2, 1.2), curveType=uiconst.ANIM_WAVE, timeOffset=0.75)
