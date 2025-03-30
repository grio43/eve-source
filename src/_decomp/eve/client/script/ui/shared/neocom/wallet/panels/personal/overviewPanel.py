#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\overviewPanel.py
import math
from carbonui.util.various_unsorted import GetWindowAbove
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.control.radioButton import RadioButton
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.control.button import Button
from eve.client.script.ui.control.donutChart import DonutChart
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium, EveCaptionLarge, EveLabelLarge, EveLabelMediumBold
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.shared.neocom.wallet.panels.personal import overviewPanelSignals
from eve.client.script.ui.shared.neocom.wallet.transactionOverviewController import TransactionOverviewController
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
MIN_SEGMENT_SIZE = 0.02
INCOME = 1
EXPENSES = 2
DONUT_RADIUS = 95
DONUT_LINEWIDTH = 15.0
DONUT_SHADOWWIDTH = 6
DONUT_SHADOWOPACITY = 0.3
COLOR_BY_REFGROUPID = {appConst.refGroupCorpAlliance: '#5c59d8',
 appConst.refGroupAgentsAndMissions: '#e68348',
 appConst.refGroupTrade: '#31c4a1',
 appConst.refGroupBounty: '#e53a3a',
 appConst.refGroupIndustry: '#3de53a',
 appConst.refGroupTransfer: '#e6e048',
 appConst.refGroupMisc: '#808080',
 appConst.refGroupHypernetRelay: '#3aa8e5'}

