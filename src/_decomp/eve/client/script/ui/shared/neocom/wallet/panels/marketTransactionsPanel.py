#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\marketTransactionsPanel.py
import math
import eveformat
import evetypes
import utillib
from carbonui import Color, TextColor, uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.shared.neocom.wallet.panels.baseTransactionsPanel import TransactionsScroll, BaseTransaction, BaseTransactionsList, BaseTransactionsPanel, GetTransactionKeyVal
from eve.client.script.ui.shared.neocom.wallet.walletConst import WALLET_TRANSACTIONS_SCROLLID
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetSettingValue, SafeGetName
from eve.client.script.ui.util import searchOld
from eve.common.script.sys import idCheckers
from eveservices.menu import GetMenuService
from inventorycommon.const import categoryOwner, groupCharacter
from localization import GetByLabel
from menu import MenuLabel
COLOR_CORPORATION = Color.from_hex('#88bbff')

class MarketTransaction(BaseTransaction):

    def __init__(self, transactionData):
        super(MarketTransaction, self).__init__(transactionData)
        self.quantity = self.data.quantity
        self.unitPrice = self.data.price
        self.total = self.data.totalPrice
        self.dateString = GetByLabel('UI/Wallet/WalletWindow/FmtWalletDate', dt=self.data.transactionDate)
        self.qtyString = eveformat.number(self.data.quantity)
        self.typeString = SafeGetName(self.data.typeID)
        self.unitPriceString = eveformat.isk(self.data.price, fraction=GetSettingValue('walletShowCents'))
        self.totalString = eveformat.isk(self.data.totalPrice, fraction=GetSettingValue('walletShowCents'))
        self.clientString = GetByLabel('UI/Wallet/WalletWindow/CharacterName', charID=self.data.clientID)
        self.whereString = GetByLabel('UI/Wallet/WalletWindow/StationName', station=self.data.stationID)
        if hasattr(self.data, 'characterID'):
            self.characterString = GetByLabel('UI/Wallet/WalletWindow/CharacterName', charID=self.data.characterID)
        else:
            self.characterString = None
        if hasattr(self.data, 'keyID'):
            self.keyString = sm.GetService('corp').GetCorpAccountName(self.data.keyID)
        else:
            self.keyString = None


class MarketTransactionsList(BaseTransactionsList):

    def __init__(self, scrollHeaders):
        super(MarketTransactionsList, self).__init__(scrollHeaders)
        self._itemTypes = set()
        self._characterIDs = set()

    def LoadTransactions(self, transactions):
        super(MarketTransactionsList, self).LoadTransactions(transactions)
        self._itemTypes = {(evetypes.GetName(tr.data.typeID), tr.data.typeID) for tr in self._allTransactions}
        for tr in self._allTransactions:
            if hasattr(tr.data, 'characterID'):
                self._characterIDs.add((cfg.eveowners.Get(tr.data.characterID).ownerName, tr.data.characterID))

    def GetAvailableItemTypes(self):
        return self._itemTypes

    def GetCharacterIDs(self):
        return self._characterIDs


