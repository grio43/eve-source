#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\buySellMultiBase.py
import math
import eveformat
import evelink.client
from carbon.common.script.util.format import FmtAmt
from carbonui import TextColor, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from carbonui.control.window import Window
from eve.client.script.ui.shared.market.accessControl import MarketAccessControl
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_MARKET_ORDER_DURATION
from eve.common.lib.appConst import corpRoleAccountant, corpRoleTrader
import evetypes
from localization import GetByLabel
import uthread
from carbonui.uicore import uicore
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
COL_GREEN = (0.3, 0.9, 0.1)
COL_RED = (1.0, 0.275, 0.0)
COL_WHITE = (1.0, 1.0, 1.0)

class SellBuyItemsWindow(Window):
    __notifyevents__ = ['OnSessionChanged']
    default_width = 520
    default_height = 390
    default_minSize = (default_width, default_height)
    default_windowID = 'SellBuyItemsWindow'
    captionTextPath = 'UI/Inventory/ItemActions/MultiBuy'
    scrollId = 'MultiBuyScroll'
    tradeForCorpSettingConfig = 'buyUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandSell'
    orderCap = 'MultiSellOrderCap'
    tradeOnConfirm = True
    corpCheckboxTop = 38
    numbersGridTop = 6
    dropLabelPath = 'UI/Market/Marketbase/DropItemsToAdd'
    cannotBeTradeLabelPath = 'UI/Market/MarketQuote/CannotBeSold'
    badDeltaWarningPath = 'UI/Market/MarketQuote/MultiBuyTypesAboveAverage'
    salesTaxToolTipHeaderLabelPath = 'UI/Market/MarketQuote/SalesTaxTooltipHeader'
    salesTaxToolTipDescriptionLabelPath = 'UI/Market/MarketQuote/SalesTaxTooltipDescription'
    brokersFeeTooltipHeaderLabelPath = 'UI/Market/MarketQuote/BrokersFeeTooltipHeader'
    brokersFeeTooltipDescriptionLabelPath = 'UI/Market/MarketQuote/BrokersFeeTooltipDescription'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.isReadOnly = MarketAccessControl().is_sell_items_read_only
        self.marketQuoteSvc = sm.GetService('marketQuote')
        self.InitializeVariables(attributes)
        self.SetCaption(GetByLabel(self.captionTextPath))
        self.scope = uiconst.SCOPE_INGAME
        self.mainCont = mainCont = Container(parent=self.sr.main, name='mainCont')
        self.infoCont = Container(parent=mainCont, name='infoCont', align=uiconst.TOBOTTOM, height=92)
        self.bottomLeft = Container(parent=self.infoCont, name='bottomLeft', align=uiconst.TOLEFT, width=250, state=uiconst.UI_PICKCHILDREN, uniqueUiName=UNIQUE_NAME_MARKET_ORDER_DURATION)
        self.bottomRight = Container(parent=self.infoCont, name='bottomRight', align=uiconst.TORIGHT, width=250)
        self.dropCont = Container(name='dropCont', parent=mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=32)
        self.dropLabel = EveCaptionSmall(parent=self.dropCont, align=uiconst.CENTER, text=GetByLabel(self.dropLabelPath), color=TextColor.SECONDARY)
        self.fakeItemsCont = Container(parent=self.dropCont, align=uiconst.TOALL, clipChildren=True)
        self.locationCont = Container(parent=mainCont, name='locationCont', align=uiconst.TOTOP)
        self.scrollCont = Container(parent=mainCont, name='scrollCont', padding=(0, 8, 0, 8))
        self.itemsScroll = ScrollContainer(parent=self.scrollCont, id=self.scrollId)
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0, line=False)
        self.tradeButton = self.btnGroup.AddButton(GetByLabel(self.tradeTextPath), self.PerformTrade, isDefault=self.tradeOnConfirm, uiName='confirm_sell_button')
        self.btnGroup.AddButton(GetByLabel('UI/Generic/Cancel'), self.Cancel, uiName='cancel_sell_button')
        self.DrawNumbers()
        corpAcctName = self._CanTradeForCorp()
        if corpAcctName is not None:
            self.DrawCheckBox(corpAcctName)
        self.globalDragHover = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)

    def StartAddItemsThread(self):
        if len(self.preItems):
            self.addItemsThread = uthread.new(self.AddPreItems, self.preItems)

    def InitializeVariables(self, attributes):
        self.globalDragHover = None
        self.cannotTradeItemList = []
        self.itemList = []
        self.preItems = attributes.preItems or []
        self.useCorp = None
        self.hasDrawn = False
        self.addItemsThread = None
        self.baseStationID = None

    def DrawNumbers(self):
        pass

    def SetupBrokersFeeTooltips(self):
        SetTooltipHeaderAndDescription(self.brokersFee, GetByLabel(self.brokersFeeTooltipHeaderLabelPath), GetByLabel(self.brokersFeeTooltipDescriptionLabelPath))
        SetTooltipHeaderAndDescription(self.brokersFeeAmt, GetByLabel(self.brokersFeeTooltipHeaderLabelPath), GetByLabel(self.brokersFeeTooltipDescriptionLabelPath))

    def SetupSalesTaxTooltips(self):
        SetTooltipHeaderAndDescription(self.salesTax, GetByLabel(self.salesTaxToolTipHeaderLabelPath), GetByLabel(self.salesTaxToolTipDescriptionLabelPath))
        SetTooltipHeaderAndDescription(self.salesTaxAmt, GetByLabel(self.salesTaxToolTipHeaderLabelPath), GetByLabel(self.salesTaxToolTipDescriptionLabelPath))

    def DrawCheckBox(self, corpAcctName):
        useCorpWallet = settings.user.ui.Get(self.tradeForCorpSettingConfig, False)
        top = self.corpCheckboxTop
        self.useCorp = Checkbox(text=GetByLabel('UI/Market/MarketQuote/UseCorpAccount', accountName=corpAcctName), parent=self.bottomLeft, settingsKey='usecorp', checked=useCorpWallet, callback=self.OnUseCorp, pos=(0,
         top,
         350,
         0), align=uiconst.TOPLEFT)

    def _CanTradeForCorp(self):
        if session.corprole & (corpRoleAccountant | corpRoleTrader):
            corpAcctName = sm.GetService('corp').GetMyCorpAccountName()
            if corpAcctName is not None:
                return corpAcctName

    def OnUseCorp(self, *args):
        if self.useCorp.checked:
            newValue = True
        else:
            newValue = False
        settings.user.ui.Set(self.tradeForCorpSettingConfig, newValue)
        self.UpdateNumbers()

    def TradingForCorp(self):
        if self.useCorp:
            useCorp = self.useCorp.checked
        else:
            useCorp = False
        return useCorp

    def DropItems(self, dragObj, nodes):
        pass

    def PerformTrade(self, *args):
        pass

    def UpdateNumbers(self):
        pass

    def GetItems(self):
        return self.itemList

    def AddPreItems(self, preItems):
        pass

    def IsAllowedDragData(self, dragData):
        return True

    def DrawDraggedItems(self, dragData):
        if not self.IsAllowedDragData(dragData):
            return
        self.hasDrawn = True
        uicore.animations.FadeOut(self.dropLabel, duration=0.15)
        noOfItems = len(dragData)
        noOfAvailable = math.floor((self.width - 16 - self.dropCont.padLeft - self.dropCont.padRight) / 28)
        for i, dragItem in enumerate(dragData):
            c = Container(parent=self.fakeItemsCont, align=uiconst.TOLEFT, padding=2, width=24)
            if noOfItems > noOfAvailable and i == noOfAvailable - 1:
                icon = Sprite(parent=c, texturePath='res:/UI/Texture/classes/MultiSell/DotDotDot.png', state=uiconst.UI_DISABLED, width=24, height=24, align=uiconst.CENTER)
                icon.SetAlpha(0.6)
                return
            typeID = self.GetTypeIDFromDragItem(dragItem)
            icon = Icon(parent=c, typeID=typeID, state=uiconst.UI_DISABLED)
            icon.SetSize(24, 24)

    def GetTypeIDFromDragItem(self, dragItem):
        getTypeID = dragItem.item.typeID
        return getTypeID

    def OnDropData(self, dragSource, dragData):
        self.ClearDragData()

    def ClearDragData(self):
        self.fakeItemsCont.Flush()
        uicore.animations.FadeIn(self.dropLabel, 0.6, duration=0.3)
        self.hasDrawn = False

    def OnGlobalMouseHover(self, *args, **kw):
        shouldClearDragData = True
        if uicore.IsDragging() and uicore.dragObject:
            mo = uicore.uilib.mouseOver
            if mo == self or mo.IsUnder(self):
                shouldClearDragData = False
                if not self.hasDrawn:
                    self.DrawDraggedItems(uicore.dragObject.dragData)
        if shouldClearDragData:
            self.ClearDragData()
        return True

    def Cancel(self, *args):
        self.Close()

    def Close(self, *args, **kwds):
        Window.Close(self, *args, **kwds)
        if self.addItemsThread:
            self.addItemsThread.kill()
        uicore.event.UnregisterForTriuiEvents(self.globalDragHover)

    def CheckOrderAvailability(self, preItems):
        availableOrders = int(sm.GetService('machoNet').GetGlobalConfig().get(self.orderCap, 100)) - len(self.itemList)
        if len(preItems) > availableOrders:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/TooManyItemsForOrder')})
            return preItems[:availableOrders]
        return preItems

    def RemoveItem(self, itemEntry):
        self.itemsScroll._RemoveChild(itemEntry)
        self.itemList.remove(itemEntry)
        self.RemoveItemFromCollection(itemEntry)
        self.UpdateNumbers()
        self.UpdateHeaderCount()

    def RemoveItemFromCollection(self, itemEntry):
        pass

    def DoAddItem(self, item):
        itemEntry = self.GetItemEntry(item)
        self.AddItemToCollection(item, itemEntry)
        itemEntry.state = uiconst.UI_NORMAL
        self.itemsScroll._InsertChild(0, itemEntry)
        self.itemList.append(itemEntry)
        self.UpdateNumbers()
        self.UpdateHeaderCount()
        return itemEntry

    def UpdateHeaderCount(self):
        self.SetCaption('%s (%i) - %s' % (GetByLabel(self.captionTextPath), len(self.itemList), self.GetStationLocationText()))

    def GetStationLocationText(self):
        if self.baseStationID is None:
            return ''
        stationLocation = cfg.evelocations.Get(self.baseStationID).locationName
        return stationLocation

    def DisplayErrorHints(self):
        hintTextList = self.GetErrorHints()
        if hintTextList:
            hintText = '<br>'.join(hintTextList)
            eve.Message('CustomNotify', {'notify': hintText})

    def GetErrorHints(self):
        hintTextList = self.BuildHintTextList(self.cannotTradeItemList, self.cannotBeTradeLabelPath)
        return hintTextList

    def BuildHintTextList(self, itemList, labelPath):
        hintTextList = []
        if len(itemList):
            hintTextList.append(eveformat.bold(GetByLabel(labelPath)))
            for item in itemList:
                hintTextList.append(evelink.type_link(type_id=item.typeID))

        return hintTextList

    def ClearErrorLists(self):
        self.cannotTradeItemList = []

    def GetValidatedItem(self, item):
        return None

    def GetItemsIterator(self, onlyValid = False):
        for item in self.GetItems():
            if not item:
                continue
            if onlyValid and not self.GetValidatedItem(item):
                continue
            yield item

    def GetOrderDeltaTextForWarning(self):
        return ''

    def GetItemsWithBadDelta(self, args):
        return []

    def ContinueAfterWarning(self, buyItemList):
        highItems = self.GetItemsWithBadDelta(buyItemList)
        orderText = self.GetOrderDeltaTextForWarning()
        hightText = ''
        if highItems:
            highTextList = [GetByLabel(self.badDeltaWarningPath)]
            highItems.sort(key=lambda x: x[0], reverse=True)
            for perc, item in highItems:
                percText = GetByLabel('UI/Common/Percentage', percentage=FmtAmt(perc * 100, showFraction=0))
                highTextList.append('- %s (%s)' % (evetypes.GetName(item.typeID), percText))

            hightText = '<br>'.join(highTextList)
        if orderText or hightText:
            warningTextList = []
            if orderText:
                warningTextList.append(orderText)
                warningTextList.append('')
            if hightText:
                warningTextList.append(hightText)
                warningTextList.append('')
            warningTextList.append(GetByLabel('UI/Market/MarketQuote/MultiBuyAboveAverageConfirmation'))
            warningText = '<br>'.join(warningTextList)
            headerLabel = GetByLabel('UI/Generic/Warning')
            ret = eve.Message('CustomQuestion', {'header': headerLabel,
             'question': warningText}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return False
        return True