class OverviewPanel(Container):
    default_name = 'OverviewPanel'
    isTabStop = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isInitialized = False
        self.selectedRefGroupID = None
        overviewPanelSignals.on_entry_selected.connect(self.OnEntrySelected)
        wnd = GetWindowAbove(self)
        if wnd:
            wnd.on_start_scale.connect(self.OnWindowStartScale)
            wnd.on_end_scale.connect(self.OnWindowEndScale)

    def OnWindowEndScale(self, wnd):
        if not self.display:
            return
        animations.FadeTo(self.leftCont, self.leftCont.opacity, 1.0)
        self.ReconstructDonutChart()
        self.Update()

    def OnWindowStartScale(self, wnd):
        if not self.display:
            return
        animations.FadeTo(self.leftCont, self.leftCont.opacity, 0.0, duration=0.1)

    def OnEntrySelected(self, refGroupID):
        self.Update(refGroupID)

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.ReconstructDonutChart()
        self.Update()

    def ConstructLayout(self):
        self.rightCont = Container(name='rightCont', parent=self, align=uiconst.TORIGHT, width=200, padding=(32, 16, 0, 0))
        self.leftCont = Container(name='leftCont', parent=self, padLeft=16)
        self.backButton = Button(name='backButton', parent=self, func=self.OnBack, align=uiconst.BOTTOMRIGHT, hint=GetByLabel('UI/Commands/Back'), texturePath='res:/UI/Texture/Vgs/back.png', iconSize=16, iconPadding=8)
        self.ConstructRadioButtons()
        self.entriesCont = ScrollContainer(parent=self.rightCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padTop=8)

    def ReconstructDonutChart(self):
        self.leftCont.Flush()
        width, height = self.leftCont.GetAbsoluteSize()
        radius = min(width, height) / 2.0 * 0.9
        self.donutTransform = Transform(name='donutTransform', parent=self.leftCont, align=uiconst.CENTER, pos=(0,
         0,
         radius * 2,
         radius * 2), alignMode=uiconst.TOPLEFT, scalingCenter=(0.5, 0.5))
        self.donutChart = DonutChart(parent=self.donutTransform, radius=radius, lineWidth=DONUT_LINEWIDTH, align=uiconst.CENTER, minSegmentSize=MIN_SEGMENT_SIZE)
        self.donutChart.on_segment_clicked.connect(self.OnSegmentClicked)
        self.donutChart.on_segment_mouse_enter.connect(self.OnSegmentMouseEnter)
        self.donutChart.on_segment_mouse_exit.connect(self.OnSegmentMouseExit)
        self.donutChart.GetSegmentColor = self.GetDonutChartSegmentColor
        radius = radius + DONUT_SHADOWWIDTH
        self.donutShadowTransform = Transform(name='donutShadowTransform', parent=self.leftCont, align=uiconst.CENTER, pos=(0,
         0,
         2 * radius,
         2 * radius), alignMode=uiconst.TOPLEFT, scalingCenter=(0.5, 0.5))
        self.donutChartShadow = DonutChart(parent=self.donutShadowTransform, radius=radius, lineWidth=DONUT_SHADOWWIDTH, align=uiconst.CENTER, state=uiconst.UI_DISABLED, minSegmentSize=MIN_SEGMENT_SIZE, opacity=0.0, outputMode=uiconst.OUTPUT_GLOW)
        self.donutChartShadow.GetSegmentColor = self.GetDonutChartSegmentColor
        self.ConstructDonutLabels()

    def ConstructDonutLabels(self):
        width, _ = self.leftCont.GetAbsoluteSize()
        self.donutLabelCont = ContainerAutoSize(name='donutLabelCont', parent=self.donutTransform, align=uiconst.CENTER, width=width - 120, opacity=0.0, idx=0)
        self.donutCenterCaption = EveCaptionLarge(parent=self.donutLabelCont, align=uiconst.TOTOP, color=Color.WHITE, padBottom=6, bold=False)
        self.donutCenterTitle = EveLabelMediumBold(parent=self.donutLabelCont, align=uiconst.TOTOP, padBottom=2)
        self.donutCenterSubCaption = EveLabelMedium(parent=self.donutLabelCont, align=uiconst.TOTOP, opacity=0.5)

    def OnSegmentMouseEnter(self, segmentID):
        pass

    def OnSegmentMouseExit(self, segmentID):
        pass

    def OnSegmentClicked(self, transactionGroup):
        if not transactionGroup.refTypeID:
            self.Update(transactionGroup.refGroupID)

    def GetDonutChartSegmentColor(self, transactionGroup, value):
        if not transactionGroup:
            return (1, 1, 1, 0.1)
        if transactionGroup.refGroupID in COLOR_BY_REFGROUPID:
            color = Color.HextoRGBA(COLOR_BY_REFGROUPID[transactionGroup.refGroupID])
        if not transactionGroup.refTypeID:
            return color
        transactionGroups = [ data.segmentID for data in self.donutChart.GetSegmentData() ]
        numSegments = len(transactionGroups)
        if numSegments <= 1:
            x = 1.0
        else:
            x = 0.3 + 0.7 * transactionGroups.index(transactionGroup) / float(numSegments - 1)
        color = Color(*color)
        brightness = color.GetBrightness()
        return color.SetBrightness(x * brightness).GetRGBA()

    def OnBack(self, *args):
        if self.selectedRefGroupID:
            self.Update()

    def ConstructRadioButtons(self):
        self.incomeRadioBtn = OverviewPanelRadioButton(name='incomeRadioBtn', parent=self.rightCont, text=GetByLabel('UI/Wallet/WalletWindow/Income'), groupname='incomeOrExpensesRadioGroup', retval=INCOME, callback=self.OnIncomeExpensesRadioButton, padBottom=6)
        self.incomeRadioBtn.SetChecked(True, report=False)
        self.expensesRadioBtn = OverviewPanelRadioButton(name='expensesRadioBtn', parent=self.rightCont, text=GetByLabel('UI/Wallet/WalletWindow/Expenses'), groupname='incomeOrExpensesRadioGroup', retval=EXPENSES, callback=self.OnIncomeExpensesRadioButton, padBottom=6)

    def OnIncomeExpensesRadioButton(self, *args):
        self.Update()

    def Update(self, refGroupID = None, animate = True):
        self.selectedRefGroupID = refGroupID
        self.controller = TransactionOverviewController(self.selectedRefGroupID)
        self.UpdateDonutChart()
        self.ConstructEntries()
        self.UpdateText()
        if not refGroupID:
            self.UpdateRadioButtons()
        self.UpdateBackButtonVisibility()
        uicore.registry.SetFocus(self)
        self.AnimEntry()

    def UpdateBackButtonVisibility(self):
        if self.selectedRefGroupID is None:
            self.backButton.Hide()
            self.backButton.OnMouseExit()
        else:
            self.backButton.Show()

    def AnimEntry(self):
        duration = 0.6
        if self.selectedRefGroupID:
            startScale = (0.9, 0.9)
        else:
            startScale = (1.1, 1.1)
        animations.Tr2DScaleTo(self.donutTransform, startScale, (1.0, 1.0), duration=duration)
        animations.FadeTo(self.donutTransform, 0.0, 1.0, duration=duration)
        animations.FadeTo(self.donutLabelCont, 0.0, 1.0, duration=duration, timeOffset=1.0)
        offset = 0.2
        animations.Tr2DScaleTo(self.donutShadowTransform, (0.9, 0.9), (1.0, 1.0), duration=duration - offset, timeOffset=duration + offset)
        animations.FadeTo(self.donutChartShadow, 0.0, DONUT_SHADOWOPACITY, duration=duration - offset, timeOffset=duration + offset)

    def UpdateText(self):
        totalIncome = self.controller.GetTotalIncome()
        totalExpenses = self.controller.GetTotalExpenses()
        totalAmount = totalIncome if self.IsIncomeSelected() else totalExpenses
        text = FmtAmt(totalAmount, fmt='sn')
        self.donutCenterCaption.SetText('<center>%s</center>' % text)
        if self.IsIncomeSelected():
            subCaption = GetByLabel('UI/Wallet/WalletWindow/Last30DaysIncome')
        else:
            subCaption = GetByLabel('UI/Wallet/WalletWindow/Last30DaysExpenses')
        self.donutCenterSubCaption.SetText('<center>%s</center>' % subCaption)
        title = self.controller.GetGroupName()
        if title:
            self.donutCenterTitle.Show()
            self.donutCenterTitle.SetText('<center>%s</center>' % title)
        else:
            self.donutCenterTitle.Hide()

    def UpdateRadioButtons(self):
        totalIncome = self.controller.GetTotalIncome()
        totalExpenses = self.controller.GetTotalExpenses()
        self.incomeRadioBtn.SetISKAmount(totalIncome)
        self.expensesRadioBtn.SetISKAmount(totalExpenses)

    def ConstructEntries(self):
        self.entriesCont.Flush()
        if self.IsIncomeSelected():
            transactionGroups = self.controller.GetIncomeTransactionGroups()
            total = self.controller.GetTotalIncome()
        else:
            transactionGroups = self.controller.GetExpenditureTransactionGroups()
            total = self.controller.GetTotalExpenses()
        if transactionGroups:
            for transactionGroup in transactionGroups:
                ratio = transactionGroup.amount / total if total else 0.0
                Entry(parent=self.entriesCont, align=uiconst.TOTOP, ratio=ratio, transactionGroup=transactionGroup, color=self.GetDonutChartSegmentColor(transactionGroup, ratio), padBottom=4)

        else:
            EveLabelMedium(parent=self.entriesCont, align=uiconst.TOTOP, text=GetByLabel('UI/Wallet/WalletWindow/HintNoTransactionsFound'), padLeft=17, opacity=0.75)

    def UpdateDonutChart(self):
        if self.IsIncomeSelected():
            groups = self.controller.GetIncomeTransactionGroups()
        else:
            groups = self.controller.GetExpenditureTransactionGroups()
        self.donutChart.Reset()
        self.donutChartShadow.Reset()
        if not groups:
            self.donutChart.AddSegment(value=1.0, segmentID=None)
            self.donutChart.Disable()
            self.donutChartShadow.AddSegment(value=1.0, segmentID=None)
        else:
            self.donutChart.Enable()
            for group in groups:
                value = math.fabs(group.amount)
                self.donutChart.AddSegment(value=value, segmentID=group, hint=group.GetHint())
                self.donutChartShadow.AddSegment(value=value, segmentID=group)

        self.donutChart.Construct(animate=bool(groups))
        self.donutChartShadow.Construct(animate=False)

    def IsIncomeSelected(self):
        return self.expensesRadioBtn.GetGroupValue() == INCOME