class MarketTransactionsPanel(BaseTransactionsPanel):
    default_name = 'MarketTransactionsPanel'
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        super(MarketTransactionsPanel, self).ApplyAttributes(attributes)
        self.scroll.sr.id = WALLET_TRANSACTIONS_SCROLLID
        self.scroll.sr.content.OnDropData = self.OnDropData

    def _BuildOptionsCont(self):
        return Container(name='transactionsOptions', parent=self, align=uiconst.TOTOP, height=32, padTop=16)

    def _BuildScroll(self):
        scroll = TransactionsScroll(parent=self, padTop=16)
        scroll.onSort.connect(self._OnSort)
        return scroll

    def _BuildTransactionsList(self, scrollHeaders):
        return MarketTransactionsList(scrollHeaders)

    def GetScrollHeaders(self):
        return [(GetByLabel('UI/Common/Date'), 'dateString'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderQuantity'), 'quantity'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderType'), 'typeString'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderPrice'), 'unitPrice'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderCredit'), 'total'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderClient'), 'clientString'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderWhere'), 'whereString')]

    def ConstructLayout(self):
        super(MarketTransactionsPanel, self).ConstructLayout()
        self.ConstructFilters()

    def ConstructFilters(self):
        buySellOptions = [(GetByLabel('UI/Wallet/WalletWindow/BuyAndSell'), None), (GetByLabel('UI/Wallet/WalletWindow/ComboBuy'), 1), (GetByLabel('UI/Wallet/WalletWindow/ComboSell'), 0)]
        self.sellBuyCombo = Combo(parent=self.transactionsOptionsCont, options=buySellOptions, name='accountkey', width=70, adjustWidth=1, align=uiconst.TOLEFT, padRight=6, callback=self.OnSellBuyCombo)
        self.qtyEdit = SingleLineEditInteger(name='qty', parent=self.transactionsOptionsCont, label=GetByLabel('UI/Wallet/WalletWindow/MinQty'), maxLength=10, top=0, width=70, setvalue=0, adjustWidth=True, align=uiconst.TOLEFT, padRight=6, OnChange=self.OnQuantityEditChange)
        self.minPriceEdit = SingleLineEditInteger(name='qty', parent=self.transactionsOptionsCont, label=GetByLabel('UI/Wallet/WalletWindow/MinValue'), maxLength=10, top=0, width=70, adjustWidth=True, align=uiconst.TOLEFT, padRight=6, OnChange=self.OnMinPriceEditChange)
        self.itemTypeCombo = Combo(name='type', parent=self.transactionsOptionsCont, top=0, width=120, align=uiconst.TOLEFT, padRight=6, callback=self.OnItemTypeCombo)
        self.itemTypeCombo.OnDropData = self.OnDropData

    def OnSellBuyCombo(self, *args):
        self.UpdateTransactionsByPage()
        self.PopulateScroll()

    def OnItemTypeCombo(self, *args):
        self.UpdateTransactionsByPage()
        self.PopulateScroll()

    def OnMinPriceEditChange(self, *args):
        self.UpdateTransactionsByPage()
        self.PopulateScroll()

    def OnQuantityEditChange(self, *args):
        self.UpdateTransactionsByPage()
        self.PopulateScroll()

    def GetIssuer(self, string, exact = 0):
        ownerID = searchOld.Search(string.lower(), groupID=groupCharacter, categoryID=categoryOwner, hideNPC=1, exact=exact, searchWndName='walletIssuerSearch')
        if ownerID:
            return (cfg.eveowners.Get(ownerID).name, ownerID)
        return (string, None)

    def UpdateTransactions(self):
        fromDate = None
        transactions = self._GetTransactions(fromDate)
        cfg.eveowners.Prime([ tr.clientID for tr in transactions ])
        self._transactionsList.LoadTransactions([ MarketTransaction(GetTransactionKeyVal(t)) for t in transactions ])
        self.UpdateItemTypeCombo()
        self.UpdateTransactionsByPage()

    def IsTransactionVisible(self, transaction):
        showBuyTransactions = self.sellBuyCombo.GetValue()
        if showBuyTransactions is not None:
            if showBuyTransactions != transaction.data.isBuyTransaction:
                return False
        typeID = self.itemTypeCombo.GetValue()
        if typeID:
            if typeID != transaction.data.typeID:
                return False
        quantity = self.GetQuantityFilterValue()
        if quantity:
            if quantity > transaction.data.quantity:
                return False
        minPrice = self.GetMinPriceFilterValue()
        if minPrice:
            if minPrice > math.fabs(transaction.data.totalPrice):
                return False
        return True

    def UpdateItemTypeCombo(self):
        options = self._transactionsList.GetAvailableItemTypes()
        options = sorted(list(options))
        options.insert(0, (GetByLabel('UI/Wallet/WalletWindow/AnyItem'), 0))
        self.itemTypeCombo.LoadOptions(options)

    def GetMinPriceFilterValue(self):
        minPrice = self.minPriceEdit.GetValue()
        if minPrice == '':
            minPrice = None
        else:
            minPrice = int(minPrice)
        return minPrice

    def GetQuantityFilterValue(self):
        quantity = self.qtyEdit.GetValue()
        if quantity == '':
            quantity = None
        else:
            quantity = int(quantity)
        return quantity

    def GetScrollEntry(self, tr):
        lines = self._GetTransactionEntryLines(tr)
        text = '<t>'.join(lines)
        data = self.GetScrollEntryData(text, tr)
        return GetFromClass(Generic, data)

    def GetScrollEntryData(self, text, tr):
        data = utillib.KeyVal()
        if tr.data.isForCorp:
            data.hint = eveformat.color(text=GetByLabel('UI/Wallet/WalletWindow/HintCorpTransaction'), color=COLOR_CORPORATION)
        data.OnDblClick = lambda *args: sm.StartService('marketutils').ShowMarketDetails(tr.data.typeID, None)
        data.rec = tr.data
        data.label = text
        data.name = 'marketTransaction_{}'.format(tr.data.typeID)
        data.clientID = tr.data.clientID
        data.GetMenu = self.OnTransactionMenu
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderQuantity'), tr.data.quantity)
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderPrice'), tr.data.price)
        data.Set('sort_%s' % GetByLabel('UI/Common/Date'), tr.data.transactionID)
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderCredit'), tr.data.totalPrice)
        return data

    def _GetTransactionEntryLines(self, tr):
        lines = []
        dateText = tr.dateString
        if tr.data.isForCorp:
            dateText = eveformat.color(text=dateText, color=COLOR_CORPORATION)
        lines.append(dateText)
        rightQty = '<right>%s' % tr.qtyString
        lines.append(rightQty)
        lines.append(tr.typeString)
        rightPrice = '<right>%s' % eveformat.color(text=tr.unitPriceString, color=TextColor.HIGHLIGHT)
        lines.append(rightPrice)
        color = TextColor.DANGER if tr.data.isBuyTransaction else TextColor.SUCCESS
        rightCurrency = '<right>%s' % eveformat.color(text=tr.totalString, color=color)
        lines.append(rightCurrency)
        leftClient = '<left>%s' % tr.clientString
        lines.append(leftClient)
        leftLocation = '<left>%s' % tr.whereString
        lines.append(leftLocation)
        return lines

    def OnTransactionMenu(self, entry):
        m = GetMenuService().GetMenuFromItemIDTypeID(None, entry.sr.node.rec.typeID, includeMarketDetails=True)
        m += [None]
        stationID = entry.sr.node.rec.stationID
        stationTypeID = solarSystemID = None
        if idCheckers.IsStation(stationID):
            stationInfo = sm.GetService('ui').GetStationStaticInfo(stationID)
            stationTypeID = stationInfo.stationTypeID
            solarSystemID = stationInfo.solarSystemID
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
            if structureInfo:
                stationTypeID = structureInfo.typeID
                solarSystemID = structureInfo.solarSystemID
        if stationTypeID and solarSystemID:
            m += [(MenuLabel('UI/Wallet/WalletWindow/MenuLocation'), GetMenuService().CelestialMenu(stationID, typeID=stationTypeID, parentID=solarSystemID))]
        m += [(MenuLabel('UI/Wallet/WalletWindow/ColHeaderClient'), GetMenuService().CharacterMenu(entry.sr.node.clientID))]
        return m

    def OnDropData(self, dragSource, dragData):
        typeID = dragData[0].invtype
        itemExists = self.itemTypeCombo.SelectItemByValue(typeID)
        if itemExists:
            self.OnItemTypeCombo()
        else:
            ShowQuickMessage(GetByLabel('UI/Wallet/WalletWindow/NoTransactionsFoundForType', typeID=typeID))
