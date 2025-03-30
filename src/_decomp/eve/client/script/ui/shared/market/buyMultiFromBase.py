#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\buyMultiFromBase.py
from carbonui.control.combo import Combo
from collections import Counter
import locks
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.infoIcon import MoreExtraInfoInTooltip
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.fitting.fittingInfoTooltip import LoadFittingInfoTooltip
from eve.common.lib import appConst as const
from marketutil.const import MAX_ORDER_PRICE
from textImporting import CleanText, GetNameFunc
from uthread2 import BufferedCall
from eve.client.script.ui.shared.market import GetTypeIDFromDragItem
from eve.client.script.ui.shared.market.buySellMultiBase import SellBuyItemsWindow, COL_RED
from eve.client.script.ui.shared.market.buytItemEntry import BuyItemContainer
from eve.client.script.util.contractutils import FmtISKWithDescription
import eveLocalization
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions.exceptionEater import ExceptionEater
import evetypes
from eveprefs import boot
from inventorycommon.util import GetPackagedVolume
from localization import GetByLabel
import localization
from marketutil.orderInfo import GetBuyItemInfo
import uthread
from utillib import KeyVal
import blue
import log
from textImporting.importMultibuy import ImportMultibuy
from carbonui.util.various_unsorted import GetClipboardData
from carbonui.uicore import uicore
ACTION_ICON = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
MILLION = 1000000