class Entry(Container):
    default_height = 18
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(Entry, self).ApplyAttributes(attributes)
        ratio = attributes.ratio
        color = attributes.color
        self.transactionGroup = attributes.transactionGroup
        self.label = Label(parent=self, align=uiconst.CENTERLEFT, text='%.1f%% %s' % (100 * ratio, self.transactionGroup.name), state=uiconst.UI_DISABLED, color=(1, 1, 1, 1), left=18)
        gauge = Fill(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, color=color, pos=(2, 0, 10, 10))
        self.underlay = ListEntryUnderlay(bgParent=self)

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(Entry, self).UpdateAlignment(*args, **kwargs)
        return alignment

    def GetHint(self):
        return FmtISK(self.transactionGroup.amount)

    def OnClick(self, *args):
        if not self.transactionGroup.refTypeID:
            overviewPanelSignals.on_entry_selected(self.transactionGroup.refGroupID)

    def OnMouseEnter(self, *args):
        self.underlay.hovered = True

    def OnMouseExit(self, *args):
        self.underlay.hovered = False


class OverviewPanelRadioButton(RadioButton):

    def ConstructLabel(self):
        super(OverviewPanelRadioButton, self).ConstructLabel()
        self.iskLabel = EveLabelLarge(parent=self, align=uiconst.TOPLEFT, left=self.label.left, top=20)

    def SetISKAmount(self, amount):
        text = FmtISK(amount)
        if amount >= 0:
            text = '+' + text
        self.iskLabel.SetText(text)
