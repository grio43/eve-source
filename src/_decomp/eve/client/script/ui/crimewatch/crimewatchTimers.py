#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\crimewatch\crimewatchTimers.py
import collections
import logging
from math import pi
import enum
import gametime
import trinity
import uthread
import uthread2
from abyss.common.constants import DEFAULT_ABYSS_CONTENT_DURATION
from carbon.common.lib.const import HOUR, SEC
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.util.color import Color
from datetimeutils import datetime_to_filetime
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.crimewatch.crimewatchConst import Colors
from eve.client.script.ui.crimewatch.crimewatchHints import TimerHint, EngagementTimerHint, BoosterTimerHint, JumpTimerHint, JumpTimerFatigueHint, EmanationLockHint
from eve.client.script.ui.shared.neocom.corporation.war.atWarIcon import AtWarCont
from eve.common.lib import appConst as const
from localization import GetByLabel
from pvpFilaments.common.constants import DEFAULT_PVP_CONTENT_DURATION
from stargate.client import get_gate_lock_messenger
from stargate.client.gateLockController import GateLockController
from uihider import UiHiderMixin
from uihighlighting import uniqueNameConst, UiHighlightDirections
from stargate.client.const import GATE_LOCK_MAX_TIMER_TIME, SETTINGS_FIRST_HIGHLIGHT_SHOWN
from voidspace.common.constants import VOID_SPACE_ENCOUNTER_LIFE_TIME
logger = logging.getLogger(__name__)
ALPHA_EMPTY = 0.2
BLINK_BEFORE_DONE_TIME = SEC * 5
TimerData = collections.namedtuple('TimerData', ['icon',
 'smallIcon',
 'color',
 'tooltip',
 'maxTimeout',
 'resetAudioEvent',
 'endingAudioEvent',
 'timerFunc',
 'hintClass',
 'callbackName',
 'timerAttributeName'])

class TimerType(enum.IntEnum):
    Weapons = 0
    Npc = 1
    Pvp = 2
    Suspect = 3
    Criminal = 4
    Engagement = 5
    Booster = 6
    JumpActivation = 7
    JumpFatigue = 8
    JumpCloak = 9
    Invulnerable = 10
    AbyssalContentExpiration = 11
    AbyssalPvpExpiration = 14
    VoidSpaceContentExpiration = 16
    Disapproval = 17
    EmanationLock = 18