class MultiBuy(SellBuyItemsWindow):
    __guid__ = 'form.BuyItems'
    default_iconNum = 'res:/UI/Texture/classes/MultiSell/multiBuy.png'
    default_windowID = 'MultiBuy'
    default_name = 'multiBuy'
    captionTextPath = 'UI/Inventory/ItemActions/MultiBuy'
    scrollId = 'MultiBuyScroll'
    tradeForCorpSettingConfig = 'buyUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandBuy'
    orderCap = 'MultiBuyOrderCap'
    tradeOnConfirm = False
    dropLabelPath = 'UI/Market/Marketbase/DropItemsToAddToBuy'
    cannotBeTradeLabelPath = 'UI/Market/MarketQuote/CannotBeBought'
    badDeltaWarningPath = 'UI/Market/MarketQuote/MultiBuyTypesAboveAverage'
    corpCheckboxTop = 0
    numbersGridTop = 1
    belowColor = '<color=0xff00ff00>'
    aboveColor = '<color=0xffff5050>'
    __notifyevents__ = ['OnOwnOrdersChanged', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        self.blinkEditBG = None
        SellBuyItemsWindow.ApplyAttributes(self, attributes)
        self.AddBuyAndFitBtn()
        self.dropCont.OnDropData = self.DropItems
        self.infoCont.height = 44
        self.totalAmt.LoadTooltipPanel = self.LoadTotalTooltip
        self.itemsScroll.OnDropData = self.DropItems
        self.AddImportButton()
        self.AddLoadingWheel()
        self.DrawStationWarning()
        self.AddToLocationCont()
        self.StartAddItemsThread()

    def AddBuyAndFitBtn(self):
        self.buyAndFitBtn = self.btnGroup.AddButton(GetByLabel('UI/Market/MarketQuote/BuyAndFit'), self.BuyAndFit)
        self.buyAndFitBtn.SetOrder(0)
        self.buyAndFitBtn.LoadTooltipPanel = lambda tooltipPanel, *args: LoadFittingInfoTooltip(tooltipPanel, self.fitting)
        if not self.fitting:
            self.buyAndFitBtn.display = False
        self.btnGroup.ResetLayout()

    def InitializeVariables(self, attributes):
        SellBuyItemsWindow.InitializeVariables(self, attributes)
        self.entriesInScrollByTypeID = {}
        self.orderMultiplier = 1
        self.activeOrders = set()
        self.orderDisabled = False
        self.preItems = self.GetKeyValsForWantedTypes(attributes.get('wantToBuy'))
        self.reloadingItemsCounter = 0
        self.verifyMultiplierTimer = None
        self.expiredOrders = {}
        self.fitting = attributes.fitting
        self.buyAndFitClicked = None
        self.fittingPending = False

    def DrawNumbers(self):
        self.numbersGrid = LayoutGrid(parent=self.bottomRight, columns=2, align=uiconst.TORIGHT, top=self.numbersGridTop, state=uiconst.UI_PICKCHILDREN, cellSpacing=(10, 0))
        self.totalAmt = EveLabelLargeBold(parent=self.numbersGrid, text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.moreInfoIcon = MoreExtraInfoInTooltip(parent=self.numbersGrid, align=uiconst.CENTERLEFT)
        self.moreInfoIcon.LoadTooltipPanel = self.LoadTotalTooltip

    def GetKeyValsForWantedTypes(self, wantToBuy):
        keyVals = []
        for typeID, qty in wantToBuy.iteritems():
            keyVals.append(KeyVal(typeID=typeID, qty=qty))

        return keyVals

    def AddToLocationCont(self):
        self.locationCont.padTop = 24
        self.locationCont.height = 32
        self.orderMultiplierEdit = SingleLineEditInteger(name='orderMultiplierEdit', parent=self.locationCont, align=uiconst.TOPRIGHT, label=GetByLabel('UI/Market/MarketQuote/NumberOfOrders'), adjustWidth=True, minValue=1, maxValue=1000, OnChange=self.OnMultiplierEditChange)
        self.stationCombo = Combo(parent=self.locationCont, callback=self.OnStationChanged, width=200, noChoiceLabel=GetByLabel('UI/Market/MarketQuote/NotStationsAvailable'))
        self.LoadStationOptions()

    def AddImportButton(self):
        self.dropCont.padLeft = 32
        importMenu = UtilMenu(name='importMenu', menuAlign=uiconst.TOPLEFT, parent=self.mainCont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), GetUtilMenu=self.GetImportMenu, texturePath='res:/UI/Texture/Shared/pasteFrom.png', iconSize=28, hint=GetByLabel('UI/Market/MarketQuote/ImportShoppingListHint'))
        self.dropCont.padRight = 32
        exportMenu = UtilMenu(name='exportMenu', menuAlign=uiconst.TOPLEFT, parent=self.mainCont, align=uiconst.TOPRIGHT, pos=(4, 0, 28, 28), GetUtilMenu=self.GetExportMenu, texturePath='res:/UI/Texture/Shared/copyTo.png', iconSize=28, hint=GetByLabel('UI/Market/MarketQuote/ExportShoppingListHint'))

    def GetImportMenu(self, menuParent):
        hint = GetByLabel('UI/Market/MarketQuote/ImportShoppingListOptionHint', type1=const.typeVeldspar, type2=const.typeTritanium)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/MarketQuote/ImportShoppingListOption'), hint=hint, callback=self.ImportShoppingList)

    def ImportShoppingList(self, *args):
        localizedDecimal = eveLocalization.GetDecimalSeparator(localization.SYSTEM_LANGUAGE)
        localizedSeparator = eveLocalization.GetThousandSeparator(localization.SYSTEM_LANGUAGE)
        marketImporter = sm.GetService('marketutils').GetMarketTypeIDFinder()
        multibuyImporter = ImportMultibuy(marketImporter, localizedDecimal, localizedSeparator)
        text = GetClipboardData()
        toAdd, failedLines = multibuyImporter.GetTypesAndQty(text)
        self.AddToOrder(toAdd)
        if failedLines:
            text = '%s<br>' % GetByLabel('UI/SkillQueue/CouldNotReadLines')
            text += '<br>'.join(failedLines)
            eve.Message('CustomInfo', {'info': text}, modal=False)

    def GetExportMenu(self, menuParent):
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/MarketQuote/CopyOrderToClipboard'), callback=self.ExportShoppingListLocalized)
        if self.AreExtraExportOptionsAvailable():
            menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/MarketQuote/CopyOrderToClipboardEnglish'), callback=self.ExportShoppingList)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Market/MarketQuote/AddOrderToQuickbar'), callback=self.AddToQuickbar)

    def AreExtraExportOptionsAvailable(self):
        extraOptions = boot.region != 'optic' and session.languageID != 'EN'
        return extraOptions

    def ExportShoppingList(self, *args):
        self._ExportShoppingList(isLocalized=False)

    def ExportShoppingListLocalized(self, *args):
        self._ExportShoppingList()

    def _ExportShoppingList(self, isLocalized = True, *args):
        listOfLines = []
        nameFunc = GetNameFunc(isLocalized)
        for item in self.GetItemsIterator():
            line = self._GetExportLine(item.typeID, item.GetTotalQty(), item.GetPrice(), nameFunc)
            listOfLines.append(line)

        totalLine = self._GetTotalLine(isLocalized)
        listOfLines.append(totalLine)
        exportText = '\r\n'.join(listOfLines)
        blue.pyos.SetClipboardData(exportText)

    def _GetExportLine(self, typeID, qty, price, nameFunc):
        decimals = 2
        if not price:
            itemPriceText = '-'
            totalPriceText = '-'
        else:
            itemPrice = round(price, decimals)
            itemPriceText = FmtAmt(itemPrice, showFraction=decimals)
            totalPrice = qty * price
            totalPrice = round(totalPrice, decimals)
            totalPriceText = FmtAmt(totalPrice, showFraction=decimals)
        lineParts = [CleanText(nameFunc(typeID)),
         str(qty),
         itemPriceText,
         totalPriceText]
        line = '\t'.join(lineParts)
        return line

    def _GetTotalLine(self, isLocalized = True):
        totalSum = self.GetSum()
        totalSumText = FmtAmt(totalSum, showFraction=2)
        if isLocalized or not self.AreExtraExportOptionsAvailable():
            totalText = GetByLabel('UI/Market/MarketQuote/TotalPrice')
        else:
            totalText = GetByLabel('UI/Market/MarketQuote/TotalPrice', languageID='en')
        totalLine = '\t'.join([totalText,
         '',
         '',
         totalSumText])
        return totalLine

    def AddToQuickbar(self):
        newFolder = sm.GetService('marketutils').AddNewQuickbarFolder()
        if newFolder:
            for item in self.GetItemsIterator():
                sm.GetService('marketutils').AddTypeToQuickBar(item.typeID, newFolder.id, fromMarket=False, extraText=item.GetTotalQty())

    def LoadStationOptions(self):
        currentSelection = self.stationCombo.GetValue()
        stations = self.GetStations()
        if currentSelection:
            select = currentSelection
        elif session.stationid:
            select = session.stationid
        elif stations:
            select = stations[0][1]
        else:
            select = None
        self.stationCombo.LoadOptions(stations, select)
        self.stationCombo.Confirm()

    def DrawStationWarning(self):
        self.stationWarning = EveLabelLargeBold(parent=self.infoCont, text='', align=uiconst.CENTERBOTTOM)
        self.stationWarning.SetRGB(*COL_RED)
        self.stationWarning.display = False

    def AddToOrder(self, wantToBuy, fitting = None):
        if fitting:
            self.fitting = fitting
            self.buyAndFitBtn.display = True
            self.btnGroup.ResetLayout()
        wantedTypes = self.GetKeyValsForWantedTypes(wantToBuy)
        self.AddItems(wantedTypes)

    def AddPreItems(self, preItems):
        self.AddItems(preItems)

    def AddItems(self, itemsToAdd):
        self.reloadingItemsCounter += 1
        items = self.CheckOrderAvailability(itemsToAdd)
        self.ClearErrorLists()
        self.loadingWheel.Show()
        for item in items:
            self.AddItem(item)

        self.DisplayErrorHints()
        self.reloadingItemsCounter -= 1
        if self.reloadingItemsCounter < 1:
            self.loadingWheel.Hide()

    def AddItem(self, itemKeyVal):
        if not self.IsBuyable(itemKeyVal):
            return
        existingEntry = self.entriesInScrollByTypeID.get(itemKeyVal.typeID, None)
        if existingEntry and not existingEntry.destroyed:
            existingEntry.AddQtyToEntry(itemKeyVal.qty)
        else:
            self.DoAddItem(itemKeyVal)

    def AddItemToCollection(self, itemKeyVal, itemEntry):
        self.entriesInScrollByTypeID[itemKeyVal.typeID] = itemEntry

    def GetItemEntry(self, itemKeyVal):
        itemEntry = BuyItemContainer(typeID=itemKeyVal.typeID, qty=int(itemKeyVal.qty), parentFunc=self.RemoveItem, editFunc=self.OnEntryEdit, stationID=self.baseStationID, orderMultiplier=self.orderMultiplier, dropParentFunc=self.DropItems)
        return itemEntry

    def BuyAndFit(self, *args):
        self.buyAndFitClicked = True
        return self._PerformTrade()

    def Cancel(self, *args):
        self.buyAndFitClicked = False
        SellBuyItemsWindow.Cancel(self, *args)

    def PerformTrade(self, *args):
        self.buyAndFitClicked = False
        return self._PerformTrade()

    def _PerformTrade(self):
        useCorp = self.TradingForCorp()
        buyItemList, failedItems = self.GetValidatedAndFailedTypes()
        if not len(buyItemList):
            uicore.Message('uiwarning03')
            return
        if not self.ContinueAfterWarning(buyItemList):
            return
        with ExceptionEater():
            self.LogBuy(buyItemList)
        ordersCreated = sm.GetService('marketQuote').BuyMulti(self.baseStationID, buyItemList, useCorp)
        orderIDs = {order.orderID for order in ordersCreated}
        self.activeOrders.update(orderIDs)
        self.CreateNewBuyOrder(failedItems)
        self.VerifyExpiredOrders()

    def GetItemsWithBadDelta(self, buyItemList):
        highItems = []
        for item in buyItemList:
            if item.delta > 1.0:
                highItems.append((item.delta, item))

        return highItems

    def GetOrderDeltaTextForWarning(self):
        orderPercentage = self.GetOrderDelta()
        orderText = ''
        if orderPercentage > 1.0:
            percText = GetByLabel('UI/Common/Percentage', percentage=FmtAmt(abs(orderPercentage * 100), showFraction=0))
            orderText = GetByLabel('UI/Market/MarketQuote/MultiBuyAboveAverage', percentage=percText)
        return orderText

    def GetValidatedAndFailedTypes(self):
        allItems = self.GetItems()
        failedItemsList = []
        buyItemsList = []
        for item in allItems:
            if item.isUpdating:
                return ([], [])
            if item.newBestPrice:
                validatedItem = self.GetValidatedItem(item)
                if validatedItem:
                    buyItemsList.append(validatedItem)
                    continue
            failedBuyInfo = KeyVal(typeID=item.typeID, qty=item.GetTotalQty())
            failedItemsList.append(failedBuyInfo)

        return (buyItemsList, failedItemsList)

    def GetValidatedItem(self, item):
        if item.isUpdating:
            return
        price = item.GetPrice()
        if not price:
            return
        if price > MAX_ORDER_PRICE:
            return
        price = round(price, 2)
        qty = item.GetTotalQty()
        if qty < 1:
            return
        validatedItem = GetBuyItemInfo(stationID=item.stationID, typeID=item.typeID, price=price, quantity=qty, minVolume=1, delta=item.GetDelta())
        return validatedItem

    def CreateNewBuyOrder(self, failedItems):
        self.ChangeOrderUIState(disable=True)
        self.RemoveAllItem()
        if self.orderMultiplierEdit.GetValue() != 1:
            self.BlinkNumOrdersEdit()
        self.orderMultiplierEdit.SetValue(1)
        if failedItems:
            self.AddItems(failedItems)

    def ChangeOrderUIState(self, disable):
        if disable:
            opacity = 0.5
        else:
            opacity = 1.0
        mainArea = self.GetMainArea()
        mainArea.opacity = opacity
        self.orderDisabled = disable

    def GetStations(self):
        marketDockableLocationsInRegion = sm.GetService('structureDirectory').GetMarketDockableLocationsInRegion()
        solarsystemItems = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2, True, False)
        marketDockableLocations = {i for i in solarsystemItems if i.itemID in marketDockableLocationsInRegion}
        currentStation = session.stationid or session.structureid
        stationList = []
        for eachStation in marketDockableLocations:
            if eachStation.itemID == currentStation:
                continue
            sortValue = (eachStation.celestialIndex, eachStation.orbitIndex, eachStation.itemName)
            stationList.append((sortValue, (eachStation.itemName, eachStation.itemID)))

        stationList = SortListOfTuples(stationList)
        if currentStation:
            stationName = cfg.evelocations.Get(currentStation).name
            currentStationOption = (GetByLabel('UI/Market/MarketQuote/CurrentStation', stationName=stationName), currentStation)
            stationList = [currentStationOption] + stationList
        return stationList

    def RemoveItemFromCollection(self, itemEntry):
        self.entriesInScrollByTypeID.pop(itemEntry.typeID, None)

    def OnMultiplierEditChange(self, *args):
        self.UpdateOrderMultiplierInEntries()
        if self.verifyMultiplierTimer:
            self.verifyMultiplierTimer.KillTimer()
        self.verifyMultiplierTimer = AutoTimer(2000, self.VerifyOrderMultiplier_thread)

    def UpdateOrderMultiplierInEntries(self, force = True):
        self.orderMultiplier = self.orderMultiplierEdit.GetValue()
        for item in self.GetItemsIterator():
            if force or item.orderMultiplier != self.orderMultiplier:
                item.UpdateOrderMultiplier(self.orderMultiplier)

    def VerifyOrderMultiplier_thread(self):
        self.verifyMultiplierTimer = None
        self.UpdateOrderMultiplierInEntries(force=False)

    def OnEntryEdit(self, *args):
        uthread.new(self.UpdateNumbers)

    def UpdateNumbers(self):
        totalShown = self.GetSum()
        if totalShown >= MILLION:
            totalAmtText = '%s (%s)' % (FmtISK(totalShown), FmtISKWithDescription(totalShown, justDesc=True))
        else:
            totalAmtText = FmtISK(totalShown)
        self.moreInfoIcon.display = bool(totalShown)
        self.totalAmt.text = totalAmtText
        self.totalAmt.SetRGB(*COL_RED)
        self.ShowOrHideStationWarning()

    def ShowOrHideStationWarning(self):
        currentStation = session.stationid or session.structureid
        if self.baseStationID is None:
            self.stationWarning.text = GetByLabel('UI/Market/MarketQuote/NoStationSelected')
            self.stationWarning.display = True
        elif self.baseStationID == currentStation:
            self.stationWarning.display = False
        else:
            self.stationWarning.text = GetByLabel('UI/Market/MarketQuote/StationWarning')
            self.stationWarning.display = True

    def GetSum(self):
        totalSum = 0
        for item in self.GetItemsIterator():
            totalSum += item.GetTotalSum()

        return totalSum

    def LoadTotalTooltip(self, tooltipPanel, *args):
        totalShown = self.GetSum()
        if not totalShown or not self.orderMultiplier:
            return
        numTypes, numAvailableTypes, volume = self.GetNumTypesAndNumAvailableTypesAndVolume()
        pricePerOrder = totalShown / float(self.orderMultiplier)
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/NumOrders'))
        tooltipPanel.AddLabelMedium(text=FmtAmt(self.orderMultiplier), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/PricePerOrder'))
        tooltipPanel.AddLabelMedium(text=FmtISK(pricePerOrder), align=uiconst.CENTERRIGHT)
        if pricePerOrder >= MILLION:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text='=%s' % FmtISKWithDescription(pricePerOrder, justDesc=True), align=uiconst.CENTERRIGHT)
        buyingText = GetByLabel('UI/Market/MarketQuote/TypesAvailableAndTotalInOrder', numAvailable=numAvailableTypes, numTypes=numTypes)
        buyingLabel = tooltipPanel.AddLabelSmall(text=buyingText, align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
        buyingLabel.SetAlpha(0.6)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        deltaText = self.GetOrderDeltaText()
        if deltaText:
            tooltipPanel.AddLabelMedium(text=deltaText, colSpan=tooltipPanel.columns)
        if volume:
            tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Common/Volume'))
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Inventory/ContainerCapacity', capacity=volume), align=uiconst.CENTERRIGHT)

    def GetOrderDelta(self):
        totalPrice = sum((i.GetTotalSum() for i in self.GetItemsIterator(onlyValid=True)))
        change = 0
        for item in self.GetItemsIterator(onlyValid=True):
            price = item.GetTotalSum()
            qty = item.GetTotalQty()
            avgPriceForQty = qty * item.averagePrice
            change += (price - avgPriceForQty) / avgPriceForQty * price / totalPrice

        return change

    def GetOrderDeltaText(self):
        percentage = self.GetOrderDelta()
        if percentage == 0:
            return ''
        if percentage < 0:
            percColor = self.belowColor
            devLabelPath = 'UI/Market/MarketQuote/BelowRegionalAverageWithPercentage'
        else:
            percColor = self.aboveColor
            devLabelPath = 'UI/Market/MarketQuote/AboveRegionalAverageWithPercentage'
        percentage = abs(percentage)
        percentageText = FmtAmt(percentage * 100, showFraction=1)
        percText = '%s%s</color>' % (percColor, GetByLabel('UI/Common/Percentage', percentage=percentageText))
        return GetByLabel(devLabelPath, percentage=percText)

    def GetNumTypesAndNumAvailableTypesAndVolume(self):
        numTypes = 0
        numAvailableTypes = 0
        totalVolume = 0
        for item in self.GetItemsIterator():
            numTypes += 1
            if item.GetPrice():
                numAvailableTypes += 1
                vol = item.GetTotalQty() * GetPackagedVolume(item.typeID)
                totalVolume += vol

        return (numTypes, numAvailableTypes, totalVolume)

    def DropItems(self, dragObj, nodes):
        if dragObj is None:
            return
        itemsToAdd = []
        for node in nodes:
            typeID = GetTypeIDFromDragItem(node)
            if typeID:
                itemsToAdd.append(KeyVal(typeID=typeID, qty=1))

        self.AddItems(itemsToAdd)

    def GetTypeIDFromDragItem(self, node):
        return GetTypeIDFromDragItem(node)

    def OnStationChanged(self, combo, key, value):
        self.baseStationID = value
        self.UpdateStationID()

    def UpdateStationID(self):
        for item in self.GetItemsIterator():
            item.UpdateStationID(self.baseStationID)

        self.UpdateHeaderCount()
        self.UpdateNumbers()

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        if reason != 'Expiry':
            return
        orderIDs = set()
        for eachOrder in orders:
            self.expiredOrders[eachOrder.orderID] = eachOrder
            orderIDs.add(eachOrder.orderID)

        self._ProccessExpiredOrders(orderIDs)

    def _ProccessExpiredOrders(self, orderIDs):
        failedItems = []
        for eachOrderID in orderIDs:
            if eachOrderID not in self.activeOrders:
                continue
            eachOrder = self.expiredOrders.get(eachOrderID, None)
            if eachOrder and eachOrder.volRemaining != 0:
                failedBuyInfo = KeyVal(typeID=eachOrder.typeID, qty=eachOrder.volRemaining)
                failedItems.append(failedBuyInfo)
            self.activeOrders.discard(eachOrderID)
            self.TryApplyFittingToBuffer()

        if failedItems:
            self.AddItems(failedItems)
        if not failedItems and not self.AreStillItemsInWindow():
            self.CloseWnd()
            return
        if self.orderDisabled and not self.activeOrders:
            self.ChangeOrderUIState(disable=False)

    def CloseWnd(self):
        if self.buyAndFitClicked and self.fitting:
            uthread.new(self.TryApplyFittingOnClosing)
        self.Close()

    def VerifyExpiredOrders(self):
        expiredOrders = set(self.expiredOrders.keys())
        expiredOrdersNotProcessed = self.activeOrders.intersection(expiredOrders)
        if expiredOrdersNotProcessed:
            self._ProccessExpiredOrders(expiredOrdersNotProcessed)

    def AreStillItemsInWindow(self):
        if self.activeOrders:
            return True
        if self.reloadingItemsCounter > 0:
            return True
        if self.itemList:
            return True
        return False

    def RemoveAllItem(self):
        self.itemsScroll.Flush()
        self.itemList = []
        self.entriesInScrollByTypeID = {}
        self.UpdateNumbers()
        self.UpdateHeaderCount()
        self.ClearErrorLists()

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change or 'stationid' in change or 'structureid' in change:
            self.LoadStationOptions()

    def IsBuyable(self, itemKeyVal):
        buyable = True
        if evetypes.GetMarketGroupID(itemKeyVal.typeID) is None:
            self.cannotTradeItemList.append(itemKeyVal)
            buyable = False
        return buyable

    def BlinkNumOrdersEdit(self):
        self.ConstructBlinkBG()
        uicore.animations.FadeTo(self.blinkEditBG, 0.0, 0.5, duration=0.5, curveType=uiconst.ANIM_WAVE, loops=2)

    def ConstructBlinkBG(self):
        if self.blinkEditBG is None:
            self.blinkEditBG = Sprite(name='blinkEditBG', bgParent=self.orderMultiplierEdit, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgSelected.png', opacity=0.0, idx=0)

    def LogBuy(self, buyItemList):
        totalDisplayed = self.totalAmt.text
        totalSum = self.GetSum()
        multiplier = self.orderMultiplierEdit.GetValue()
        buyTextList = []
        for eachItem in buyItemList:
            text = '[typeID=%s, price=%s, qty=%s]' % (eachItem.typeID, eachItem.price, eachItem.quantity)
            buyTextList.append(text)

        buyText = ','.join(buyTextList)
        logInfo = 'Multibuy: totalDisplayed=%s, totalSum=%s, multiplier=%s, buyText=%s' % (totalDisplayed,
         totalSum,
         multiplier,
         buyText)
        log.LogNotice(logInfo)

    def Close(self, *args, **kwds):
        self.verifyMultiplierTimer = None
        return SellBuyItemsWindow.Close(self, *args, **kwds)

    def DisplayErrorHints(self):
        hintTextList = self.GetErrorHints()
        if hintTextList:
            hintText = '<br>'.join(hintTextList)
            eve.Message('CustomInfo', {'info': hintText})

    def AddLoadingWheel(self):
        self.loadingWheel = LoadingWheel(parent=self.scrollCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.loadingWheel.Hide()

    def TryApplyFittingToBuffer(self):
        if not self.buyAndFitClicked or not self.fitting:
            return
        if self.fittingPending:
            return
        self.fittingPending = True
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Market/MarketQuote/AttemptingToFitShip'), '', 1, 2)
        self._TryApplyFittingBuffered()

    @BufferedCall(2000)
    def _TryApplyFittingBuffered(self):
        self.TryApplyFitting()

    def TryApplyFittingOnClosing(self):
        blue.pyos.synchro.SleepWallclock(500)
        if self.fittingPending:
            return
        self.TryApplyFitting()

    def TryApplyFitting(self):
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Market/MarketQuote/AttemptingToFitShip'), '', 1, 2)
        with locks.TempLock('FitShipFromBuyAll'):
            self.fittingPending = False
            self._TryApplyFitting()

    def _TryApplyFitting(self):
        failedToLoad = sm.GetService('fittingSvc').LoadFitting(self.fitting, getFailedDict=True)
        failedToLoadCounter = Counter({x[0]:x[1] for x in failedToLoad})
        if failedToLoadCounter:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/SomeItemsCouldNotBeFitted')})
        else:
            sm.GetService('ghostFittingSvc').TryExitSimulation()
        sm.GetService('loading').ProgressWnd(GetByLabel('UI/Market/MarketQuote/AttemptingToFitShip'), '', 2, 2)
