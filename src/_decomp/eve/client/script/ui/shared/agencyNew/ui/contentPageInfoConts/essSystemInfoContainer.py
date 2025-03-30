#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\essSystemInfoContainer.py
import appConst
from carbon.common.script.util.format import FmtAmt, FmtTimeIntervalMaxParts
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.util.color import Color
from dynamicresources.common.ess.const import ESS_AUTOPAY_STATE_SHORT, ESS_AUTOPAY_STATE_MEDIUM, ESS_RESERVE_WINDOW_STATE_INACTIVE
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.agencyConst import ESS_TIME_TO_COLOR_MAP, ESS_TIME_TO_LABEL_MAP
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.baseContentPageInfoCont import BaseContentPageInfoContainer
from carbonui.control.section import SubSectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.tooltips.ess.essBountiesOutputTooltip import EssBountiesOutputTooltip
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from localization import GetByLabel

class ESSSystemInfoContainer(BaseContentPageInfoContainer):
    default_name = 'ESSSystemInfoContainer'
    default_headerText = GetByLabel('UI/Agency/ESS/ESSSystemInfo')

    def __init__(self, *args, **kwargs):
        self.payoutStateIndicators = []
        super(ESSSystemInfoContainer, self).__init__(*args, **kwargs)

    def ConstructLayout(self):
        self.ConstructBountiesOutputSection()
        self.ConstructMainBankSection()
        self.ConstructReserveBankSection()

    def _UpdateContentPiece(self, contentPiece):
        self.systemInfoContainer.UpdateContentPiece(contentPiece)
        self.primaryActionButton.SetController(contentPiece)
        self.UpdateBountiesOutputLabel(contentPiece.bountiesOutput)
        self.UpdateMainBankAmountLabel(contentPiece.mainBankAmount)
        self.UpdateReserveBankAmountLabel(contentPiece.reserveBankAmount)
        essSystemDetails = contentPiece.GetESSSystemDetails()
        self.UpdateTimeToAutoPaymentGauge(essSystemDetails['autopaymentWindowState'])
        self.UpdateActiveLinksLabel(essSystemDetails['activeLinks'])
        self.UpdateReserveTimeChosenLabel(essSystemDetails['totalPulses'], essSystemDetails['reserveTimeWindowState'])
        self.UpdatePayoutStateContainer(essSystemDetails['reserveTimeWindowState'])
        dynamicResourceSettings = self.GetDynamicResourceSettings()
        self.UpdateTimeChosenTooltip(essSystemDetails['reserveTimeChosen'], timeFactor=dynamicResourceSettings['reserveBankTimeAccessFactor'])

    def GetEntryContentPieces(self):
        pass

    def ConstructBountiesOutputSection(self):
        self.bountiesOutputSection = SubSectionAutoSize(parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/ESS/DynamicBounties'), top=10)
        bountiesOutputContainer = Container(name='bountiesOutputContainer', parent=self.bountiesOutputSection, align=uiconst.TOTOP, height=26)
        EveLabelMedium(parent=bountiesOutputContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/BountiesOutput'))
        self.bountiesOutputLabel = EveLabelMedium(parent=bountiesOutputContainer, align=uiconst.CENTERRIGHT, left=35)
        DescriptionIcon(parent=bountiesOutputContainer, align=uiconst.CENTERRIGHT, tooltipPanelClassInfo=EssBountiesOutputTooltip())

    def ConstructMainBankSection(self):
        self.mainBankSection = SubSectionAutoSize(parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/ESS/MainBank'), top=10)
        bankAmountContainer = Container(parent=self.mainBankSection, align=uiconst.TOTOP, height=26)
        EveLabelMedium(parent=bankAmountContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/BankAmount'))
        self.mainBankAmountLabel = EveLabelMedium(parent=bankAmountContainer, align=uiconst.CENTERRIGHT, left=35, state=uiconst.UI_NORMAL)
        DescriptionIcon(parent=bankAmountContainer, align=uiconst.CENTERRIGHT, tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/MainBankAmount')))
        autoPaymentContainer = Container(parent=self.mainBankSection, align=uiconst.TOTOP, height=26, top=4)
        EveLabelMedium(parent=autoPaymentContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/TimeToAutoPayment'))
        self.timeToAutoPaymentGauge = Gauge(parent=autoPaymentContainer, align=uiconst.CENTERRIGHT, left=35)
        self.timeToAutoPaymentIcon = DescriptionIcon(parent=autoPaymentContainer, align=uiconst.CENTERRIGHT, tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/TimeToAutoPayment')))

    def ConstructReserveBankSection(self):
        self.reserveBankSection = SubSectionAutoSize(parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/ESS/ReserveBank'), top=10)
        reserveBankAmountContainer = Container(parent=self.reserveBankSection, align=uiconst.TOTOP, height=26)
        EveLabelMedium(parent=reserveBankAmountContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/BankAmount'))
        self.reserveBankAmountLabel = EveLabelMedium(parent=reserveBankAmountContainer, align=uiconst.CENTERRIGHT, left=35, state=uiconst.UI_NORMAL)
        DescriptionIcon(parent=reserveBankAmountContainer, align=uiconst.CENTERRIGHT, tooltipPanelClassInfo=SimpleTextTooltip(GetByLabel('UI/Agency/Tooltips/Exploration/ESS/ReserveBankAmount')))
        activeLinksContainer = Container(parent=self.reserveBankSection, align=uiconst.TOTOP, height=26, top=4)
        EveLabelMedium(parent=activeLinksContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/ActiveLinks'))
        self.activeLinksLabel = EveLabelMedium(parent=activeLinksContainer, align=uiconst.CENTERRIGHT, left=35)
        DescriptionIcon(parent=activeLinksContainer, align=uiconst.CENTERRIGHT, tooltipPanelClassInfo=SimpleTextTooltip(GetByLabel('UI/Agency/Tooltips/Exploration/ESS/ActiveLinks')))
        timeChosenContainer = Container(parent=self.reserveBankSection, align=uiconst.TOTOP, height=26, top=4)
        EveLabelMedium(parent=timeChosenContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/ESS/TimeChosen'))
        self.reserveTimeChosenLabel = EveLabelMedium(parent=timeChosenContainer, align=uiconst.CENTERRIGHT, left=35)
        self.timeChosenIcon = DescriptionIcon(parent=timeChosenContainer, align=uiconst.CENTERRIGHT)
        payoutStateContainer = Container(parent=self.reserveBankSection, align=uiconst.TOTOP, height=60, top=5)
        DescriptionIcon(parent=payoutStateContainer, align=uiconst.TOPRIGHT, tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/PayoutRate')))
        self.payoutStateSection = SubSectionAutoSize(parent=payoutStateContainer, align=uiconst.TOTOP, top=12)
        self.payoutStateSection.caption.uppercase = False
        self.payoutStateSection.mainCont.top = 5
        self.payoutStateSection.caption.top = -5
        self.ConstructPayoutStateContainer()

    def ConstructPayoutStateContainer(self):
        currentPayoutContainer = Container(name='currentPayoutContainer', parent=self.payoutStateSection, align=uiconst.TOTOP, height=18)
        dynamicResourceSettings = self.GetDynamicResourceSettings()
        self.risingPayoutFill = Fill(parent=currentPayoutContainer, align=uiconst.TOLEFT_PROP, width=dynamicResourceSettings['earlyPayoutThresholdFactor'], color=agencyConst.ESS_LOW_PAYOUT_COLOR, opacity=0.8, hint=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/RisingPayoutRate'))
        self.decreasingPayoutFill = Frame(parent=currentPayoutContainer, align=uiconst.TORIGHT_PROP, width=dynamicResourceSettings['latePayoutThresholdFactor'], texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', color=agencyConst.ESS_MEDIUM_PAYOUT_COLOR, opacity=0.8, fillCenter=True, cornerSize=9, hint=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/PayoutRateDecreasing'))
        self.peakPayoutFill = Fill(parent=currentPayoutContainer, align=uiconst.TOALL, color=agencyConst.ESS_HIGH_PAYOUT_COLOR, opacity=0.8, hint=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/PeakPayoutRate'))
        self.payoutFills = [self.risingPayoutFill, self.peakPayoutFill, self.decreasingPayoutFill]

    def GetDynamicResourceSettings(self):
        return sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()

    def UpdateBountiesOutputLabel(self, bountiesOutput):
        self.bountiesOutputLabel.SetText('%s%%' % (round(bountiesOutput, 4) * 100))

    def UpdateMainBankAmountLabel(self, bankAmount):
        self.mainBankAmountLabel.SetText('%s %s' % (FmtAmt(bankAmount), GetByLabel('UI/Wallet/WalletWindow/ISK')))
        self.mainBankAmountLabel.SetHint('%s %s' % (FmtAmt(bankAmount, fmt='sn'), GetByLabel('UI/Wallet/WalletWindow/ISK')))

    def UpdateReserveBankAmountLabel(self, bankAmount):
        self.reserveBankAmountLabel.SetText('%s %s' % (FmtAmt(bankAmount), GetByLabel('UI/Wallet/WalletWindow/ISK')))
        self.reserveBankAmountLabel.SetHint('%s %s' % (FmtAmt(bankAmount, fmt='sn'), GetByLabel('UI/Wallet/WalletWindow/ISK')))

    def UpdateActiveLinksLabel(self, activeLinks):
        self.activeLinksLabel.SetText(activeLinks)

    def UpdateReserveTimeChosenLabel(self, reserveTimeChosen, payoutState):
        if not reserveTimeChosen or payoutState == ESS_RESERVE_WINDOW_STATE_INACTIVE:
            text = '-'
        else:
            text = FmtTimeIntervalMaxParts(reserveTimeChosen * appConst.MIN, breakAt='min')
        self.reserveTimeChosenLabel.SetText(text)

    def UpdateTimeToAutoPaymentGauge(self, autopaymentWindowState):
        if autopaymentWindowState == ESS_AUTOPAY_STATE_SHORT:
            gaugeValue = 0.75
        elif autopaymentWindowState == ESS_AUTOPAY_STATE_MEDIUM:
            gaugeValue = 0.5
        else:
            gaugeValue = 0.25
        self.timeToAutoPaymentGauge.SetValueInstantly(gaugeValue)
        self.timeToAutoPaymentGauge.SetColor(ESS_TIME_TO_COLOR_MAP.get(autopaymentWindowState))
        self.timeToAutoPaymentGauge.SetText(GetByLabel(ESS_TIME_TO_LABEL_MAP[autopaymentWindowState]))

    def UpdateTimeChosenTooltip(self, timeChosen, timeFactor):
        self.timeChosenIcon.tooltipPanelClassInfo = SimpleTextTooltip(GetByLabel('UI/Agency/Tooltips/Exploration/ESS/TimeChosen', timeChosen=timeChosen / 60, timeFactor=round(timeFactor, 1)))

    def UpdatePayoutStateContainer(self, currentPayoutState):
        self.payoutStateSection.SetText(GetByLabel('UI/Agency/ESS/PayoutRate', payoutRate=GetByLabel(agencyConst.ESS_PAYOUT_STATE_TO_LABEL_MAP[currentPayoutState]), color=Color.RGBtoHex(*agencyConst.ESS_PAYOUT_STATE_TO_COLOR_MAP[currentPayoutState])))
        if currentPayoutState == ESS_RESERVE_WINDOW_STATE_INACTIVE:
            for payoutFill in self.payoutFills:
                self.DisablePayoutFill(payoutFill)

        else:
            for index, payoutFill in enumerate(self.payoutFills):
                if index + 1 != currentPayoutState:
                    self.DisablePayoutFill(payoutFill)
                else:
                    payoutFill.SetAlpha(0.6)
                    payoutFill.SetState(uiconst.UI_NORMAL)
                    animations.BlinkOut(payoutFill, startVal=0.6, endVal=0.9, duration=2.0, loops=-1, curveType=uiconst.ANIM_WAVE)

    def DisablePayoutFill(self, payoutFill):
        payoutFill.SetAlpha(0.2)
        animations.StopAllAnimations(payoutFill)
        payoutFill.SetState(uiconst.UI_DISABLED)
