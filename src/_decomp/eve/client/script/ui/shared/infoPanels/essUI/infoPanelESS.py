#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\essUI\infoPanelESS.py
import blue
import eveformat
import localization
import locks
import uthread2
from carbon.common.lib.const import SEC
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from dynamicresources.client.ess.bracket.notification import TransitionNotification, COLOR_WARN, ICON_WARN
from dynamicresources.client.ui.ess_info_panel_ui_const import RESERVE_BANK_AUTOPAYOUT_BAR_COLOR, MAIN_BANK_ACTIVE_BAR_COLOR, TRANSITION_LOCK
from dynamicresources.client.ui.main_bank_hacking_timer import MainBankHackingTimer
from dynamicresources.client.ui.reserve_bank_hacking_widget import ReserveBankHackingWidget
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveCaptionLarge, EveCaptionSmall
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.shared.dynamicResource.warpToEssStatefulButtonController import WarpToEssButtonController
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.essUI.controller import InfoPanelESSStateController, MAIN_BANK_HACKING, RESERVE_BANK_UNLOCKED, MAIN_BANK_IDLE, RESERVE_BANK_LOCKED
from evelink.link import Link
from gametime import GetSimTime
from globalConfig import GetESSFeatureFlaggedOffline
from localization.formatters import FormatTimeIntervalShort
from uthread2 import StartTasklet

