#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\sellMulti.py
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui import const as uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium, EveLabelMediumBold, EveLabelLargeBold
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.market import INVENTORY_GUIDS
from eve.client.script.ui.shared.market.buySellMultiBase import SellBuyItemsWindow, COL_RED, COL_GREEN, COL_WHITE
from eve.client.script.ui.shared.market.sellItemEntry import SellItemContainer
from eve.client.script.ui.util.qtyTooltipUtil import AssignQtyTooltipFunc
from eve.client.script.ui.services.menuSvcExtras.invItemFunctions import CheckRepackageItems
from eve.common.script.sys.idCheckers import IsStation
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError
from inventorycommon import const as invconst
from inventorycommon.const import flagCorpSAGs, flagHangar
from localization import GetByLabel
import uthread
from marketutil.const import MAX_ORDER_PRICE
from menucheckers import ItemChecker
from menucheckers.sessionChecker import SessionChecker
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_FLOAT
import uthread2
from vgs.common.listeners import PlexWithdrawalListener
from utillib import KeyVal
from carbonui.uicore import uicore
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription

class SellItems(SellBuyItemsWindow):
    default_windowID = 'SellItemsWindow'
    default_name = 'SellItems'
    default_iconNum = 'res:/ui/Texture/WindowIcons/market.png'
    captionTextPath = 'UI/Inventory/ItemActions/MultiSell'
    scrollId = 'MultiSellScroll'
    durationSettingConfig = 'multiSellDuration'
    tradeForCorpSettingConfig = 'sellUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandSell'
    orderCap = 'MultiSellOrderCap'
    badDeltaWarningPath = 'UI/Market/MarketQuote/MultiSellTypesBelowAverage'
    salesButtonCantAffordBrokersFeeTooltipHeaderLabelPath = 'UI/Market/MarketQuote/SalesButtonCantAffordBrokersFeeTooltipHeader'
    salesButtonCantAffordBrokersFeeDescriptionLabelPath = 'UI/Market/MarketQuote/SalesButtonCantAffordBrokersFeeTooltipDescription'

    def __init__(self, **kwargs):
        self.orderCountLabel = None
        self.maxCount = None
        self.myOrderCount = None
        self.itemDict = {}
        self.sellItemList = None
        self.itemAlreadyInList = None
        self.baseStationID = None
        self.durationCombo = None
        self.errorItemList = None
        self.itemsNeedRepackaging = []
        super(SellItems, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        super(SellItems, self).ApplyAttributes(attributes)
        top = 62 if self.useCorp else 44
        self.orderCountLabel = EveLabelSmall(parent=self.bottomLeft, top=top, left=2)
        self.maxCount = self.GetMaxOrderCount()
        self.myOrderCount = self.GetCurrentOrderCount()
        self.UpdateOrderCount()
        self.DrawDurationCombo()
        self.StartAddItemsThread()

    def InitializeVariables(self, attributes):
        SellBuyItemsWindow.InitializeVariables(self, attributes)
        self.itemDict = {}
        self.sellItemList = []
        self.itemAlreadyInList = []
        self.itemsNeedRepackaging = []

    def DrawNumbers(self):
        self.numbersGrid = LayoutGrid(parent=self.bottomRight, columns=2, align=uiconst.TORIGHT, top=self.numbersGridTop, state=uiconst.UI_PICKCHILDREN)
        self.sccRow = self.numbersGrid.AddRow(name='sccRow')
        self.sccSurchargeLabel = EveLabelMedium(parent=self.sccRow, text='', padRight=4, state=uiconst.UI_NORMAL)
        self.sccSurchargeAmtLabel = EveLabelMediumBold(parent=self.sccRow, text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.brokersFee = EveLabelMedium(text='', padRight=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.brokersFee)
        self.brokersFeeAmt = EveLabelMediumBold(text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.brokersFeeAmt)
        self.salesTax = EveLabelMedium(text='', padRight=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.salesTax)
        self.salesTaxAmt = EveLabelMediumBold(text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.salesTaxAmt)
        self.SetupSalesTaxTooltips()
        self.SetupBrokersFeeTooltips()
        spacer = Container(align=uiconst.TOTOP, height=12)
        self.numbersGrid.AddCell(spacer, colSpan=2)
        self.totalAmt = EveLabelLargeBold(text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.totalAmt, colSpan=2)

    def AddPreItems(self, preItems):
        itemLocations = set([])
        preItems = self.CheckOrderAvailability(preItems)
        for item in preItems:
            itemStationID = sm.GetService('invCache').GetStationIDOfItem(item)
            itemLocations.add(itemStationID)

        if len(itemLocations) > 1:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/AddingFromDifferentLocations')})
            return
        for item in preItems:
            if self.CheckItemLocation(item):
                self.AddItem(item)

    def CheckItemLocation(self, item):
        if not self.CheckStation(item) and len(self.itemList) > 0:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/LocationNotShared')})
            return False
        if item.flagID not in flagCorpSAGs + (flagHangar,):
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/NotValidLocation')})
            return False
        return True

    def GetErrorHints(self):
        hintTextList = SellBuyItemsWindow.GetErrorHints(self)
        alreadyInList = self.BuildHintTextList(self.itemAlreadyInList, 'UI/Market/MarketQuote/AlreadyInList')
        if hintTextList and alreadyInList:
            hintTextList.append('')
        hintTextList += alreadyInList
        needsRepackaging = self.BuildHintTextList(self.itemsNeedRepackaging, 'UI/Market/MarketQuote/NeedsRepackaging')
        if hintTextList and needsRepackaging:
            hintTextList.append('')
        hintTextList += needsRepackaging
        return hintTextList

    def AddItems(self, items):
        self.ClearErrorLists()
        items = self.CheckOrderAvailability(items)
        sellItems = []
        OkWithDumpingStuff = None
        for item in items:
            if item.singleton and cfg.IsContainer(item):
                try:
                    itemsInside = {i for i in sm.GetService('invCache').GetInventoryFromId(item.itemID).List() if i.flagID != invconst.flagHiddenModifers}
                except UserError:
                    continue

                if itemsInside:
                    if item.categoryID == invconst.categoryShip:
                        rigs = {i for i in itemsInside if const.flagRigSlot0 <= i.flagID <= const.flagRigSlot7}
                        if rigs:
                            self.itemsNeedRepackaging.append(item)
                            continue
                    if OkWithDumpingStuff is None:
                        if eve.Message('RepackageContainers', {}, uiconst.YESNO) != uiconst.ID_YES:
                            OkWithDumpingStuff = False
                            continue
                        OkWithDumpingStuff = True
                    if OkWithDumpingStuff is False:
                        continue
            sellItems.append(item)

        sellItems = CheckRepackageItems(sellItems, OkWithDumpingStuff is None)
        for item in sellItems:
            self.AddItem(item)

        self.DisplayErrorHints()

    def AddItem(self, item):
        if not self.IsSellable(item):
            return
        self.itemDict[item.itemID] = item
        itemEntry = self.DoAddItem(item)
        if len(self.itemList) == 1:
            self.UpdateStationInfo(itemEntry.stationID)
        self.CheckItemSize()
        uicore.registry.SetFocus(itemEntry.priceEdit)

    def GetItemEntry(self, item):
        solarSystemID = self._GetSolarSystemIDForItem(item)
        marketQuote = sm.GetService('marketQuote')
        bestPrice = marketQuote.GetBestPrice(item.typeID, item, item.stacksize, solarSystemID)
        bestBid = marketQuote.GetBestBidWithStationID(item, locationID=solarSystemID)
        stationID = sm.GetService('invCache').GetStationIDOfItem(item)
        itemEntry = SellItemContainer(item=item, editFunc=self.OnEntryEdit, align=uiconst.TOTOP, parentFunc=self.RemoveItem, bestPrice=bestPrice, bestBid=bestBid, stationID=stationID, solarSystemID=solarSystemID, isReadOnly=self.isReadOnly)
        return itemEntry

    @staticmethod
    def _GetSolarSystemIDForItem(item):
        if IsStation(item.locationID):
            station = sm.StartService('ui').GetStationStaticInfo(item.locationID)
            return station.solarSystemID
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(item.locationID)
        if structureInfo and structureInfo.solarSystemID:
            return structureInfo.solarSystemID
        return session.solarsystemid2

    def AddItemToCollection(self, item, itemEntry):
        self.itemDict[item.itemID] = item

    def CheckItemSize(self):
        if not len(self.itemList):
            return
        firstItem = self.itemList[0]
        if len(self.itemList) == 1:
            firstItem.MakeSingle()
        elif len(self.itemList) == 2:
            firstItem.RemoveSingle()

    def UpdateStationInfo(self, stationID):
        self.baseStationID = stationID
        if self.baseStationID:
            self.UpdateHeaderCount()
        else:
            self.SetCaption(GetByLabel(self.captionTextPath))
        if not self.baseStationID or IsStation(self.baseStationID):
            self.sccRow.Hide()
        else:
            self.sccRow.Show()

    def RemoveItem(self, itemEntry):
        SellBuyItemsWindow.RemoveItem(self, itemEntry)
        self.CheckItemSize()
        if len(self.itemList) == 0:
            self.baseStationID = None
            self.UpdateStationInfo(None)

    def RemoveItemFromCollection(self, itemEntry):
        self.itemDict.pop(itemEntry.itemID)

    def CheckStation(self, item):
        itemStationID = sm.GetService('invCache').GetStationIDOfItem(item)
        if itemStationID != self.baseStationID:
            return False
        return True

    def ClearErrorLists(self):
        SellBuyItemsWindow.ClearErrorLists(self)
        self.itemsNeedRepackaging = []
        self.itemAlreadyInList = []

    def IsSellable(self, item):
        if item.itemID in self.itemDict:
            self.itemAlreadyInList.append(item)
            return False
        sessionChecker = SessionChecker(session, sm)
        itemChecker = ItemChecker(item, sessionChecker)
        if not itemChecker.OfferSellThisItem():
            self.cannotTradeItemList.append(item)
            return False
        return True

    def OnEntryEdit(self, *args):
        uthread.new(self.UpdateNumbers)

    def DropItems(self, dragObj, nodes):
        if not self.IsAllowedDragData(nodes):
            return
        if not self.CheckItemLocation(self.GetDragNodeItem(nodes[0])):
            return
        self.AddItems([ self.GetDragNodeItem(n) for n in nodes ])

    @staticmethod
    def GetDragNodeItem(node):
        if hasattr(node, 'WithdrawPlex') and callable(node.WithdrawPlex):
            item = node.item
            item.locationID = session.stationid or session.structureid
            item.flagID = invconst.flagHangar
            return item
        else:
            return node.item

    def DrawDurationCombo(self):
        if self.isReadOnly:
            durations = [[GetByLabel('UI/Market/MarketQuote/Immediate'), 0]]
        else:
            durations = [[GetByLabel('UI/Market/MarketQuote/Immediate'), 0],
             [GetByLabel('UI/Common/DateWords/Day'), 1],
             [GetByLabel('UI/Market/MarketQuote/ThreeDays'), 3],
             [GetByLabel('UI/Common/DateWords/Week'), 7],
             [GetByLabel('UI/Market/MarketQuote/TwoWeeks'), 14],
             [GetByLabel('UI/Common/DateWords/Month'), 30],
             [GetByLabel('UI/Market/MarketQuote/ThreeMonths'), 90]]
        durationValue = settings.user.ui.Get(self.durationSettingConfig, 0)
        self.durationCombo = Combo(parent=self.bottomLeft, options=durations, select=durationValue, top=6, callback=self.OnDurationChange, maxVisibleEntries=len(durations))

    def UpdateNumbers(self):
        brokersFee, sccSurchargeFee, salesTax, totalSum = self.GetSums()
        totalShown = totalSum - salesTax - brokersFee - sccSurchargeFee
        if totalSum > 0:
            brokersPerc = round(brokersFee / totalSum * 100, 2)
            sccSurcharge = round(sccSurchargeFee / totalSum * 100, 2)
            salesPerc = round(salesTax / totalSum * 100, 2)
        else:
            brokersPerc = 0.0
            sccSurcharge = 0.0
            salesPerc = 0.0
        self.brokersFeeAmt.text = FmtISK(-brokersFee)
        self.ConfigureBasedOnFee(brokersFee, self.brokersFee, self.brokersFeeAmt)
        self.brokersFee.text = GetByLabel('UI/Market/MarketQuote/BrokersFeePerc', percentage=brokersPerc)
        self.sccSurchargeAmtLabel.text = FmtISK(-sccSurchargeFee)
        self.ConfigureBasedOnFee(sccSurchargeFee, self.sccSurchargeLabel, self.sccSurchargeAmtLabel)
        self.sccSurchargeLabel.text = GetByLabel('UI/Market/MarketQuote/SccSurchargeFeePerc', percentage=sccSurcharge)
        if sccSurchargeFee:
            self.sccRow.Show()
        self.salesTaxAmt.text = FmtISK(-salesTax)
        self.salesTax.text = GetByLabel('UI/Market/MarketQuote/SalesTaxPerc', percentage=salesPerc)
        self.totalAmt.text = FmtISK(totalShown)
        AssignQtyTooltipFunc(self.totalAmt, totalShown, inputType=EDIT_INPUT_TYPE_FLOAT)
        if totalShown < 0:
            self.totalAmt.SetRGB(*COL_RED)
        else:
            self.totalAmt.SetRGB(*COL_GREEN)

    def ConfigureBasedOnFee(self, feeAmt, feeLabel, amtLabel):
        useCorp = self.TradingForCorp()
        walletAmount = sm.GetService('wallet').GetWealth()
        if useCorp:
            walletAmount = sm.GetService('wallet').GetCorpWealth(None)
        if walletAmount < feeAmt:
            feeLabel.SetRGB(*COL_RED)
            amtLabel.SetRGB(*COL_RED)
            cantAffordText = GetByLabel(self.salesButtonCantAffordBrokersFeeDescriptionLabelPath, walletBalance=walletAmount, brokersFee=feeAmt)
            SetTooltipHeaderAndDescription(self.tradeButton, GetByLabel(self.salesButtonCantAffordBrokersFeeTooltipHeaderLabelPath), cantAffordText)
            self.tradeButton.Disable()
        else:
            feeLabel.SetRGB(*COL_WHITE)
            amtLabel.SetRGB(*COL_WHITE)
            self.tradeButton.Enable()
            self.tradeButton.tooltipPanelClassInfo = None

    def GetSums(self):
        brokersFee = 0.0
        sccSurcharge = 0.0
        salesTax = 0
        totalSum = 0
        isImmediate = self.durationCombo.GetValue() == 0
        for item in self.GetItems():
            if item:
                if not isImmediate:
                    brokersFee += item.brokersFee
                    sccSurcharge += item.sccSurcharge
                if isImmediate and item.bestBid is None:
                    pass
                else:
                    salesTax += item.salesTax
                totalSum += item.totalSum

        return (brokersFee,
         sccSurcharge,
         salesTax,
         totalSum)

    def PerformTrade(self, *args):
        return self._PerformTrade()

    def _PerformTrade(self):
        self.sellItemList = []
        unitCount = self.GetUnitCount()
        allItems = self.GetItems()
        if unitCount == 0:
            uicore.Message('uiwarning03')
            return
        if eve.Message('ConfirmSellingItems', {'noOfItems': int(unitCount)}, uiconst.OKCANCEL, suppress=uiconst.ID_OK) != uiconst.ID_OK:
            return
        self.errorItemList = []
        useCorp = self.TradingForCorp()
        duration = self.durationCombo.GetValue()
        expectedBrokerFeePercentage = None
        for item in allItems:
            if duration == 0:
                if item.bestBid:
                    validatedItem = self.GetValidatedItem(item)
                else:
                    continue
            else:
                validatedItem = self.GetValidatedItem(item)
            if validatedItem:
                if duration != 0:
                    if expectedBrokerFeePercentage is None:
                        expectedBrokerFeePercentage = validatedItem.rawBrokerFeePercentage
                    elif not FloatCloseEnough(expectedBrokerFeePercentage, validatedItem.rawBrokerFeePercentage):
                        brokerFeeNow = sm.GetService('marketQuote').GetBrokersFeeCommissionFromStationID(validatedItem.stationID)
                        raise UserError('MktBrokersFeeUnexpected2', {'actualBrokerFeePerc': 100 * brokerFeeNow})
                self.sellItemList.append(validatedItem)

        if not len(self.sellItemList):
            return
        if duration > 0:
            brokerFeeNow = sm.GetService('marketQuote').GetBrokersFeeCommissionFromStationID(self.sellItemList[0].stationID)
            if not FloatCloseEnough(brokerFeeNow, expectedBrokerFeePercentage):
                raise UserError('MktBrokersFeeUnexpected2', {'actualBrokerFeePerc': 100 * brokerFeeNow,
                 'expectedBrokerFeePercentage': expectedBrokerFeePercentage})
        if not self.ContinueAfterWarning(self.sellItemList):
            return
        wereOrdersCreated = sm.GetService('marketQuote').SellMulti(self.sellItemList, useCorp, duration, expectedBrokerFeePercentage)
        if wereOrdersCreated:
            self.Close()

    def GetUnitCount(self):
        unitCount = 0
        isImmediate = self.durationCombo.GetValue() == 0
        for item in self.itemList:
            if isImmediate:
                unitCount += item.estimatedSellCount
            else:
                unitCount += item.GetQtyToSell()

        return unitCount

    def GetValidatedItem(self, item):
        invItem = item.item
        if item.isUpdating:
            return
        price = round(item.GetPrice(), 2)
        if price > MAX_ORDER_PRICE:
            return
        if self.durationCombo.GetValue() == 0:
            if not item.bestBid:
                return
            if not item.estimatedSellCount:
                return
        self.CheckAndHandlePlexVaultItem(item)
        qty = item.GetQtyToSell()
        officeID = None
        if invItem.locationID != item.stationID and invItem.flagID in invconst.flagCorpSAGs:
            officeID = invItem.locationID
        validatedItem = KeyVal(stationID=int(item.stationID), typeID=int(item.typeID), itemID=item.itemID, price=price, quantity=int(qty), officeID=officeID, delta=item.GetDelta(), rawBrokerFeePercentage=item.rawBrokerFeePercentage)
        return validatedItem

    def CheckAndHandlePlexVaultItem(self, item):
        if item.typeID != invconst.typePlex or item.itemID is not None:
            return
        quantity = item.GetQtyToSell()
        item.locationID = session.stationid or session.structureid
        reference = sm.GetService('invCache').GetInventoryMgr().WithdrawPlexFromVault(quantity, item.locationID, item.item.flagID)
        listener = PlexWithdrawalListener(session.userid, quantity, reference)
        loading_wheel = LoadingWheel(parent=self.mainCont, align=uiconst.CENTER)
        loading_wheel.Show()
        while not listener.received_event:
            uthread2.Sleep(1)

        loading_wheel.Hide()
        if listener.received_item_id:
            item.itemID = listener.received_item_id

    def IsAllowedDragData(self, dragData):
        for entry in dragData:
            guid = getattr(entry, '__guid__', None)
            if guid is not None and guid not in INVENTORY_GUIDS:
                return False

        return True

    def OnDurationChange(self, *args):
        newDuration = self.durationCombo.GetValue()
        settings.user.ui.Set(self.durationSettingConfig, newDuration)
        self.UpdateNumbers()
        for item in self.GetItems():
            item.OnDurationChanged(newDuration)

    def UpdateOrderCount(self):
        self.orderCountLabel.text = GetByLabel('UI/Market/MarketQuote/OpenOrdersRemaining', orders=FmtAmt(self.maxCount - self.myOrderCount), maxOrders=FmtAmt(self.maxCount))

    def OnUseCorp(self, *args):
        SellBuyItemsWindow.OnUseCorp(self, *args)
        self.UpdateOrderCount()

    def GetMaxOrderCount(self):
        limits = self.marketQuoteSvc.GetSkillLimits(self.baseStationID)
        maxCount = limits['cnt']
        return maxCount

    def GetCurrentOrderCount(self):
        myOrders = self.marketQuoteSvc.GetMyOrders()
        return len(myOrders)

    def GetItemsWithBadDelta(self, buyItemList):
        lowItems = []
        for item in buyItemList:
            if item.delta < -0.5:
                lowItems.append((item.delta, item))

        return lowItems
