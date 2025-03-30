#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\resourceConts.py
import carbonui
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gauge import GaugeMultiValue
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from localization import GetByLabel
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE

class BaseResourceCont(ContainerAutoSize):
    headerPath = 'UI/Sovereignty/Resource'
    headerHintPath = 'Tooltips/StructureUI/ResourceMax'
    inUseHintPath = 'Tooltips/StructureUI/ResourceInUse'
    availableHintPath = 'Tooltips/StructureUI/ResourceInUse'
    maxHintPath = 'Tooltips/StructureUI/ResourceMax'
    default_minHeight = 40
    default_align = carbonui.Align.TOTOP
    default_alignMode = carbonui.Align.TOTOP
    default_gaugeHeight = 4
    default_useLegend = True
    default_isCompact = False
    gaugeOverlay = None

    def ApplyAttributes(self, attributes):
        self.legendCont = None
        self.threadedLoader = ThreadedLoader('BaseResourceCont')
        super(BaseResourceCont, self).ApplyAttributes(attributes)
        self.useLegend = attributes.Get('useLegend', self.default_useLegend)
        self.isCompact = attributes.Get('isCompact', self.default_isCompact)
        self.controller = attributes.controller
        self.gaugeHeight = attributes.Get('gaugeHeight', self.default_gaugeHeight)
        self.ConstructUI()

    def ConstructUI(self):
        header = carbonui.TextDetail(parent=self, text=GetByLabel(self.headerPath), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, pickState=carbonui.PickState.ON)
        header.hint = GetByLabel(self.headerHintPath)
        valueCont = Container(parent=self, align=carbonui.Align.TOTOP, height=30)
        self.valueGrid = LayoutGrid(parent=valueCont, columns=4, cellSpacing=10)
        if self.isCompact:
            inUseClass = carbonui.TextBody
            topOffset = 0
        else:
            inUseClass = carbonui.TextHeadline
            topOffset = 2
        self.inUseLabel = inUseClass(parent=self.valueGrid, text='', align=carbonui.Align.BOTTOMLEFT, pickState=carbonui.PickState.ON)
        self.inUseLabel.hint = GetByLabel(self.inUseHintPath)
        carbonui.TextBody(parent=self.valueGrid, text='/', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.BOTTOMLEFT, top=topOffset)
        self.totalLabel = carbonui.TextBody(parent=self.valueGrid, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.BOTTOMLEFT, top=topOffset, pickState=carbonui.PickState.ON)
        self.totalLabel.hint = GetByLabel(self.availableHintPath)
        self.extraInfo = carbonui.TextBody(parent=self.valueGrid, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.BOTTOMLEFT, top=topOffset, pickState=carbonui.PickState.ON)
        self.extraInfo.OnMouseEnter = lambda *args: self.controller.on_legend_moused_over(True, 'extraInfoLabel')
        self.extraInfo.OnMouseExit = lambda *args: self.controller.on_legend_moused_over(False, 'extraInfoLabel')
        self.maxLabel = carbonui.TextBody(parent=valueCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.BOTTOMRIGHT, top=2, pickState=carbonui.PickState.ON)
        self.maxLabel.hint = GetByLabel(self.maxHintPath)
        self.overlayCont = Container(parent=self, align=carbonui.Align.TOTOP_NOPUSH, height=self.gaugeHeight)
        self.gauge = GaugeMultiValue(parent=self, colors=(eveColor.SMOKE_BLUE, eveColor.CRYO_BLUE, eveColor.LEAFY_GREEN), values=(0.0, 0.0), align=carbonui.Align.TOTOP, gaugeHeight=self.gaugeHeight)
        if self.useLegend:
            self.legendCont = Legend(parent=self, legendHints=self.GetLegendHints(), controller=self.controller)
        self.controller.on_legend_moused_over.connect(self.OnLegendMousedOver)

    def LoadContAsync(self, *args):
        self.threadedLoader.StartLoading(self.LoadCont, self)

    def LoadCont(self, *args):
        self.SetText()
        self.SetTotalText()
        self.SetMaxText()
        self.SetGauge()
        self.SetLegend()

    def SetGauge(self):
        pass

    def SetText(self):
        pass

    def SetTotalText(self):
        pass

    def SetMaxText(self):
        pass

    def SetLegend(self):
        pass

    def GetLegendHints(self):
        return {}

    def OnLegendMousedOver(self, enter, legendType):
        pass

    def Close(self):
        self.threadedLoader = None
        super(BaseResourceCont, self).Close()


