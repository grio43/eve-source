#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\moonmining\outputCont.py
import evetypes
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.themeColored import LineThemeColored, FillThemeColored
from eve.client.script.ui.moonmining import GetPrice
from eve.client.script.ui.shared.ledger.ledgerUtil import GetColorForBaseTypeID
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from localization import GetByLabel
from moonmining.util import CalculateExtractionTotalYield

class SchedulingOutputPanel(Container):
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.moonMaterialInfo = attributes.moonMaterialInfo
        outputHeaderText = attributes.outputHeaderText or GetByLabel('UI/Moonmining/Output')
        EveLabelMedium(parent=self, text=outputHeaderText, align=uiconst.TOTOP)
        self.totalCont = TotalContainer(parent=self)
        self.scroll = Scroll(parent=self, id='schedulingOutputPanelScroll', padTop=4)
        self.scroll.sr.fixedColumns = MoonminingOutputEntry.GetFixedColumns()
        contentList, header = self.GetScrollContents()
        self.scroll.Load(contentList=contentList, headers=header)
        self.totalCont.UpdateColumns(self.scroll.sr.tabs)
        self.scroll.OnColumnChanged = self.OnScrollColumnChanged

    def OnScrollColumnChanged(self, tabstops, *args):
        self.totalCont.UpdateColumns(tabstops)

    def GetScrollContents(self):
        headers = [GetByLabel('UI/Moonmining/MoonProductHeader'), GetByLabel('UI/Moonmining/EstVolumeHeader'), GetByLabel('UI/Moonmining/EstPriceHeader')]
        scrollList = []
        totalWorth = 0
        worthByTypeID = {}
        for typeID, abundancy in self.moonMaterialInfo.iteritems():
            volume = abundancy * CalculateExtractionTotalYield(3600)
            units = volume / evetypes.GetVolume(typeID)
            price = GetPrice(typeID, units)
            worthByTypeID[typeID] = price
            totalWorth += price

        for typeID, abundancy in self.moonMaterialInfo.iteritems():
            data = Bunch(decoClass=MoonminingOutputEntry, estVolume=0, estPrice=0, typeID=typeID, gaugeColor=GetColorForBaseTypeID(typeID)[:3] + (0.6,), abundancy=abundancy, pricePerc=worthByTypeID.get(typeID, 0) / float(totalWorth), GetSortValue=MoonminingOutputEntry.GetSortValue)
            scrollList.append(data)

        return (scrollList, headers)

    def SetEstimation(self, numSec, yieldMultiplier):
        totalVol = 0
        totalPrice = 0
        totalYield = CalculateExtractionTotalYield(numSec, yieldMultiplier)
        for eachNode in self.scroll.GetNodes():
            percentageOfOutput = self.moonMaterialInfo.get(eachNode.typeID, None)
            estVol = percentageOfOutput * totalYield
            eachNode.estVolume = estVol
            units = estVol / evetypes.GetVolume(eachNode.typeID)
            estPrice = GetPrice(eachNode.typeID, units)
            eachNode.estPrice = estPrice
            totalVol += estVol
            totalPrice += estPrice
            if eachNode.panel:
                eachNode.panel.UpdateGauges()

        self.totalCont.SetTotals(totalVol, totalPrice)

    def GetOutputHeight(self):
        return self.scroll.GetTotalHeight() + 100