CRIMEWATCH_TIMER_DATA = {TimerType.Disapproval: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_Disapproval.png', 'res:/UI/Texture/Crimewatch/Crimewatch_Disapproval_Small.png', Colors.Disapproval.GetRGBA(), 'UI/Crimewatch/Timers/DisapprovalTimerTooltip', const.disapprovalTimerTimeout, 'crimewatch_weapons_timer_play', 'crimewatch_weapons_timer_end_play', gametime.GetSimTime, None, None, 'disapprovalTimer'),
 TimerType.Weapons: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_Locked.png', 'res:/UI/Texture/Crimewatch/Crimewatch_Locked_Small.png', Colors.Red.GetRGBA(), 'UI/Crimewatch/Timers/WeaponsTimerTooltip', const.weaponsTimerTimeout, 'crimewatch_weapons_timer_play', 'crimewatch_weapons_timer_end_play', gametime.GetSimTime, None, None, 'weaponsTimer'),
 TimerType.Npc: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_Combat.png', 'res:/UI/Texture/Crimewatch/Crimewatch_Combat_Small.png', Colors.Yellow.GetRGBA(), 'UI/Crimewatch/Timers/PveTimerTooltip', const.npcTimerTimeout, 'crimewatch_log_off_timer_new_play', 'crimewatch_log_off_timer_end_play', gametime.GetSimTime, None, None, 'npcTimer'),
 TimerType.Pvp: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_Combat.png', 'res:/UI/Texture/Crimewatch/Crimewatch_Combat_Small.png', Colors.Red.GetRGBA(), 'UI/Crimewatch/Timers/PvpTimerTooltiip', const.pvpTimerTimeout, 'crimewatch_log_off_timer_new_play', 'crimewatch_log_off_timer_end_play', gametime.GetSimTime, None, None, 'pvpTimer'),
 TimerType.Suspect: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal.png', 'res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal_Small.png', Colors.Suspect.GetRGBA(), 'UI/Crimewatch/Timers/SuspectTimerTooltip', const.criminalTimerTimeout, 'crimewatch_criminal_timer_play', 'crimewatch_criminal_timer_end_play', gametime.GetSimTime, None, None, 'criminalTimer'),
 TimerType.Criminal: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal.png', 'res:/UI/Texture/Crimewatch/Crimewatch_SuspectCriminal_Small.png', Colors.Criminal.GetRGBA(), 'UI/Crimewatch/Timers/CriminalTimerTooltip', const.criminalTimerTimeout, 'crimewatch_criminal_timer_play', 'crimewatch_criminal_timer_end_play', gametime.GetSimTime, None, None, 'criminalTimer'),
 TimerType.Engagement: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_LimitedEngagement.png', None, Colors.Engagement.GetRGBA(), None, const.crimewatchEngagementDuration, 'crimewatch_engagement_timer_play', 'crimewatch_engagement_timer_end_play', gametime.GetWallclockTime, EngagementTimerHint, None, 'engagementTimer'),
 TimerType.Booster: TimerData('res:/UI/Texture/Crimewatch/booster.png', None, Colors.Boosters.GetRGBA(), None, const.crimewatchEngagementDuration, 'boostertimer_timerstart_play', 'boostertimer_timerend_play', gametime.GetWallclockTime, BoosterTimerHint, None, 'boosterTimer'),
 TimerType.JumpActivation: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_JumpActivation.png', None, (0.945,
                            0.353,
                            0.141,
                            1.0), 'UI/Crimewatch/Timers/JumpActivationTooltip', 1, 'jump_activation_timer_play', 'jump_activation_timer_end_play', gametime.GetWallclockTime, JumpTimerHint, 'DeleteWhenFinished', 'jumpActivationTimer'),
 TimerType.JumpFatigue: TimerData('res:/UI/Texture/Crimewatch/Crimewatch_JumpFatigue.png', None, (0.0,
                         1.0,
                         1.0,
                         1.0), 'UI/Crimewatch/Timers/JumpFatigueTooltip', 1, 'jump_fatigue_timer_play', 'jump_fatigue_timer_end_play', gametime.GetWallclockTime, JumpTimerFatigueHint, 'DeleteWhenFinished', 'jumpFatigueTimer'),
 TimerType.JumpCloak: TimerData('res:/UI/Texture/Crimewatch/jump_cloak.png', None, (0.0,
                       1.0,
                       1.0,
                       1.0), 'UI/Crimewatch/Timers/JumpCloakTooltip', 1, None, None, gametime.GetSimTime, None, 'DeleteWhenFinished', 'jumpCloakTimer'),
 TimerType.Invulnerable: TimerData('res:/UI/Texture/Crimewatch/invulnerable.png', None, (0.0,
                          1.0,
                          1.0,
                          1.0), 'UI/Crimewatch/Timers/InvulTooltip', 1, None, None, gametime.GetSimTime, None, 'DeleteWhenFinished', 'invulnTimer'),
 TimerType.AbyssalContentExpiration: TimerData('res:/UI/Texture/crimewatch/deadspace.png', None, Colors.Red.GetRGBA(), 'UI/Crimewatch/Timers/AbyssalContentExpiryTooltip', DEFAULT_ABYSS_CONTENT_DURATION, None, None, gametime.GetSimTime, None, 'DeleteWhenFinished', 'abyssalContentExpirationTimer'),
 TimerType.AbyssalPvpExpiration: TimerData('res:/UI/Texture/crimewatch/deadspace.png', None, (0.541,
                                  0.169,
                                  0.886,
                                  1.0), 'UI/Crimewatch/Timers/AbyssalContentExpiryTooltip', DEFAULT_PVP_CONTENT_DURATION, None, None, gametime.GetSimTime, None, 'DeleteWhenFinished', 'abyssalContentExpirationTimer'),
 TimerType.VoidSpaceContentExpiration: TimerData('res:/UI/Texture/crimewatch/deadspace.png', None, Colors.Red.GetRGBA(), 'UI/Crimewatch/Timers/voidSpaceContentExpiryTooltip', VOID_SPACE_ENCOUNTER_LIFE_TIME, None, None, gametime.GetSimTime, None, 'DeleteWhenFinished', 'voidSpaceContentExpirationTimer'),
 TimerType.EmanationLock: TimerData('res:/UI/Texture/eveicon/system_icons/link_16px.png', None, Colors.Yellow.GetRGBA(), 'UI/Crimewatch/Timers/EmanationLockTimerTooltip', GATE_LOCK_MAX_TIMER_TIME, None, None, gametime.GetWallclockTime, EmanationLockHint, 'DeleteWhenFinished', 'emanationLockTimer')}