class PowerCont(BaseResourceCont):
    headerPath = 'UI/Sovereignty/Power'
    headerHintPath = 'Tooltips/StructureUI/SovHubPowerWidgetHeader'
    inUseHintPath = 'Tooltips/StructureUI/SovHubPowerAllocated'
    availableHintPath = 'Tooltips/StructureUI/SovHubAvailablePower'
    maxHintPath = 'Tooltips/StructureUI/SovHubTotalPowerPotential'

    def SetGauge(self):
        power = self.controller.GetPowerAllocated()
        if power == DATA_NOT_AVAILABLE:
            inUsePercentage = 0
            available = 0
        else:
            inUsePercentage = float(power) / self.controller.maxPower
            available = float(self.controller.GetAvailablePower()) / self.controller.maxPower
        self.gauge.SetValue(0, inUsePercentage)
        self.gauge.SetValue(1, available)

    def SetText(self):
        power = self.controller.GetPowerAllocatedText()
        self.inUseLabel.text = power

    def SetTotalText(self):
        self.totalLabel.text = self.controller.GetAvailablePowerText()

    def SetMaxText(self):
        self.maxLabel.text = FmtAmt(self.controller.maxPower)

    def SetLegend(self):
        if self.legendCont:
            power = self.controller.GetPowerAllocated()
            if power == DATA_NOT_AVAILABLE:
                self.legendCont.SetLegendValues(0, 0, 0)
            else:
                freePower = self.controller.GetAvailablePower() - power
                lowStatePower = self.controller.GetPowerLowStateUpgrades()
                self.legendCont.SetLegendValues(power, freePower, lowStatePower, None)

    def GetLegendHints(self):
        return {'inUse': GetByLabel('Tooltips/StructureUI/SovHubPowerBarAllocated'),
         'total': GetByLabel('Tooltips/StructureUI/SovHubPowerBarAvailable'),
         'lowState': GetByLabel('Tooltips/StructureUI/SovHubPowerBarMissingPower')}


class WorkforceCont(BaseResourceCont):
    headerPath = 'UI/Sovereignty/Workforce'
    headerHintPath = 'Tooltips/StructureUI/SovHubWorkforceWidgetHeader'
    inUseHintPath = 'Tooltips/StructureUI/SovHubWorkforceBarAllocated'
    availableHintPath = 'Tooltips/StructureUI/SovHubAvailableWorkforce'
    maxHintPath = 'Tooltips/StructureUI/SovHubTotalWorkforcePotential'

    def SetGauge(self):
        workforce = self.controller.GetWorkforce()
        maxWorkforceInSystem = self.controller.maxWorkforce
        if workforce == DATA_NOT_AVAILABLE or not maxWorkforceInSystem:
            inUsePercentage = 0
            available = 0
            exportedPercentage = 0
        else:
            importedValue = self.controller.GetImportedValue()
            exportedValue = self.controller.GetExportedValue()
            maxWorkforceInSystem += importedValue
            inUsePercentage = float(workforce) / maxWorkforceInSystem
            exportedPercentage = float(exportedValue) / maxWorkforceInSystem
            available = float(self.controller.GetAvailableWorkforce()) / maxWorkforceInSystem
        self.gauge.SetValue(0, inUsePercentage)
        self.gauge.SetValue(1, available)
        self.gauge.SetValue(2, available + exportedPercentage)

    def SetText(self):
        self.inUseLabel.text = self.controller.GetWorkforceText()

    def SetTotalText(self):
        self.totalLabel.text = self.controller.GetAvailableBaseWorkforceText()
        text, hint = self.controller.GetImportedValueTextAndHint()
        self.extraInfo.text = text
        self.extraInfo.hint = hint

    def SetMaxText(self):
        self.maxLabel.text = FmtAmt(self.controller.maxWorkforce)

    def SetLegend(self):
        workforce = self.controller.GetWorkforce()
        if workforce != DATA_NOT_AVAILABLE:
            freeWorkforce = self.controller.GetAvailableWorkforce() - workforce
            lowStateWorkforce = self.controller.GetWorkforceLowStateUpgrades()
            exported = self.controller.GetExportedValue()
            if self.legendCont:
                self.legendCont.SetLegendValues(workforce, freeWorkforce, lowStateWorkforce, exported)

    def GetLegendHints(self):
        return {'inUse': GetByLabel('Tooltips/StructureUI/SovHubWorkforceBarAllocated'),
         'total': GetByLabel('Tooltips/StructureUI/SovHubWorkforceBarAvailable'),
         'lowState': GetByLabel('Tooltips/StructureUI/SovHubWorkforceBarMissingPower'),
         'extraInfo': GetByLabel('Tooltips/StructureUI/SovHubWorkforceBarExported')}

    def OnLegendMousedOver(self, enter, legendType):
        if legendType == 'extraInfoLabel':
            if enter:
                availableWorkforce = self.controller.GetAvailableWorkforce()
                imported = self.controller.GetImportedValue()
                availableWithoutImported = availableWorkforce - imported
                self.ConstructGaugeOverlay()
                self.gaugeOverlay.Show()
                maxWorkforceInSystem = self.controller.maxWorkforce
                maxWorkforceInSystem += imported
                self.gaugeOverlay.left = float(availableWithoutImported) / maxWorkforceInSystem
                self.gaugeOverlay.width = float(imported) / maxWorkforceInSystem
            elif self.gaugeOverlay:
                self.gaugeOverlay.Hide()

    def ConstructGaugeOverlay(self):
        if self.gaugeOverlay is None or self.gaugeOverlay.destroyed:
            self.gaugeOverlay = Fill(parent=self.overlayCont, align=carbonui.Align.TOLEFT_PROP, idx=0, color=eveColor.SUCCESS_GREEN, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)


