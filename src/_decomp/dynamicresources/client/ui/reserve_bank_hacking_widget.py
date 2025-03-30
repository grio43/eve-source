#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ui\reserve_bank_hacking_widget.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from dynamicresources.client.ui import RadialBarGraph
from dynamicresources.client.ui.alert_animations import TimerDissapearAnimation, TimerAppearAnimation
from dynamicresources.client.ui.ess_info_panel_ui_const import TRANSITION_LOCK, RESERVE_BANK_AUTOPAYOUT_BAR_COLOR
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eveui import Sprite

class ReserveBankHackingWidget(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    default_radius = 50
    default_padTop = 13
    default_barHeight = 10
    default_hoverBarHeight = 20
    default_linked = 0
    default_animateIn = True

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.radius = attributes.get('radius', self.default_radius)
        self.initialProgress = attributes.get('progress', 1.0)
        self.barHeight = attributes.get('barHeight', self.default_barHeight)
        self.hoverBarHeight = attributes.get('hoverBarHeight', self.default_hoverBarHeight)
        self.paymentValues = attributes.paymentValues
        self.OnMouseEnterCallback = attributes.get('onMouseEnterCallback', lambda _: None)
        self.OnMouseExitCallback = attributes.get('onMouseExitCallback', lambda _: None)
        self.nextPaymentTimerBlinkingOut = False
        self.innerRadius = self.radius - self.barHeight
        self.linked = attributes.get('linked', self.default_linked)
        self.animateIn = attributes.get('animateIn', self.default_animateIn)
        self.pulsesTotal = attributes.pulsesTotal
        self.hoverStateActive = False
        if self.animateIn:
            self.AnimateIn()
        self.ConstructLayout()

    def AnimateOut(self):
        TimerDissapearAnimation(parent=self, width=self.radius * 2, height=self.radius * 2, endRadius=self.radius, gaugeLineWidth=5, startAngle=-math.pi / 2, align=uiconst.TOPLEFT, left=3, top=3, includeDashedBackground=False, transitionLock=TRANSITION_LOCK, idx=0)
        animations.FadeOut(self.gaugeCont, duration=0.25, sleep=True)

    def AnimateIn(self):
        self.animatedGaugeBackground = TimerAppearAnimation(parent=self, width=self.radius * 2, height=self.radius * 2, endRadius=self.radius, gaugeLineWidth=5, startAngle=-math.pi / 2, align=uiconst.TOPLEFT, dashSizeFactor=8.0, timerColor=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), left=3, top=3, includeDashedBackground=False, transitionLock=TRANSITION_LOCK)

    def BlinkInNextPaymentTimer(self):
        if not self.hoverStateActive:
            animations.BlinkIn(self.nextPayoutTimer, duration=0.2)

    def BlinkOutNextPaymentTimer(self):
        if not self.nextPaymentTimerBlinkingOut and not self.hoverStateActive:

            def reset_blink_flag():
                self.nextPaymentTimerBlinkingOut = False

            animations.BlinkOut(self.nextPayoutTimer, duration=0.2, callback=reset_blink_flag, loops=6)
            self.nextPaymentTimerBlinkingOut = True

    def _GetPrefferedBarGapRatio(self, nSegments):
        if nSegments <= 15:
            return 7
        elif nSegments >= 45:
            return 2.5
        else:
            return 4

    def ConstructLayout(self):
        startingOpacity = 0.0 if self.animateIn else 1.0
        self.gaugeCont = Container(parent=self, width=self.radius * 2 + self.hoverBarHeight / 2, height=self.radius * 2 + self.hoverBarHeight / 2, align=uiconst.TOPLEFT, opacity=startingOpacity)
        self.nextPayoutTimer = GaugeCircular(parent=self.gaugeCont, color=Color.WHITE, align=uiconst.CENTER, colorStart=Color.WHITE, colorEnd=Color.WHITE, showMarker=False, lineWidth=2.0, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), radius=self.radius + 6, state=uiconst.UI_DISABLED)
        self.paymentValues.reverse()
        barGapRatio = self._GetPrefferedBarGapRatio(len(self.paymentValues))
        self.reserveBankHackingGauge = ReserveBankHackingGauge(self.gaugeCont, uiconst.CENTER, self.paymentValues, radius=self.radius, inner_radius=self.innerRadius, start_angle=0.0, end_angle=360.0, progress=self.initialProgress, color=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR, background_color=(1.0, 1.0, 1.0, 0.3), bar_gap_ratio=barGapRatio, value_radius_modifier=0.0)
        self.pointingArrowRotationTransform = Transform(parent=self.gaugeCont, name='pointingArrowTransform', align=uiconst.CENTER, width=65, height=65, rotation=math.pi, opacity=0)
        self.pointingArrowTransform = Transform(parent=self.pointingArrowRotationTransform, name='pointingArrowTransform', align=uiconst.TOBOTTOM_NOPUSH, width=10, height=7)
        Sprite(parent=self.pointingArrowTransform, texturePath='res:/ui/Texture/classes/ess/reserveBank/Arrow_Big.png', name='pointingArrowTransform', align=uiconst.CENTER, width=10, height=7, color=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR)
        self.arrowsTransform = Transform(parent=self.gaugeCont, name='arrowsTransform', align=uiconst.CENTER, width=49, height=49)
        Sprite(parent=self.arrowsTransform, texturePath='res:/ui/Texture/classes/ess/reserveBank/Arrows.png', name='arrows', width=49, height=49)
        animations.Tr2DRotateTo(self.arrowsTransform, self.arrowsTransform.rotation, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_LINEAR, duration=6.0)
        Sprite(parent=self.gaugeCont, name='ring', texturePath='res:/ui/Texture/classes/ess/reserveBank/Ring.png', align=uiconst.CENTER, width=59, height=59)
        Sprite(parent=self.gaugeCont, name='head', texturePath='res:/ui/Texture/classes/ess/reserveBank/Person.png', align=uiconst.CENTER, width=22, height=21, top=-10)
        self.linkedLabel = EveCaptionSmall(parent=self.gaugeCont, align=uiconst.CENTER, text=self.linked, top=12, bold=False)
        if self.animateIn:
            animations.FadeIn(self.gaugeCont, duration=2)

    def SetLinked(self, linked):
        self.linked = linked
        self.linkedLabel.SetText(linked)

    @property
    def value(self):
        return self.reserveBankHackingGauge.value

    @property
    def nextPayoutTimerValue(self):
        return self.nextPayoutTimer.value

    def SetValue(self, value, animate = True, duration = 0.2):
        self.reserveBankHackingGauge.SetValue(value, animate=animate, duration=duration)
        onePulseWidthRotation = math.pi * 2 / self.pulsesTotal
        segmentToPointTo = self.pulsesTotal - self.pulsesTotal * value
        newRotation = math.pi + onePulseWidthRotation * segmentToPointTo + onePulseWidthRotation / 2
        self.pointingArrowRotationTransform.rotation = newRotation

    def SetNextPayoutTimerValue(self, value, animate = True):
        self.nextPayoutTimer.SetValue(value, animate=animate)

    def OnMouseEnter(self, *args):
        self.hoverStateActive = True
        self.OnMouseEnterCallback()
        animations.FadeOut(self.arrowsTransform, duration=0.2)
        animations.FadeOut(self.nextPayoutTimer, duration=0.2)
        animations.FadeIn(self.pointingArrowRotationTransform, duration=0.2)
        self.reserveBankHackingGauge.OnMouseEnter()
        ContainerAutoSize.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        self.hoverStateActive = False
        self.OnMouseExitCallback()
        animations.FadeIn(self.arrowsTransform, duration=0.2)
        animations.FadeIn(self.nextPayoutTimer, duration=0.2)
        animations.FadeOut(self.pointingArrowRotationTransform, duration=0.2)
        self.reserveBankHackingGauge.OnMouseExit()
        ContainerAutoSize.OnMouseExit(self, *args)


class ReserveBankHackingGauge(RadialBarGraph):
    default_state = uiconst.UI_NORMAL

    def __init__(self, *args, **kwargs):
        RadialBarGraph.__init__(self, *args, **kwargs)
        self.value = self.progress
        self.entryAnimation = None
        self.exitAnimation = None
        self._idleRadius = self.radius
        self._idleInnerRadius = self.inner_radius
        self.hoverBarHeight = 10

    def SetValue(self, value, animate = True, duration = 0.2):
        self.progress = value
        self.value = self.progress

    def OnMouseEnter(self, *args):
        newRadius = self.radius + self.hoverBarHeight
        self.entryAnimation = animations.MorphScalar(self, 'value_radius_modifier', startVal=self.value_radius_modifier, endVal=0.8, duration=0.2)
        animations.MorphScalar(self, 'radius', startVal=self.radius, endVal=newRadius, duration=0.2)

    def OnMouseExit(self, *args):
        self.exitAnimation = animations.MorphScalar(self, 'value_radius_modifier', startVal=self.value_radius_modifier, endVal=0.0, duration=0.2)
        animations.MorphScalar(self, 'radius', startVal=self.radius, endVal=self._idleRadius, duration=0.2)
