#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\skyhookTheftUI\infoPanelSkyhookTheftTimerContainer.py
import localization
import locks
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from dynamicresources.client.ui.ess_info_panel_ui_const import TRANSITION_LOCK
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
import eveicon
from gametime import GetSimTime
from localization.formatters import FormatTimeIntervalShort
import uthread2
import trinity
import mathext
import logging
log = logging.getLogger(__name__)
LINK_STARTED = 1
LINK_FAILED = 2
LINK_SUCCESS = 3

class InfoPanelSkyhookTheftTimerContainer(ContainerAutoSize):
    default_name = 'skyhookLinkingCont'
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP

    def __init__(self, startTime = None, endTime = None, planetName = None, service = None, *args, **kwargs):
        super(InfoPanelSkyhookTheftTimerContainer, self).__init__(*args, **kwargs)
        self.completeLinkAtTime = endTime
        self.statedLinkAtTime = startTime
        self.planetName = planetName
        self._skyhookLinkingTimer = None
        self.skyhookSiloTheftProgressBar = None
        self.collapsedStateCont = None
        self.currentState = LINK_STARTED
        self.ConstructUncollapsedState(True)

    def ConstructUncollapsedState(self, animateChange):
        with locks.TempLock(TRANSITION_LOCK):
            gaugeStates = {'skyhookLinkingTimerStartValue': None}
            if self.skyhookSiloTheftProgressBar:
                gaugeStates['skyhookLinkingTimerStartValue'] = self.skyhookSiloTheftProgressBar.value
            if self._skyhookLinkingTimer:
                self._skyhookLinkingTimer.Kill()
                self._skyhookLinkingTimer = None
            self.ConstructSkyhookLinkingState(gaugeStates, animateChange)

    def ConstructSkyhookLinkingState(self, gaugeStates, animate):
        self.skyhookLinkingTimerCont = Container(name='timerCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, height=46, state=uiconst.UI_DISABLED)
        startingOpacity = 0 if animate else 1
        self.skyhookSiloTheftProgressBar = GaugeCircular(parent=self.skyhookLinkingTimerCont, color=eveColor.FOCUS_BLUE, align=uiconst.TOLEFT, showMarker=True, lineWidth=2, radius=18, colorStart=eveColor.FOCUS_BLUE, colorEnd=eveColor.FOCUS_BLUE, colorBg=Color(*eveColor.WHITE).SetAlpha(0.2).GetRGBA(), opacity=startingOpacity)
        self.hourglassSymbolTransform = Transform(parent=self.skyhookLinkingTimerCont, align=uiconst.TOPLEFT, width=36, height=36)
        self.hourglassSymbolSprite = Sprite(parent=self.hourglassSymbolTransform, align=uiconst.CENTER, texturePath=eveicon.hourglass, color=eveColor.WHITE, width=16, height=16)
        self.hourglassSymbolSprite.scalingCenter = (0.5, 0.5)
        self.skyhookLinkingTimerTextCont = ContainerAutoSize(name='timerTextCont', parent=self.skyhookLinkingTimerCont, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT, padLeft=15, opacity=startingOpacity)
        self.descriptionLabel = EveLabelLarge(parent=self.skyhookLinkingTimerTextCont, text=localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftLootDrops', planetName=self.planetName), align=uiconst.TOPLEFT, top=-3)
        current = self.statedLinkAtTime
        maxVal = self.completeLinkAtTime
        countdown = max(0, maxVal - current)
        self.skyhookLinkingCountdownLabel = EveCaptionLarge(parent=self.skyhookLinkingTimerTextCont, text=FormatTimeIntervalShort(countdown, showFrom='hour', showTo='second'), align=uiconst.BOTTOMLEFT, bold=False, top=3, color=eveColor.FOCUS_BLUE)
        self.skyhookLinkingSuccessLabel = EveCaptionLarge(parent=self.skyhookLinkingTimerTextCont, text=localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftSuccessful'), align=uiconst.BOTTOMLEFT, bold=False, top=3, color=eveColor.SUCCESS_GREEN, opacity=0)
        self.skyhookLinkingFailedLabel = EveCaptionLarge(parent=self.skyhookLinkingTimerTextCont, text=localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftFailed'), align=uiconst.BOTTOMLEFT, bold=False, top=3, color=eveColor.DANGER_RED, opacity=0)
        if not animate and gaugeStates['skyhookLinkingTimerStartValue']:
            self.skyhookSiloTheftProgressBar.SetValue(gaugeStates['skyhookLinkingTimerStartValue'], animate=False)

        def animate_in():
            with locks.TempLock(TRANSITION_LOCK):
                animations.FadeIn(self.skyhookSiloTheftProgressBar, duration=0.25)
                animations.FadeIn(self.skyhookLinkingTimerTextCont, duration=0.25)
                animations.MoveInFromRight(self.skyhookLinkingTimerTextCont, amount=10, duration=0.25, sleep=True)

        if animate:
            uthread2.StartTasklet(animate_in)
        self._skyhookLinkingTimer = uthread2.StartTasklet(self.UpdateLinkingTimer, self.skyhookLinkingCountdownLabel, self.skyhookSiloTheftProgressBar)

    def UpdateLinkingTimer(self, label, gauge, animate = True):
        while self._skyhookLinkingTimer:
            current = GetSimTime()
            timeLeft = long(max(0, self.completeLinkAtTime - current))
            proportion = 1.0 - float(current - self.statedLinkAtTime) / float(self.completeLinkAtTime - self.statedLinkAtTime)
            proportion = mathext.clamp(proportion, 0.0, 1.0)
            gauge.SetValue(proportion, animate=animate)
            if timeLeft > 0:
                label.SetText(FormatTimeIntervalShort(timeLeft, showFrom='hour', showTo='second'))
                uthread2.Sleep(1)
            else:
                label.SetText(FormatTimeIntervalShort(0, showFrom='hour', showTo='second'))
                self._skyhookLinkingTimer = None

    def LinkFailed(self):
        self.StopTimers()
        self.TransitionState(LINK_FAILED)

    def LinkSuccess(self):
        self.StopTimers()
        self.TransitionState(LINK_SUCCESS)

    def StopTimers(self):
        if self._skyhookLinkingTimer:
            self._skyhookLinkingTimer.Kill()
            self._skyhookLinkingTimer = None

    def TransitionState(self, newState = None):
        with locks.TempLock('TransitionState'):
            self.currentState = newState
            if self.currentState == LINK_SUCCESS:
                descText = localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftLootDropped', planetName=self.planetName)
                self.AnimateState(descText, self.skyhookLinkingSuccessLabel)
            elif self.currentState == LINK_FAILED:
                self.iconBlink = self.FlipFlop(self.hourglassSymbolSprite, startValue=1.0, endValue=0.0)
                descText = localization.GetByLabel('UI/OrbitalSkyhook/SkyhookInfoPanel/SkyhookTheftLinkBroke', planetName=self.planetName)
                self.AnimateState(descText, self.skyhookLinkingFailedLabel)
                self.skyhookSiloTheftProgressBar.SetColorMarker(eveColor.DANGER_RED)
                self.skyhookSiloTheftProgressBar.SetColor(eveColor.DANGER_RED, eveColor.DANGER_RED)
                self.gaugeBlink = self.FlipFlop(self.skyhookSiloTheftProgressBar.gauge, startValue=1.0, endValue=0.0)
            animations.FadeOut(self.hourglassSymbolTransform, duration=0.25, timeOffset=2)
            animations.FadeOut(self.skyhookSiloTheftProgressBar, duration=0.25, timeOffset=2)
            animations.FadeOut(self.skyhookLinkingTimerTextCont, duration=0.25, timeOffset=2)
            animations.MoveOutRight(self.skyhookLinkingTimerTextCont, amount=10, duration=0.25, sleep=True, timeOffset=2)
        self.Close()

    def AnimateState(self, descText, label):
        self.descriptionLabel.text = descText
        animations.FadeOut(self.skyhookLinkingCountdownLabel, duration=0.25, timeOffset=0)
        animations.FadeIn(label, duration=0.25, timeOffset=0)

    def FlipFlop(self, sprite, duration = 1.0, startValue = 0.0, endValue = 1.0, loops = 5):
        curve = trinity.Tr2CurveScalar()
        curve.AddKey(0, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.01 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.5 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(0.51 * duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        curve.AddKey(duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        return animations.Play(curve, sprite, 'opacity', loops, None, False)