class InfoPanelESS(InfoPanelBase):
    default_name = 'InfoPanelESS'
    panelTypeID = infoPanelConst.PANEL_ESS
    label = 'UI/ESS/infoPanelESSTitle'
    default_iconTexturePath = 'res:/ui/Texture/classes/ess/Icon_ESS_24px.png'
    default_isModeFixed = False
    hasSettings = False
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnESSDataUpdate_Local', 'OnMainBankPlayerLinkDisconnected', 'OnMainBankPlayerHackSuccess']

    @staticmethod
    def IsAvailable():
        if GetESSFeatureFlaggedOffline(sm.GetService('machoNet')):
            return False
        if sm.GetService('dynamicResourceSvc').GetESSDataForCurrentSystem() is None:
            return False
        return True

    def ApplyAttributes(self, attributes):
        super(InfoPanelESS, self).ApplyAttributes(attributes)
        self.titleCaption = EveCaptionSmall(parent=self.headerCont, text=localization.GetByLabel('UI/ESS/infoPanelESSTitle'), align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.bodyCont = ContainerAutoSize(name='bodyCont', align=uiconst.TOTOP, parent=self.mainCont)
        self.mainBankState = None
        self.reserveBankState = None
        self.updateIdleMainBankTimer = None
        self.updateMainBankHackingGaugeTimer = None
        self.updateMainBankHackingLabelTimer = None
        self.updateReserveBankHackingStateTimer = None
        self.mainBankDelayedPayoutTimerGauge = None
        self.updateIdleMainBankLabelsTimer = None
        self.collapsedStateMainBankIdleGaugeAutoTimer = None
        self.collapsedStateMainBankHackingTimer = None
        self.collapsedStateReserveBankHackingTimer = None
        self.mainBankHackTimerGauge = None
        self.mainBankAutopaymentProgressBar = None
        self.reserveBankHackingGauge = None
        self.collapsedStateCont = None
        self.state_controller = InfoPanelESSStateController()
        StartTasklet(self.TransitionState)

    def ConstructHeaderButton(self):
        btn = ButtonIcon(parent=self.headerBtnCont, align=uiconst.TOPRIGHT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), texturePath=self.default_iconTexturePath, iconSize=18, showIcon=True, func=uicore.cmd.OpenEncounterSurveillanceSystemInAgency)
        btn.hint = localization.GetByLabel('UI/ESS/LinkToAgencyTooltip')

    def ConstructHiddenCollpsedState(self):
        if self.collapsedStateCont:
            self.collapsedStateCont.Flush()
        else:
            self.collapsedStateCont = ContainerAutoSize(parent=self.headerCont, align=uiconst.TOLEFT)
        mainBankState = self.state_controller.GetEnumeratedMainBankState()
        reserveBankState = self.state_controller.GetEnumeratedReserveBankState()
        if mainBankState == MAIN_BANK_IDLE:
            self.collapsedStateMainBankIdleGauge = GaugeCircular(parent=self.collapsedStateCont, align=uiconst.TOLEFT, showMarker=False, colorStart=Color.WHITE, colorEnd=Color.WHITE, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), radius=12, state=uiconst.UI_DISABLED, top=2)
            self.UpdateMainBankAutopaymentGauge(None, self.collapsedStateMainBankIdleGauge, animate=False)
            self.collapsedStateMainBankIdleGaugeAutoTimer = AutoTimer(500, self.UpdateMainBankAutopaymentGauge, self.collapsedStateMainBankIdleGaugeAutoTimer, self.collapsedStateMainBankIdleGauge, animate=False)
        elif mainBankState == MAIN_BANK_HACKING:
            self.collapsedStateMainBankhackingGauge = GaugeCircular(parent=self.collapsedStateCont, align=uiconst.TOLEFT, showMarker=False, colorStart=MAIN_BANK_ACTIVE_BAR_COLOR, colorEnd=MAIN_BANK_ACTIVE_BAR_COLOR, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), radius=12, state=uiconst.UI_DISABLED, top=2)
            self.UpdateMainBankHackingTimerGauge(None, self.collapsedStateMainBankhackingGauge)
            self.collapsedStateMainBankHackingTimer = AutoTimer(500, self.UpdateMainBankHackingTimerGauge, self.collapsedStateMainBankHackingTimer, self.collapsedStateMainBankhackingGauge)
        if reserveBankState == RESERVE_BANK_UNLOCKED:
            reserveBankGauge = GaugeCircular(parent=self.collapsedStateCont, align=uiconst.TOLEFT, showMarker=False, colorStart=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR, colorEnd=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), radius=12, state=uiconst.UI_DISABLED, padLeft=10, top=2)

            def update_simple_reserve_bank_gauge(thisTimer, gauge):
                if self.destroyed:
                    thisTimer = None
                    return
                pulsesRemaining = self.state_controller.Get('reserveBankPulsesRemaining')
                pulsesTotal = self.state_controller.Get('reserveBankPulsesTotal')
                newGaugeValue = float(pulsesRemaining) / float(pulsesTotal)
                gauge.SetValue(newGaugeValue, animate=False)

            update_simple_reserve_bank_gauge(None, reserveBankGauge)
            self.collapsedStateReserveBankHackingTimer = AutoTimer(500, update_simple_reserve_bank_gauge, self.collapsedStateReserveBankHackingTimer, reserveBankGauge)
        if self.mode != infoPanelConst.MODE_COMPACT:
            self.collapsedStateCont.Hide()

    def ConstructCompact(self):
        if self.titleCaption:
            self.titleCaption.Hide()
        if self.collapsedStateCont:
            self.collapsedStateCont.Show()

    def ConstructNormal(self):
        if self.titleCaption:
            self.titleCaption.Show()
        if self.collapsedStateCont:
            self.collapsedStateCont.Hide()

    def TransitionState(self, newMainBankState = None, newReserveBankState = None, linkDisconnected = False, hackSuccess = False, thisClient = False):
        with locks.TempLock('TransitionState'):
            if not self.state_controller.RefreshEssData():
                return
            if newMainBankState is None:
                newMainBankState = self.state_controller.GetEnumeratedMainBankState()
            if newReserveBankState is None:
                newReserveBankState = self.state_controller.GetEnumeratedReserveBankState()
            animateMainBankChange = False
            animateReserveBankChange = False
            if self.mainBankState:
                if self.mainBankState != newMainBankState:
                    animateMainBankChange = True
                    if self.mainBankState == MAIN_BANK_IDLE and newMainBankState == MAIN_BANK_HACKING:
                        animations.FadeOut(self.mainBankIdleIskSymbolTransform, duration=0.25)
                        animations.FadeOut(self.mainBankAutopaymentProgressBar, duration=0.25)
                        animations.FadeOut(self.mainBankAutupaymentTimerTextCont, duration=0.25)
                        animations.MoveOutRight(self.mainBankAutupaymentTimerTextCont, amount=10, duration=0.25, sleep=True)
                        link_state = self.state_controller.GetMainBankLinkState()
                        if not link_state['this_client']:
                            notificationBox = TransitionNotification(self.mainBankIdleTimerCont, uiconst.TOPLEFT, text=localization.GetByLabel('UI/ESS/MainBankOtherPlayerHacking'), iconHexColor=COLOR_WARN, icon=ICON_WARN)
                            notificationBox.show(sleep=True)
                            uthread2.sleep(1)
                            notificationBox.hide(close=True, sleep=True)
                    elif self.mainBankState == MAIN_BANK_HACKING and newMainBankState == MAIN_BANK_IDLE:
                        animations.FadeOut(self.mainBankHackingLabelsCont, duration=0.25)
                        animations.MoveOutLeft(self.mainBankHackingLabelsCont, amount=10, duration=0.25)
                        if self.mainBankHackTimerGauge:
                            self.mainBankHackTimerGauge.AnimateOut()
                        if self.mainBankDelayedPayoutTimerGauge:
                            animations.FadeOut(self.mainBankDelayedPayoutLockSymbol)
                            animations.FadeOut(self.mainBankDelayedPayoutTimerGauge, sleep=True)
                        if not thisClient:
                            alertText = None
                            if linkDisconnected:
                                alertText = localization.GetByLabel('UI/ESS/MainBankLinkDisconnected')
                            elif hackSuccess:
                                alertText = localization.GetByLabel('UI/ESS/MainBankHackingSuccess')
                            notificationBox = TransitionNotification(self.mainBankHackingCont, uiconst.TOPLEFT, text=alertText, iconHexColor=COLOR_WARN, icon=ICON_WARN)
                            notificationBox.show(sleep=True)
                            uthread2.sleep(1)
                            notificationBox.hide(close=True, sleep=True)
                        self.mainBankHackTimerGauge = None
            if self.reserveBankState:
                if self.reserveBankState != newReserveBankState:
                    animateReserveBankChange = True
                    if self.reserveBankState == RESERVE_BANK_UNLOCKED and newReserveBankState == RESERVE_BANK_LOCKED:
                        animations.FadeOut(self.reserveBankHackingTimerLabelsCont, duration=0.25)
                        animations.MoveOutLeft(self.reserveBankHackingTimerLabelsCont, amount=0.05, duration=0.25)
                        self.reserveBankHackingGauge.AnimateOut()
            self.mainBankState = newMainBankState
            self.reserveBankState = newReserveBankState
            self.ConstructHiddenCollpsedState()
            self.ConstructUncollapsedState(animateMainBankChange, animateReserveBankChange)

    def ConstructUncollapsedState(self, animateMainBankChange, animateReserveBankChange):
        with locks.TempLock(TRANSITION_LOCK):
            gaugeStates = {'mainBankHackGaugeStartValue': None,
             'reserveBankHackGaugeStartValue': None,
             'reserveBankNextPayoutTimerValue': None,
             'mainBankIdleTimerStartValue': None,
             'mainBankDelayedAutopayGaugeValue': None}
            if self.mainBankAutopaymentProgressBar:
                gaugeStates['mainBankIdleTimerStartValue'] = self.mainBankAutopaymentProgressBar.value
            if self.mainBankHackTimerGauge:
                gaugeStates['mainBankHackGaugeStartValue'] = self.mainBankHackTimerGauge.value
            if self.reserveBankHackingGauge:
                gaugeStates['reserveBankHackGaugeStartValue'] = self.reserveBankHackingGauge.value
                gaugeStates['reserveBankNextPayoutTimerValue'] = self.reserveBankHackingGauge.nextPayoutTimerValue
            if self.mainBankDelayedPayoutTimerGauge:
                gaugeStates['mainBankDelayedAutopayGaugeValue'] = self.mainBankDelayedPayoutTimerGauge.value
            self.bodyCont.Flush()
            if self.updateIdleMainBankTimer:
                self.updateIdleMainBankTimer.KillTimer()
                self.updateIdleMainBankTimer = None
            if self.updateMainBankHackingGaugeTimer:
                self.updateMainBankHackingGaugeTimer.KillTimer()
                self.updateMainBankHackingGaugeTimer = None
            if self.updateReserveBankHackingStateTimer:
                self.updateReserveBankHackingStateTimer.KillTimer()
                self.updateReserveBankHackingStateTimer = None
            if self.updateMainBankHackingLabelTimer:
                self.updateMainBankHackingLabelTimer.KillTimer()
                self.updateMainBankHackingLabelTimer = None
            self.ConstructMainBankInfo(gaugeStates, animateMainBankChange)
            self.ConstructReserveBankInfo(gaugeStates, animateReserveBankChange)
            if self.mainBankState == MAIN_BANK_HACKING or self.reserveBankState == RESERVE_BANK_UNLOCKED:
                warpToButtonCont = ContainerAutoSize(parent=self.bodyCont, align=uiconst.TOTOP)
                StatefulButton(name='warpToEssButton', parent=warpToButtonCont, align=uiconst.TOPLEFT, controller=WarpToEssButtonController(), top=15)

    def ConstructReserveBankInfo(self, gaugeStates, animate):
        if self.state_controller.GetEssData() is not None:
            self.reserveBankCont = ContainerAutoSize(name='reserveBankCont', parent=self.bodyCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=15)
            reserveBankLinkText = localization.GetByLabel('UI/ESS/infoPanelReserveBank', iskString=eveformat.isk_readable_short(self.state_controller.Get('reserveValue', 0.0)))
            reserveBankLink = Link(url='essTransactionHistory:reserveBank', text=reserveBankLinkText, alt=localization.GetByLabel('UI/ESS/TransactionHistoryHint'))
            reserveBankLinkCont = ContainerAutoSize(parent=self.reserveBankCont, align=uiconst.TOTOP, name='reserveBankLinkCont')
            EveLabelLarge(parent=reserveBankLinkCont, text=reserveBankLink, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, linkStyle=uiconst.LINKSTYLE_SUBTLE)
            pulsesRemaining = self.state_controller.Get('reserveBankPulsesRemaining')
            pulsesTotal = self.state_controller.Get('reserveBankPulsesTotal')
            if pulsesRemaining > 0 and pulsesTotal > 0:
                self.ConstructReserveBankUnlockedState(animate, gaugeStates)
            else:
                self.ConstructReserveBankLockedState(animate)
                if self.reserveBankHackingGauge:
                    self.reserveBankHackingGauge = None

    def ConstructReserveBankLockedState(self, animate):
        startingOpacity = 0 if animate else 1
        lockedGaugeCont = Container(name='lockedGaugeCont', parent=self.reserveBankCont, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, padTop=13, height=50, state=uiconst.UI_DISABLED, opacity=startingOpacity)
        GaugeCircular(parent=lockedGaugeCont, color=Color.WHITE, align=uiconst.TOLEFT, showMarker=False, lineWidth=3, radius=22, colorStart=Color.WHITE, colorEnd=Color.WHITE, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA())
        lockSymbolTransform = Transform(parent=lockedGaugeCont, align=uiconst.TOPLEFT, width=44, height=44)
        lockSymbolSprite = Sprite(parent=lockSymbolTransform, align=uiconst.CENTER, texturePath='res:/ui/Texture/classes/ess/mainBank/lock.png', color=Color(*Color.WHITE).SetAlpha(0.8).GetRGBA(), width=25, height=25)
        EveLabelLarge(parent=lockedGaugeCont, align=uiconst.TOLEFT, bold=False, padLeft=15, top=11, text=localization.GetByLabel('UI/ESS/BankLocked'))
        lockSymbolSprite.scalingCenter = (0.5, 0.5)
        if animate:
            animations.FadeIn(lockedGaugeCont, duration=0.25)

    def ConstructReserveBankUnlockedState(self, animate, gaugeStates):
        pulsesRemaining = self.state_controller.Get('reserveBankPulsesRemaining')
        pulsesTotal = self.state_controller.Get('reserveBankPulsesTotal')
        lastPulseInitiated = self.state_controller.Get('reserveBankLastPulseInitiated')
        activeLinks = self.state_controller.Get('reserveBankActiveLinks')
        currentSimTime = blue.os.GetSimTime()
        pulseInterval = self.state_controller.GetSetting('reservePulseIntervalSeconds') * SEC
        hackInfoCont = Container(parent=self.reserveBankCont, align=uiconst.TOTOP, height=150)
        initialValue = float(pulsesRemaining) / float(pulsesTotal)
        payoutValues = self.state_controller.CalculateReserveBankPayouts()
        self.reserveBankHackingGauge = ReserveBankHackingWidget(parent=hackInfoCont, name='reserveBankHackingWidget', align=uiconst.TOLEFT, pulsesTotal=pulsesTotal, progress=initialValue, linked=activeLinks, paymentValues=payoutValues, onMouseEnterCallback=self._OnReserveBankHackingWidgetMouseEnter, onMouseExitCallback=self._OnReserveBankHackingWidgetMouseExit, animateIn=animate)
        gaugeValue = float(pulsesRemaining) / float(pulsesTotal)
        self.reserveBankHackingGauge.SetValue(gaugeValue)
        if gaugeStates['reserveBankNextPayoutTimerValue']:
            self.reserveBankHackingGauge.SetNextPayoutTimerValue(gaugeStates['reserveBankNextPayoutTimerValue'], animate=False)
        self.reserveBankHackingTimerLabelsCont = Container(name='reserveBankHackingTimerLabelsCont', parent=hackInfoCont, align=uiconst.TOLEFT_PROP, width=0.5, padLeft=15)
        EveLabelLarge(parent=self.reserveBankHackingTimerLabelsCont, text=localization.GetByLabel('UI/ESS/ReserveBankOpenFor'), align=uiconst.TOTOP, bold=False, padTop=20)
        timeUntilNextPulse = pulseInterval - (currentSimTime - lastPulseInitiated)
        timeLeftUntilCloseText = FormatTimeIntervalShort(pulseInterval * (pulsesRemaining - 1) + timeUntilNextPulse, showFrom='minute')
        self.reserveBankTimeLeftLabel = EveCaptionLarge(parent=self.reserveBankHackingTimerLabelsCont, text=timeLeftUntilCloseText, align=uiconst.TOTOP, bold=False, color=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR)
        if timeUntilNextPulse <= 0:
            timeUntilNextPulseText = FormatTimeIntervalShort(0, showFrom='minute')
        else:
            timeUntilNextPulseText = FormatTimeIntervalShort(timeUntilNextPulse, showFrom='minute')
        EveLabelLarge(parent=self.reserveBankHackingTimerLabelsCont, align=uiconst.TOTOP, bold=False, text=localization.GetByLabel('UI/ESS/MainBankNextAutopayLabel'))
        self.reserveBankTimeUntilNextPulseLabel = EveCaptionLarge(parent=self.reserveBankHackingTimerLabelsCont, align=uiconst.TOTOP, bold=False, text=timeUntilNextPulseText)
        self.reserveBankHackingOnHoverLabelsCont = Container(name='reserveBankHackingTimerLabelsCont', parent=hackInfoCont, align=uiconst.TOLEFT_PROP, width=0.5, padLeft=17, opacity=0)
        EveLabelLarge(parent=self.reserveBankHackingOnHoverLabelsCont, text=localization.GetByLabel('UI/ESS/ReserveBankPaymentRate'), align=uiconst.TOTOP, bold=False, padTop=20)
        self.reserveBankPayoutRateLabel = EveCaptionLarge(parent=self.reserveBankHackingOnHoverLabelsCont, align=uiconst.TOTOP, text=self._GetPaymentRateText(), bold=False, color=RESERVE_BANK_AUTOPAYOUT_BAR_COLOR)
        EveLabelLarge(parent=self.reserveBankHackingOnHoverLabelsCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ESS/MainBankNextAutopayLabel'), bold=False)
        self.reserveBankNextPayoutLabel = EveCaptionLarge(parent=self.reserveBankHackingOnHoverLabelsCont, align=uiconst.TOTOP, text=eveformat.isk_readable_short(25000000), bold=False)
        self.updateReserveBankHackingStateTimer = AutoTimer(500, self.UpdateReserveBankState)

    def _GetPaymentRateText(self):
        earlyPayoutThresholdFactor = round(self.state_controller.GetSetting('earlyPayoutThresholdFactor'), 1)
        latePayoutThresholdFactor = round(self.state_controller.GetSetting('latePayoutThresholdFactor'), 1)
        pulsesRemaining = self.state_controller.Get('reserveBankPulsesRemaining')
        pulsesTotal = self.state_controller.Get('reserveBankPulsesTotal')
        proportionComplete = 1.0 - float(pulsesRemaining) / float(pulsesTotal)
        if proportionComplete < earlyPayoutThresholdFactor:
            return localization.GetByLabel('UI/ESS/ReserveBankEarly')
        elif proportionComplete >= earlyPayoutThresholdFactor and proportionComplete < 1.0 - latePayoutThresholdFactor:
            return localization.GetByLabel('UI/ESS/ReserveBankPeak')
        else:
            return localization.GetByLabel('UI/ESS/ReserveBankLate')

    def _OnReserveBankHackingWidgetMouseEnter(self):

        def fade_in_cont():
            self.reserveBankHackingTimerLabelsCont.Hide()
            animations.FadeIn(self.reserveBankHackingOnHoverLabelsCont, duration=0.1)
            animations.MoveInFromLeft(self.reserveBankHackingOnHoverLabelsCont, duration=0.1, amount=0.025)

        animations.FadeOut(self.reserveBankHackingTimerLabelsCont, duration=0.1, callback=fade_in_cont)

    def _OnReserveBankHackingWidgetMouseExit(self):
        animations.FadeIn(self.reserveBankHackingTimerLabelsCont, duration=0.1, callback=self.reserveBankHackingTimerLabelsCont.Show)
        animations.FadeOut(self.reserveBankHackingOnHoverLabelsCont, duration=0.1)

    def UpdateMainBankAutopaymentGauge(self, thisTimer, gauge, animate = True):
        if self.destroyed or not self.state_controller.GetEssData():
            thisTimer = None
            return
        maxVal = self.state_controller.Get('nextScheduledAutopayment', GetSimTime() + 100)
        minVal = self.state_controller.Get('lastAutopayment', GetSimTime())
        current = GetSimTime()
        proportion = 1.0 - float(current - minVal) / float(maxVal - minVal)
        proportion = max(0.0, min(proportion, 1.0))
        gauge.SetValue(proportion, animate=animate)

    def UpdateMainBankAutopaymemtLabel(self, thisTimer, label):
        if self.destroyed or not self.state_controller.GetEssData():
            thisTimer = None
            return
        maxVal = self.state_controller.Get('nextScheduledAutopayment', GetSimTime() + 100)
        current = GetSimTime()
        autopaymentCountdown = maxVal - current
        if autopaymentCountdown > 0:
            label.SetText(FormatTimeIntervalShort(autopaymentCountdown, showFrom='hour', showTo='second'))
        else:
            label.SetText(FormatTimeIntervalShort(0, showFrom='hour', showTo='second'))

    def UpdateReserveBankState(self):
        if not self.state_controller.GetEssData():
            self.updateReserveBankHackingStateTimer.KillTimer()
            self.updateReserveBankHackingStateTimer = None
            self.reserveBankHackingGauge = None
            return
        lastPulseInitiated = self.state_controller.Get('reserveBankLastPulseInitiated')
        pulsesRemaining = self.state_controller.Get('reserveBankPulsesRemaining')
        pulsesTotal = self.state_controller.Get('reserveBankPulsesTotal')
        if self.destroyed or pulsesRemaining < 1:
            self.updateReserveBankHackingStateTimer.KillTimer()
            self.updateReserveBankHackingStateTimer = None
            self.reserveBankHackingGauge = None
            return
        currentSimTime = blue.os.GetSimTime()
        pulseInterval = self.state_controller.GetSetting('reservePulseIntervalSeconds') * SEC
        nextPayoutIn = max(0, pulseInterval - (currentSimTime - lastPulseInitiated))
        timeLeft = pulseInterval * (pulsesRemaining - 1)
        timeLeftText = FormatTimeIntervalShort(timeLeft + nextPayoutIn, showFrom='minute')
        self.reserveBankTimeLeftLabel.SetText(timeLeftText)
        nextPayoutInText = FormatTimeIntervalShort(nextPayoutIn, showFrom='minute')
        if nextPayoutIn <= 0:
            nextPayoutInText = FormatTimeIntervalShort(0, showFrom='minute')
        self.reserveBankTimeUntilNextPulseLabel.SetText(nextPayoutInText)
        newNextPayoutTimerValue = float(nextPayoutIn) / float(pulseInterval)
        if newNextPayoutTimerValue < 0.01:
            newNextPayoutTimerValue = 0
        normalGaugeMovement = newNextPayoutTimerValue <= self.reserveBankHackingGauge.nextPayoutTimerValue
        self.reserveBankHackingGauge.SetNextPayoutTimerValue(newNextPayoutTimerValue, animate=normalGaugeMovement)
        if newNextPayoutTimerValue == 0:
            self.reserveBankHackingGauge.BlinkOutNextPaymentTimer()
        if not normalGaugeMovement:
            self.reserveBankHackingGauge.BlinkInNextPaymentTimer()
        newGaugeValue = float(pulsesRemaining) / float(pulsesTotal)
        self.reserveBankHackingGauge.SetValue(newGaugeValue)
        activeLinks = self.state_controller.Get('reserveBankActiveLinks')
        self.reserveBankHackingGauge.SetLinked(activeLinks)
        nextPayoutAmount = self.state_controller.GetCurrentReserveBankPulsePayout()
        self.reserveBankNextPayoutLabel.SetText(eveformat.isk_readable_short(nextPayoutAmount))
        self.reserveBankPayoutRateLabel.SetText(self._GetPaymentRateText())

    def ConstructMainBankInfo(self, gaugeStates, animate):
        if self.state_controller.GetEssData() is not None:
            mainBankLinkText = localization.GetByLabel('UI/ESS/infoPanelMainBank', iskString=eveformat.isk_readable(self.state_controller.Get('mainValue', 0.0)))
            mainBankLink = Link(url='essTransactionHistory:mainBank', text=mainBankLinkText, alt=localization.GetByLabel('UI/ESS/TransactionHistoryHint'))
            mainBankLabelCont = ContainerAutoSize(parent=self.bodyCont, name='mainBankLabelCont', align=uiconst.TOTOP, padTop=15)
            EveLabelLarge(parent=mainBankLabelCont, text=mainBankLink, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
            if self.mainBankState == MAIN_BANK_HACKING:
                self.ConstructMainBankHackingState(gaugeStates, animate)
            else:
                self.ConstructMainBankIdleState(gaugeStates, animate)

    def ConstructMainBankHackingState(self, gaugeStates, animate):
        self.mainBankHackingCont = Container(name='mainBankHackingCont', parent=self.bodyCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=13, padBottom=0, height=46)
        autopayTimerCont = Container(name='autopayTimerCont', parent=self.mainBankHackingCont, align=uiconst.TOTOP, height=50)
        gaugeStartingOpacity = 1
        if animate:
            gaugeStartingOpacity = 0
        self.mainBankDelayedPayoutLockSymbol = Transform(parent=autopayTimerCont, align=uiconst.TOLEFT_NOPUSH, width=44, height=44, top=-1, opacity=gaugeStartingOpacity, state=uiconst.UI_DISABLED)
        lockSprite = Sprite(parent=self.mainBankDelayedPayoutLockSymbol, width=32, height=32, align=uiconst.CENTER, color=Color(*Color.WHITE).SetAlpha(0.8).GetRGBA(), texturePath='res:/ui/Texture/classes/ess/mainBank/lock.png')
        lockSprite.scalingCenter = (0.5, 0.5)
        self.mainBankDelayedPayoutTimerGauge = GaugeCircular(parent=autopayTimerCont, color=Color.WHITE, align=uiconst.TOLEFT, colorStart=Color.WHITE, colorEnd=Color.WHITE, showMarker=False, lineWidth=5.0, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), radius=22, opacity=gaugeStartingOpacity, state=uiconst.UI_DISABLED)
        if gaugeStates['mainBankDelayedAutopayGaugeValue']:
            self.mainBankDelayedPayoutTimerGauge.SetValue(gaugeStates['mainBankDelayedAutopayGaugeValue'], animate=animate)
        if animate:
            animations.FadeIn(self.mainBankDelayedPayoutTimerGauge)
            animations.FadeIn(self.mainBankDelayedPayoutLockSymbol)
        startValue = gaugeStates['mainBankHackGaugeStartValue'] or 1.0
        mainBankLink = self.state_controller.GetMainBankLinkState()['link']
        self.mainBankHackTimerGauge = MainBankHackingTimer(name='mainBankHackTimerGauge', parent=autopayTimerCont, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT, characterID=mainBankLink.get('characterID'), padLeft=20, value=startValue, animate=animate)
        self.mainBankHackingLabelsCont = ContainerAutoSize(name='hackingLabelsCont', parent=autopayTimerCont, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT, padLeft=15)
        EveLabelLarge(parent=self.mainBankHackingLabelsCont, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/ESS/mainBankHackedIn'))
        timeLeftText = FormatTimeIntervalShort(self.state_controller.GetTimeLeftForMainBankHack(), showFrom='minute')
        self.mainBankHackTimerLabel = EveCaptionLarge(parent=self.mainBankHackingLabelsCont, align=uiconst.CENTERLEFT, text=timeLeftText, color=MAIN_BANK_ACTIVE_BAR_COLOR, padTop=5, bold=False)
        if gaugeStates['mainBankHackGaugeStartValue']:
            self.mainBankHackTimerGauge.SetValue(gaugeStates['mainBankHackGaugeStartValue'])
        self.updateMainBankHackingLabelTimer = AutoTimer(500, self.UpdateMainBankHackingTimerLabel)
        self.updateMainBankHackingGaugeTimer = AutoTimer(500, self.UpdateMainBankHackingTimerGauge, self.updateMainBankHackingGaugeTimer, self.mainBankHackTimerGauge)
        self.updateIdleMainBankTimer = AutoTimer(500, self.UpdateMainBankAutopaymentGauge, self.updateIdleMainBankTimer, self.mainBankDelayedPayoutTimerGauge)

    def UpdateMainBankHackingTimerLabel(self):
        if self.destroyed:
            self.updateMainBankHackingLabelTimer = None
            return
        timeLeftText = FormatTimeIntervalShort(self.state_controller.GetTimeLeftForMainBankHack(), showFrom='minute')
        self.mainBankHackTimerLabel.SetText(timeLeftText)

    def UpdateMainBankHackingTimerGauge(self, thisTimer, gauge):
        if self.destroyed and thisTimer:
            thisTimer.KillTimer()
            thisTimer = None
            return
        newValue = self.state_controller.GetProportionOfTimeLeftForMainBankHack()
        gauge.SetValue(newValue)

    def ConstructMainBankIdleState(self, gaugeStates, animate):
        if self.state_controller.GetEssData():
            self.mainBankCont = ContainerAutoSize(name='mainBankCont', parent=self.bodyCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=13)
            self.mainBankIdleTimerCont = Container(name='timerCont', parent=self.mainBankCont, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, height=46, state=uiconst.UI_DISABLED)
            startingOpacity = 0 if animate else 1
            self.mainBankAutopaymentProgressBar = GaugeCircular(parent=self.mainBankIdleTimerCont, color=Color.WHITE, align=uiconst.TOLEFT, showMarker=False, lineWidth=5.0, radius=22, colorStart=Color.WHITE, colorEnd=Color.WHITE, colorBg=Color(*Color.WHITE).SetAlpha(0.2).GetRGBA(), opacity=startingOpacity)
            self.mainBankIdleIskSymbolTransform = Transform(parent=self.mainBankIdleTimerCont, align=uiconst.TOPLEFT, width=44, height=44)
            iskSymbolSprite = Sprite(parent=self.mainBankIdleIskSymbolTransform, align=uiconst.CENTER, texturePath='res:/ui/Texture/classes/ess/mainBank/wallet.png', color=Color(*Color.WHITE).SetAlpha(0.8).GetRGBA(), width=25, height=25)
            iskSymbolSprite.scalingCenter = (0.5, 0.5)
            self.mainBankAutupaymentTimerTextCont = ContainerAutoSize(name='timerTextCont', parent=self.mainBankIdleTimerCont, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT, padLeft=15, opacity=startingOpacity)
            EveLabelLarge(parent=self.mainBankAutupaymentTimerTextCont, text=localization.GetByLabel('UI/ESS/MainBankNextAutopayLabel'), align=uiconst.TOPLEFT, top=-3)
            current = GetSimTime()
            maxVal = self.state_controller.Get('nextScheduledAutopayment', GetSimTime() + 100)
            autopaymentCountdown = max(0, maxVal - current)
            self.mainBankIdlePaymentCountdownLabel = EveCaptionLarge(parent=self.mainBankAutupaymentTimerTextCont, text=FormatTimeIntervalShort(autopaymentCountdown, showFrom='hour', showTo='second'), align=uiconst.BOTTOMLEFT, bold=False, top=3)
            if not animate and gaugeStates['mainBankIdleTimerStartValue']:
                self.mainBankAutopaymentProgressBar.SetValue(gaugeStates['mainBankIdleTimerStartValue'], animate=False)

            def animate_in():
                with locks.TempLock(TRANSITION_LOCK):
                    animations.FadeIn(self.mainBankAutopaymentProgressBar, duration=0.25)
                    animations.FadeIn(self.mainBankAutupaymentTimerTextCont, duration=0.25)
                    animations.MoveInFromRight(self.mainBankAutupaymentTimerTextCont, amount=10, duration=0.25, sleep=True)

            if animate:
                StartTasklet(animate_in)
            self.updateIdleMainBankTimer = AutoTimer(500, self.UpdateMainBankAutopaymentGauge, self.updateIdleMainBankTimer, self.mainBankAutopaymentProgressBar)
            self.updateIdleMainBankLabelsTimer = AutoTimer(500, self.UpdateMainBankAutopaymemtLabel, self.updateIdleMainBankLabelsTimer, self.mainBankIdlePaymentCountdownLabel)

    def OnESSDataUpdate_Local(self):
        self.TransitionState()

    def OnMainBankPlayerLinkDisconnected(self, data):
        thisClient = data['characterID'] == session.charid
        self.TransitionState(linkDisconnected=True, newMainBankState=MAIN_BANK_IDLE, thisClient=thisClient)

    def OnMainBankPlayerHackSuccess(self, data):
        thisClient = data['characterID'] == session.charid
        self.TransitionState(hackSuccess=True, newMainBankState=MAIN_BANK_IDLE, thisClient=thisClient)