class Timer(Container):
    default_width = 46
    default_align = uiconst.TOLEFT
    default_hintClass = TimerHint

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        timerData = CRIMEWATCH_TIMER_DATA[attributes.Get('timerType')]
        self.hintClass = timerData.hintClass or self.default_hintClass
        self.state = uiconst.UI_PICKCHILDREN
        self.timerHint = None
        self.showHint = False
        self.expiryTime = None
        self.iconBlink = None
        self.rewind = False
        self.ratio = 0.0
        self.counterText = None
        self.animationThread = None
        self.timerType = attributes.Get('timerType')
        self.timerData = attributes.get('timerData', timerData)
        self.GetTime = self.timerData.timerFunc
        self.activeAnimationCurves = None
        self.callback = attributes.get('callback', None)
        self.updateTimestamp = None
        self.customData = None
        self.content = Transform(parent=self, name='content', align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_NORMAL)
        self.content.OnMouseEnter = self.OnMouseEnter
        self.iconTransform = Transform(parent=self.content, name='iconTransform', align=uiconst.CENTER, width=16, height=16, state=uiconst.UI_DISABLED)
        self.icon = Sprite(name='icon', parent=self.iconTransform, pos=(0, 0, 16, 16), texturePath=self.timerData.icon, color=self.timerData.color, state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        self.gaugeCircular = GaugeCircular(parent=self.content, radius=16, align=uiconst.CENTER, colorStart=self.timerData.color, colorEnd=self.timerData.color, colorBg=self._GetGaugeBgColor(self.timerData.color), lineWidth=2.5, clockwise=False, showMarker=False, state=uiconst.UI_DISABLED)
        self.pointerContainer = Transform(name='pointer_container', parent=self.content, width=32, height=32, idx=0)
        self.pointerClipper = Container(parent=self.pointerContainer, pos=(9, -10, 15, 13), clipChildren=True, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.pointerSprite = Sprite(name='cycle_pointer', parent=self.pointerClipper, pos=(0, 0, 15, 19), texturePath='res:/UI/Texture/Crimewatch/Crimewatch_TimerPoint_WithShadow.png', color=self.timerData.color, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.iconTransform.scalingCenter = (0.5, 0.5)
        uicore.animations.Tr2DScaleTo(self.iconTransform, startScale=(0.8, 0.8), endScale=(1.0, 1.0), duration=0.75, curveType=uiconst.ANIM_OVERSHOT)

    def _GetGaugeBgColor(self, color):
        return Color(*color).SetAlpha(ALPHA_EMPTY).GetRGBA()

    def SetTimerType(self, timerType):
        self.timerData = CRIMEWATCH_TIMER_DATA[timerType]
        r, g, b, a = self.timerData.color
        self.icon.SetRGBA(r, g, b, a)
        self.pointerSprite.SetRGBA(r, g, b, a)
        self.gaugeCircular.SetColor(self.timerData.color, self.timerData.color)
        self.gaugeCircular.SetColorBg(self._GetGaugeBgColor(self.timerData.color))
        self.timerType = timerType

    def SetRatio(self, ratio):
        self.ratio = min(1.0, max(0.0, ratio))
        rotation = min(pi * 2, 2 * pi * self.ratio)
        self.pointerContainer.rotation = rotation
        self.gaugeCircular.SetValue(ratio, animate=False)

    def SetExpiryTime(self, expiryTime, doAlert, maxDuration = None, updateTimestamp = None):
        logger.debug('Setting timer %s expiry time to %s', self.name, expiryTime)
        self.Reset(expiryTime, doAlert, maxDuration=maxDuration)
        self.expiryTime = expiryTime
        self.updateTimestamp = updateTimestamp
        if expiryTime is None:
            self.PlayActiveAnimation()
        else:
            self.animationThread = uthread.new(self.Animate_Thread)

    def Reset(self, resetTo, doAlert, maxDuration = None):
        if self.animationThread is not None:
            self.animationThread.kill()
        if maxDuration and maxDuration != self.timerData.maxTimeout:
            self.timerData = self.timerData._replace(maxTimeout=maxDuration)
        uthread.new(self.Rewind_Thread, resetTo, doAlert)

    def Rewind_Thread(self, resetTo, doAlert):
        if self.rewind:
            return
        if doAlert and self.timerData.resetAudioEvent is not None:
            sm.GetService('audio').SendUIEvent(self.timerData.resetAudioEvent)
        self.rewind = True
        ratio = self.ratio
        startTime = self.GetTime()
        distance = 1 - ratio
        cycleSpeed = float(distance * 500)
        while not self.destroyed and self.ratio < (self.GetRatio(resetTo - self.GetTime()) if resetTo is not None else 1.0):
            elapsedTime = gametime.GetTimeDiffInMs(startTime, self.GetTime())
            toAdd = elapsedTime / cycleSpeed
            self.SetRatio(ratio + toAdd)
            uthread2.sleep(0.025)

        self.rewind = False

    def FlipFlop(self, sprite, duration = 1.0, startValue = 0.0, endValue = 1.0, loops = 5):
        curve = trinity.Tr2CurveScalar()
        curve.AddKey(0, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.01 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.5 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.51 * duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        return uicore.animations.Play(curve, sprite, 'opacity', loops, None, False)

    def GetRatio(self, timeLeft):
        ratio = timeLeft / float(self.timerData.maxTimeout)
        ratio = min(1.0, max(0.0, ratio))
        return ratio

    def Animate_Thread(self):
        self.StopActiveAnimation()
        while not self.destroyed and self.expiryTime is not None:
            if not self.rewind:
                if self.ratio <= 0.0:
                    break
                timeLeft = self.expiryTime - self.GetTime()
                ratio = self.GetRatio(timeLeft)
                self.SetRatio(ratio)
                if timeLeft < BLINK_BEFORE_DONE_TIME:
                    self.PlayIconBlink()
                else:
                    self.StopIconBlink()
            uthread2.sleep(0.05)

        if self.callback:
            self.callback(self)

    def PlayIconBlink(self):
        if self.iconBlink is None:
            self.iconBlink = self.FlipFlop(self.icon, startValue=1.0, endValue=0.0)
            if self.timerData.endingAudioEvent:
                sm.GetService('audio').SendUIEvent(self.timerData.endingAudioEvent)

    def StopIconBlink(self):
        if self.iconBlink is not None:
            self.iconBlink.Stop()
            self.iconBlink = None
            self.icon.opacity = 1.0

    def EndAnimation(self):
        self.SetRatio(0.0)
        uicore.animations.MoveOutBottom(self.pointerSprite, amount=9, duration=0.3, sleep=False)
        self.content.scalingCenter = (0.5, 0.5)
        uicore.animations.Tr2DScaleTo(self.content, startScale=(1.0, 1.0), endScale=(0.8, 0.8), duration=0.4, sleep=True)

    def OnMouseEnter(self, *args):
        uthread.new(self.ShowHide)

    def ShowHide(self):
        uthread2.sleep(0.25)
        if uicore.uilib.mouseOver is self.content:
            self.showHint = True
            if self.timerHint is None:
                left, top, width, height = self.content.GetAbsolute()
                self.timerHint = self.hintClass(parent=uicore.layer.abovemain, left=left + 16, top=top + 16, timerData=self.timerData, parentTimer=self)

    def ShiftLeft(self):
        uicore.animations.MoveInFromRight(self, self.width, duration=0.5)

    def SetCounter(self, count):
        if count is None or count <= 1:
            if self.counterText is not None:
                self.counterText.Close()
                self.counterText = None
        else:
            if self.counterText is None:
                self.counterText = eveLabel.EveHeaderLarge(parent=self.content, name='counter', left=34, top=-2, bold=True, color=self.timerData.color)
            text = str(count) if count < 10 else '9+'
            self.counterText.text = text

    def PlayActiveAnimation(self):
        self.activeAnimationCurves = ((self.pointerSprite, self.FlipFlop(self.pointerSprite, startValue=1.0, endValue=0.75, duration=1.0, loops=uiconst.ANIM_REPEAT)), (self.gaugeCircular, self.FlipFlop(self.gaugeCircular, startValue=1.0, endValue=0.75, duration=1.0, loops=uiconst.ANIM_REPEAT)))

    def StopActiveAnimation(self):
        if self.activeAnimationCurves is not None:
            for sprite, animCurve in self.activeAnimationCurves:
                animCurve.Stop()
                sprite.opacity = 1.0

            self.activeAnimationCurves = None


class TimerContainer(UiHiderMixin, Container):
    __notifyevents__ = ['OnWeaponsTimerUpdate',
     'OnPvpTimerUpdate',
     'OnCriminalTimerUpdate',
     'OnNpcTimerUpdate',
     'OnCombatTimersUpdated',
     'OnCrimewatchEngagementUpdated',
     'OnBoosterUpdated',
     'OnDisapprovalTimerUpdate',
     'OnJumpTimersUpdated',
     'OnJumpCloakUpdated',
     'OnJumpCloakCancelled',
     'OnRestoringInvulnUpdated',
     'OnInvulunOnUndockingUpdated',
     'OnInvulnCancelled',
     'OnAbyssalContentFinished',
     'OnVoidSpaceContentFinished',
     'OnWarStatusUpdated',
     'OnEmanationLockUpdated']
    default_name = 'unique_UI_crimewatchTimers'
    uniqueUiName = uniqueNameConst.UNIQUE_NAME_CRIMEWATCH_TIMERS
    default_height = 32
    default_width = 96 + 16
    default_padBottom = 6
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(TimerContainer, self).ApplyAttributes(attributes)
        self.warCont = AtWarCont(parent=self, align=uiconst.TOLEFT)
        sm.RegisterNotify(self)
        self.uiCriticalSectionsByTimerType = {}
        for timerType, timerData in CRIMEWATCH_TIMER_DATA.iteritems():
            setattr(self, timerData.timerAttributeName, None)
            if timerType not in self.uiCriticalSectionsByTimerType:
                criticalSection = uthread.CriticalSection('uiTimerCriticalSection:%s' % timerData.timerAttributeName)
                self.uiCriticalSectionsByTimerType[timerType] = criticalSection

        self.crimewatchSvc = sm.GetService('crimewatchSvc')
        self.warSvc = sm.GetService('war')
        uthread.new(self.OnCombatTimersUpdated)

    def Release(self):
        sm.UnregisterNotify(self)
        for timerData in CRIMEWATCH_TIMER_DATA.itervalues():
            timer = getattr(self, timerData.timerAttributeName, None)
            if timer is not None and timer.animationThread is not None:
                timer.animationThread.kill()

    def OnCombatTimersUpdated(self):
        self.OnWeaponsTimerUpdate(doAlert=False, *self.crimewatchSvc.GetWeaponsTimer())
        self.OnNpcTimerUpdate(doAlert=False, *self.crimewatchSvc.GetNpcTimer())
        self.OnPvpTimerUpdate(doAlert=False, *self.crimewatchSvc.GetPvpTimer())
        self.OnCriminalTimerUpdate(doAlert=False, *self.crimewatchSvc.GetCriminalTimer())
        self.OnDisapprovalTimerUpdate(doAlert=False, *self.crimewatchSvc.GetDisapprovalTimer())
        self.OnCrimewatchEngagementUpdated(None, None, doAlert=False)
        self.OnBoosterUpdated()
        self.OnJumpTimersUpdated(doAlert=False, *self.crimewatchSvc.GetJumpTimers())
        self.OnWarStatusUpdated(self.warSvc.IsPlayerCurrentlyAtWarOrInFW(), doAlert=False)
        uthread2.start_tasklet(self._UpdateEmanationLock)

    def OnWeaponsTimerUpdate(self, state, expiryTime, doAlert = True):
        with self.uiCriticalSectionsByTimerType[TimerType.Weapons]:
            if state in (const.weaponsTimerStateActive, const.weaponsTimerStateInherited):
                timer = self.GetTimer(TimerType.Weapons)
                timer.SetExpiryTime(None, doAlert)
            elif expiryTime is not None:
                timer = self.GetTimer(TimerType.Weapons)
                timer.SetExpiryTime(expiryTime, doAlert)
            else:
                self.DeleteTimer(TimerType.Weapons)

    def OnNpcTimerUpdate(self, state, expiryTime, doAlert = True):
        with self.uiCriticalSectionsByTimerType[TimerType.Npc]:
            if state in (const.npcTimerStateActive, const.npcTimerStateInherited):
                timer = self.GetTimer(TimerType.Npc)
                timer.SetExpiryTime(None, doAlert)
            elif expiryTime is not None:
                timer = self.GetTimer(TimerType.Npc)
                timer.SetExpiryTime(expiryTime, doAlert)
            else:
                self.DeleteTimer(TimerType.Npc)

    def OnPvpTimerUpdate(self, state, expiryTime, doAlert = True):
        with self.uiCriticalSectionsByTimerType[TimerType.Pvp]:
            if state in (const.pvpTimerStateActive, const.pvpTimerStateInherited):
                timer = self.GetTimer(TimerType.Pvp)
                timer.SetExpiryTime(None, doAlert)
            elif expiryTime is not None:
                timer = self.GetTimer(TimerType.Pvp)
                timer.SetExpiryTime(expiryTime, doAlert)
            else:
                self.DeleteTimer(TimerType.Pvp)

    def OnDisapprovalTimerUpdate(self, state, expiryTime, doAlert = True):
        with self.uiCriticalSectionsByTimerType[TimerType.Disapproval]:
            if state in (const.disapprovalTimerStateActive, const.disapprovalTimerStateInherited):
                timer = self.GetTimer(TimerType.Disapproval)
                timer.SetExpiryTime(None, doAlert)
            elif state == const.disapprovalTimerStateTimer and expiryTime is not None:
                timer = self.GetTimer(TimerType.Disapproval)
                timer.SetExpiryTime(expiryTime, doAlert)
            else:
                self.DeleteTimer(TimerType.Disapproval)

    def OnCriminalTimerUpdate(self, state, expiryTime, doAlert = True):
        with self.uiCriticalSectionsByTimerType[TimerType.Suspect]:
            if state in (const.criminalTimerStateActiveSuspect, const.criminalTimerStateInheritedSuspect):
                timer = self.GetTimer(TimerType.Suspect)
                timer.SetExpiryTime(None, doAlert)
            elif state == const.criminalTimerStateTimerSuspect and expiryTime is not None:
                timer = self.GetTimer(TimerType.Suspect)
                timer.SetExpiryTime(expiryTime, doAlert)
            elif state in (const.criminalTimerStateActiveCriminal, const.criminalTimerStateInheritedCriminal):
                timer = self.GetTimer(TimerType.Criminal)
                timer.SetExpiryTime(None, doAlert)
            elif state == const.criminalTimerStateTimerCriminal and expiryTime is not None:
                timer = self.GetTimer(TimerType.Criminal)
                timer.SetExpiryTime(expiryTime, doAlert)
            else:
                self.DeleteTimer(TimerType.Suspect)

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout, doAlert = True):
        engagements = self.crimewatchSvc.GetMyEngagements()
        if len(engagements) == 0:
            self.DeleteTimer(TimerType.Engagement)
        else:
            timer = self.GetTimer(TimerType.Engagement)
            onGoingEngagement = any((_timeout == const.crimewatchEngagementTimeoutOngoing for _timeout in engagements.itervalues()))
            if onGoingEngagement:
                timeout = None
            else:
                timeout = max((_timeout for _timeout in engagements.itervalues()))
            timer.SetExpiryTime(timeout, doAlert)
            timer.SetCounter(len(engagements))

    def OnBoosterUpdated(self, doAlert = True):
        boosters = self.crimewatchSvc.GetMyBoosters()
        boosterList = [ b for b in boosters if b.boosterDuration ]
        if len(boosterList) == 0:
            self.DeleteTimer(TimerType.Booster)
        else:
            timer = self.GetTimer(TimerType.Booster)
            boosterList.sort(key=lambda x: x.expiryTime, reverse=True)
            longestLastingBooster = boosterList[0]
            timeout = longestLastingBooster.expiryTime
            maxDuration = longestLastingBooster.boosterDuration
            timer.SetExpiryTime(timeout, doAlert, maxDuration * 10000)
            timer.SetCounter(len(boosterList))

    def OnJumpTimersUpdated(self, jumpActivation, jumpFatigue, lastUpdated, doAlert = False):
        if jumpFatigue and jumpFatigue > gametime.GetWallclockTime():
            timer = self.GetTimer(TimerType.JumpFatigue)
            timer.SetExpiryTime(jumpFatigue, doAlert, jumpFatigue - lastUpdated)
        else:
            self.DeleteTimer(TimerType.JumpFatigue)
        if jumpActivation and jumpActivation > gametime.GetWallclockTime():
            self.GetTimer(TimerType.JumpActivation).SetExpiryTime(jumpActivation, doAlert, jumpActivation - lastUpdated)
        else:
            self.DeleteTimer(TimerType.JumpActivation)

    def OnWarStatusUpdated(self, atWar, doAlert = True):
        self.warCont.ShowIcon(animate=doAlert) if atWar else self.warCont.HideIcon(animate=doAlert)

    def OnJumpCloakUpdated(self, shipID, endTime, duration):
        self.GetTimer(TimerType.JumpCloak).SetExpiryTime(endTime, maxDuration=duration, doAlert=True)

    def OnJumpCloakCancelled(self, shipID):
        self.DeleteTimer(TimerType.JumpCloak)

    def OnRestoringInvulnUpdated(self, shipID, endTime, duration):
        self._SetInvulnTimerExpiryTime(endTime, duration)

    def OnInvulunOnUndockingUpdated(self, shipID, endTime, duration):
        self._SetInvulnTimerExpiryTime(endTime, duration)

    def _SetInvulnTimerExpiryTime(self, endTime, duration):
        with self.uiCriticalSectionsByTimerType[TimerType.Invulnerable]:
            timer = self.GetTimer(TimerType.Invulnerable)
            timer.SetExpiryTime(endTime, maxDuration=duration, doAlert=True)

    def OnInvulnCancelled(self, shipID):
        with self.uiCriticalSectionsByTimerType[TimerType.Invulnerable]:
            self.DeleteTimer(TimerType.Invulnerable)

    def SetAbyssalTimer(self, endTime):
        self.SetTimerContentExpiry(TimerType.AbyssalContentExpiration, endTime)

    def SetAbyssalPvpTimer(self, endTime):
        self.SetTimerContentExpiry(TimerType.AbyssalPvpExpiration, endTime)

    def SetVoidSpaceTimer(self, endTime):
        self.SetTimerContentExpiry(TimerType.VoidSpaceContentExpiration, endTime)

    def SetTimerContentExpiry(self, timerType, endTime):
        with self.uiCriticalSectionsByTimerType[timerType]:
            timer = self.GetTimer(timerType)
            timer.SetExpiryTime(endTime, False)

    def OnAbyssalContentFinished(self, content_id, timer_type):
        if not sm.GetService('abyss').is_active_content(content_id):
            return
        with self.uiCriticalSectionsByTimerType[timer_type]:
            self.DeleteTimer(timer_type)

    def OnVoidSpaceContentFinished(self, content_id, timer_type):
        if not sm.GetService('voidSpaceSvc').is_content_active(content_id):
            return
        with self.uiCriticalSectionsByTimerType[timer_type]:
            self.DeleteTimer(timer_type)

    def OnEmanationLockUpdated(self, lock_details):
        if lock_details is None or lock_details.expiry_time < gametime.now():
            with self.uiCriticalSectionsByTimerType[TimerType.EmanationLock]:
                self.DeleteTimer(TimerType.EmanationLock)
                return
        with self.uiCriticalSectionsByTimerType[TimerType.EmanationLock]:
            timer = self.GetTimer(TimerType.EmanationLock)
            timer.SetExpiryTime(datetime_to_filetime(lock_details.expiry_time), doAlert=True)
        hasShownHighlight = settings.char.ui.Get(SETTINGS_FIRST_HIGHLIGHT_SHOWN, False)
        if hasShownHighlight:
            return
        settings.char.ui.Set(SETTINGS_FIRST_HIGHLIGHT_SHOWN, True)
        sm.GetService('uiHighlightingService').highlight_ui_element_by_name(ui_element_name=timer.name, message=GetByLabel('UI/Crimewatch/Timers/EmanationLockHighlight'), default_direction=UiHighlightDirections.RIGHT, offset=-10, fadeout_seconds=10)

    def _UpdateEmanationLock(self):
        messenger = get_gate_lock_messenger(sm.GetService('publicGatewaySvc'))
        lock_details = GateLockController.get_instance(messenger).get_current_system_lock()
        self.OnEmanationLockUpdated(lock_details)

    def DeleteTimer(self, timerType):
        idx = None
        timerName = CRIMEWATCH_TIMER_DATA[timerType].timerAttributeName
        timer = getattr(self, timerName, None)
        if timer is not None:
            if timer in self.children:
                idx = self.children.index(timer)
            timer.EndAnimation()
            timer.Close()
            setattr(self, timerName, None)
            logger.debug('Closed Timer %s', timerName)
        if idx is not None:
            for timer in self.children[idx:idx + 1]:
                timer.ShiftLeft()

    def DeleteWhenFinished(self, timer):
        with self.uiCriticalSectionsByTimerType[timer.timerType]:
            self.DeleteTimer(timer.timerType)

    def GetTimer(self, timerType):
        timerData = CRIMEWATCH_TIMER_DATA[timerType]
        timerAttributeName = timerData.timerAttributeName
        timer = getattr(self, timerAttributeName)
        if timer is None:
            timer = Timer(parent=self, name=timerAttributeName, timerType=timerType, callback=getattr(self, timerData.callbackName) if timerData.callbackName else None)
            setattr(self, timerAttributeName, timer)
            logger.debug('Created Timer %s', timerAttributeName)
        if timer.timerType != timerType:
            timer.SetTimerType(timerType)
        return timer

    def GetExistingTimer(self, timerType):
        timerName = CRIMEWATCH_TIMER_DATA[timerType].timerAttributeName
        return getattr(self, timerName, None)
