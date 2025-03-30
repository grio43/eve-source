#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\priceLabel.py
from collections import defaultdict
import evetypes
import eveui
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.shared.market import GetTypeIDFromDragItem
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.lib.appConst import singletonBlueprintCopy
from eve.common.script.util.eveFormat import FmtISKAndRound
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
MILLION = 1000000L
BILLION = 1000000000L

class LabelPriceLabelCont(Container):
    default_align = uiconst.TOBOTTOM
    default_height = 40

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.priceByTypeID = defaultdict(float)
        self.qtyByTypeID = defaultdict(int)
        self.label = EveLabelLarge(name='priceLabel', parent=self, align=uiconst.BOTTOMRIGHT, text='', pos=(30, 1, 0, 0), state=uiconst.UI_NORMAL)
        self.label.LoadTooltipPanel = self.LoadTooltipPanel
        cartBtn = ButtonIcon(name='cartBtn', parent=self, align=uiconst.BOTTOMRIGHT, pos=(4, 0, 24, 24), iconSize=24, texturePath='res:/UI/Texture/classes/MultiSell/multiBuy.png', hint=GetByLabel('UI/Market/MarketQuote/OpenMultiBuy'), func=self.BuyAll, uniqueUiName=pConst.UNIQUE_NAME_SHOW_BUY_ALL_BTN)
        cartBtn.OnDropData = self.OnDropOnMultibuyBtn

    @eveui.skip_if_destroyed
    def UpdateLabel(self, controller):
        fittedItems = controller.dogmaLocation.GetFittedItemsToShip()
        cargoItems = controller.dogmaLocation.GetHoldItems(const.flagCargo)
        fighterItems = controller.dogmaLocation.GetHoldItems(const.flagFighterBay)
        droneItems = controller.dogmaLocation.GetHoldItems(const.flagDroneBay)
        totalPrice = 0.0
        self.priceByTypeID.clear()
        self.qtyByTypeID.clear()
        shipItem = controller.dogmaLocation.GetShip()
        for eachDict in (fittedItems,
         cargoItems,
         fighterItems,
         droneItems):
            for itemID, dogmaItem in eachDict.iteritems():
                if itemID == session.charid:
                    continue
                if getattr(dogmaItem, 'flagID', None) == const.flagHiddenModifers:
                    continue
                if getattr(dogmaItem, 'singleton', None) == singletonBlueprintCopy:
                    continue
                typeID = dogmaItem.typeID
                stacksize = getattr(dogmaItem, 'stacksize', None) or getattr(dogmaItem.invItem, 'stacksize', 1)
                self.qtyByTypeID[typeID] += stacksize

        for typeID, qty in self.qtyByTypeID.iteritems():
            marketPrice = GetAveragePrice(typeID)
            if marketPrice:
                totalPrice += qty * marketPrice
                self.priceByTypeID[typeID] = marketPrice

        if totalPrice:
            marketPriceStr = self._FmtAmt(totalPrice)
        else:
            marketPriceStr = GetByLabel('UI/Generic/NotAvailableShort')
        self.label.text = marketPriceStr

    def _FmtAmt(self, amount):
        if amount < MILLION:
            return FmtISKAndRound(amount, showFractionsAlways=False)
        if amount > BILLION:
            amount = float(amount) / BILLION
            return GetByLabel('UI/Fitting/FittingWindow/FmtBillionIskShort', amount=amount)
        amount = float(amount) / MILLION
        return GetByLabel('UI/Fitting/FittingWindow/FmtMillionIskShort', amount=amount)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Fitting/FittingWindow/TotalEstimatedPrice', bold=True))
        tooltipPanel.AddLabelLarge(text=self.label.text, align=uiconst.CENTERRIGHT, bold=True)
        tooltipPanel.AddDivider()
        scrollcontainer = ScrollContainer(align=uiconst.TOTOP, height=100)
        tooltipPanel.AddCell(cellObject=scrollcontainer, colSpan=2)
        layoutGrid = LayoutGrid(parent=scrollcontainer, columns=4, cellSpacing=(20, 2), padTop=4)
        sortedList = [ (typeID, qty, self.priceByTypeID.get(typeID, None)) for typeID, qty in self.qtyByTypeID.iteritems() ]
        sortedList.sort(key=lambda x: x[2], reverse=True)
        for typeID, qty, price in sortedList:
            self.CreateIcon(layoutGrid, typeID)
            typeName = evetypes.GetName(typeID)
            EveLabelMedium(text=typeName, parent=layoutGrid, left=5, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERLEFT)
            EveLabelMedium(text='%sx' % qty, parent=layoutGrid, left=5, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERRIGHT)
            if price is None:
                priceText = GetByLabel('UI/Generic/NotAvailableShort')
            else:
                priceText = self._FmtAmt(price)
            EveLabelMedium(text=priceText, parent=layoutGrid, left=5, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERRIGHT)

        buttonCont = FlowContainer(name='buttonParent', align=uiconst.TOTOP, autoHeight=True, centerContent=True, contentSpacing=uiconst.BUTTONGROUPMARGIN, padTop=10)
        tooltipPanel.AddCell(cellObject=buttonCont, colSpan=2)
        Button(parent=buttonCont, label=GetByLabel('UI/Market/MarketQuote/BuyAll'), func=self.BuyAll, align=uiconst.NOALIGN)
        layoutGrid.RefreshGridLayout()
        w, h = layoutGrid.GetSize()
        scrollcontainer.height = min(h + 10, 400)
        tooltipPanel.AddSpacer(w + 20, 0, colSpan=2)

    def CreateIcon(self, parent, typeID):
        size = 32
        cont = Container(parent=parent, pos=(0,
         0,
         size,
         size), align=uiconst.CENTER)
        techIcon = Sprite(name='techIcon', parent=cont, pos=(0, 0, 16, 16))
        GetTechLevelIcon(tlicon=techIcon, typeID=typeID)
        Icon(parent=cont, typeID=typeID, size=size)

    def BuyAll(self, *args):
        return self.OpenMultiBuy(self.qtyByTypeID)

    def OpenMultiBuy(self, buyDict):
        BuyMultipleTypesWithQty(buyDict)

    def OnDropOnMultibuyBtn(self, dragObj, nodes):
        buyDict = {}
        for node in nodes:
            typeID = GetTypeIDFromDragItem(node)
            if not typeID:
                continue
            try:
                qty = int(node.extraText)
            except:
                qty = 1

            buyDict[typeID] = qty

        if buyDict:
            self.OpenMultiBuy(buyDict)