class Legend(Container):
    default_name = 'legendCont'
    default_height = 30
    default_top = 7
    default_align = carbonui.Align.TOTOP

    def ApplyAttributes(self, attributes):
        super(Legend, self).ApplyAttributes(attributes)
        legendHints = attributes.legendHints
        self.controller = attributes.controller
        FILL_SIZE = 8
        legendGrid = LayoutGrid(parent=self, columns=6, cellSpacing=10)
        cont = ContainerAutoSize(parent=legendGrid, align=carbonui.Align.CENTERLEFT, pickState=carbonui.PickState.ON)
        f = Fill(parent=cont, pos=(0,
         0,
         FILL_SIZE,
         FILL_SIZE), align=carbonui.Align.CENTERLEFT, color=eveColor.SMOKE_BLUE)
        self.inUseLegendLabel = carbonui.TextDetail(parent=cont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERLEFT, left=16)
        cont.hint = legendHints.get('inUse', '')
        cont = ContainerAutoSize(parent=legendGrid, align=carbonui.Align.CENTERLEFT, pickState=carbonui.PickState.ON, left=20)
        f = Fill(parent=cont, pos=(0,
         0,
         FILL_SIZE,
         FILL_SIZE), align=carbonui.Align.CENTERLEFT, color=eveColor.CRYO_BLUE)
        self.availableLegendLabel = carbonui.TextDetail(parent=cont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERLEFT, left=16)
        cont.hint = legendHints.get('total', '')
        self.lowStateCont = ContainerAutoSize(parent=legendGrid, align=carbonui.Align.CENTERLEFT, pickState=carbonui.PickState.ON, left=20)
        self.lowStateLegend = Fill(parent=self.lowStateCont, pos=(0,
         0,
         FILL_SIZE,
         FILL_SIZE), align=carbonui.Align.CENTERLEFT, color=eveColor.DANGER_RED)
        self.lowStateLabel = carbonui.TextDetail(parent=self.lowStateCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERLEFT, left=16)
        self.lowStateCont.hint = legendHints.get('lowState', '')
        self.lowStateCont.display = False
        self.lowStateCont.OnMouseEnter = lambda *args: self.controller.on_legend_moused_over(True, 'low')
        self.lowStateCont.OnMouseExit = lambda *args: self.controller.on_legend_moused_over(False, 'low')
        self.extraInfoCont = ContainerAutoSize(parent=legendGrid, align=carbonui.Align.CENTERLEFT, pickState=carbonui.PickState.ON, left=20)
        self.extraInfoLegend = Fill(parent=self.extraInfoCont, pos=(0,
         0,
         FILL_SIZE,
         FILL_SIZE), align=carbonui.Align.CENTERLEFT, color=eveColor.LEAFY_GREEN)
        self.extraLabel = carbonui.TextDetail(parent=self.extraInfoCont, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.CENTERLEFT, left=16)
        self.extraInfoCont.hint = legendHints.get('extraInfo', '')
        self.extraInfoCont.display = False
        self.extraInfoCont.OnMouseEnter = lambda *args: self.controller.on_legend_moused_over(True, 'extra')
        self.extraInfoCont.OnMouseExit = lambda *args: self.controller.on_legend_moused_over(False, 'extra')

    def SetLegendValues(self, inUse, available, lowState, exported = None):
        self.inUseLegendLabel.text = inUse
        self.availableLegendLabel.text = available
        if lowState:
            self.lowStateCont.display = True
            self.lowStateLabel.text = lowState
            self.lowStateLegend.display = True
        else:
            self.lowStateLabel.text = ''
            self.lowStateLegend.display = False
        if exported:
            self.extraInfoCont.display = True
            self.extraLabel.text = exported
            self.extraInfoLegend.display = True
        else:
            self.extraLabel.text = ''
            self.extraInfoLegend.display = False