class TotalContainer(Container):
    default_align = uiconst.TOBOTTOM
    default_height = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        FillThemeColored(name='underlay', bgParent=self)
        LineThemeColored(parent=self, align=uiconst.TOLEFT_NOPUSH, name='line', opacity=uiconst.OPACITY_FRAME)
        LineThemeColored(parent=self, align=uiconst.TORIGHT_NOPUSH, name='line', opacity=uiconst.OPACITY_FRAME)
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM_NOPUSH, name='line', opacity=uiconst.OPACITY_FRAME)
        self.totalCont = Container(parent=self, align=uiconst.TOLEFT, width=100)
        EveLabelMedium(parent=self.totalCont, text=GetByLabel('UI/Moonmining/Total'), align=uiconst.CENTERLEFT, left=10)
        self.volCont = Container(parent=self, align=uiconst.TOLEFT, width=100)
        self.AddLine(self.volCont)
        self.volLabel = EveLabelMedium(parent=self.volCont, text='volCont', align=uiconst.CENTER)
        self.priceCont = Container(parent=self, align=uiconst.TOLEFT, width=100)
        self.AddLine(self.priceCont)
        line = self.AddLine(self.priceCont, align=uiconst.TORIGHT)
        line.left = -1
        self.priceLabel = EveLabelMedium(parent=self.priceCont, text='priceCont', align=uiconst.CENTER)

    def AddLine(self, parent, align = uiconst.TOLEFT):
        line = LineThemeColored(parent=parent, align=align, name='__columnLine', opacity=uiconst.OPACITY_FRAME)
        return line

    def UpdateColumns(self, tabStops):
        self.totalCont.width = tabStops[0]
        self.volCont.width = tabStops[1] - tabStops[0]
        self.priceCont.width = tabStops[2] - tabStops[1]

    def SetTotals(self, vol, price):
        self.volLabel.text = GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(vol, showFraction=False))
        self.priceLabel.text = FmtISK(price, showFractionsAlways=False)


class MoonminingOutputEntry(BaseListEntryCustomColumns):
    default_height = 40

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.BuildUI()

    def BuildUI(self):
        self.typeCont = self.AddColumnContainer()
        self.typeCont.name = 'typeCont'
        self.volumeCont = self.AddColumnContainer()
        self.volumeCont.name = 'volumeCont'
        self.priceCont = self.AddColumnContainer()
        self.priceCont.name = 'priceCont'
        self.typeIcon = Icon(name='typeIcon', parent=self.typeCont, pos=(0, 0, 32, 32), align=uiconst.CENTERLEFT)
        self.typeLabel = EveLabelMedium(name='typeLabel', parent=self.typeCont, left=40, align=uiconst.CENTERLEFT)
        self.volumeGauge = MoonminingGauge(parent=self.volumeCont, name='productGauge', value=0.0, color=(1, 1, 1, 0), pos=(5, 10, 5, 0), gradientBrightnessFactor=1.5)
        self.priceGauge = MoonminingGauge(parent=self.priceCont, name='priceGauge', value=0.0, color=(1, 1, 1, 0), pos=(5, 10, 5, 0), gradientBrightnessFactor=1.5)

    def Load(self, node):
        self.typeIcon.LoadIconByTypeID(typeID=node.typeID)
        self.typeLabel.text = evetypes.GetName(node.typeID)
        self.volumeGauge.SetValue(node.abundancy)
        self.volumeGauge.SetColor(node.gaugeColor)
        self.priceGauge.SetValue(node.pricePerc)
        self.priceGauge.SetColor(node.gaugeColor)
        self.UpdateGauges()

    def UpdateGauges(self):
        node = self.sr.node
        text = GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(node.estVolume, showFraction=False))
        self.volumeGauge.SetValueText(text)
        text = FmtISK(node.estPrice, showFractionsAlways=False)
        self.priceGauge.SetValueText(text)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.sr.node.typeID, includeMarketDetails=True)

    @classmethod
    def GetCopyData(cls, node):
        name = evetypes.GetName(node.typeID)
        volume = GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(node.estVolume, showFraction=False))
        price = FmtISK(node.estPrice, showFractionsAlways=False)
        return '<t>'.join([name, volume, price])

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Moonmining/EstVolumeHeader'): 150,
         GetByLabel('UI/Moonmining/EstPriceHeader'): 150}

    @classmethod
    def GetSortValue(cls, node, by, sortDir, idx):
        if idx == 0:
            return evetypes.GetName(node.typeID)
        if idx == 1:
            return node.abundancy
        if idx == 2:
            return node.pricePerc


class MoonminingGauge(Gauge):
    __guid__ = 'MoonminingGauge'
    default_gaugeHeight = 20
    default_align = uiconst.TOALL
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Gauge.ApplyAttributes(self, attributes)
        self.valueText = EveLabelSmall(parent=self.gaugeCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0)
        self.valueText.opacity = 1.5
        self.shadowLabel = EveLabelSmall(parent=self.gaugeCont, text='', align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=(0, 0, 0, 1), idx=1)
        self.shadowLabel.renderObject.spriteEffect = trinity.TR2_SFX_BLUR

    def SetValueText(self, text):
        Gauge.SetValueText(self, text)
        if self.shadowLabel.text != text:
            self.shadowLabel.text = text
