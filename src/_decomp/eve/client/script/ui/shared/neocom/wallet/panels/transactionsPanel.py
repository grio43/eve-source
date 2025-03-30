#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\transactionsPanel.py
import blue
import log
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.wallet import walletConst, transactionsUtil
from eve.client.script.ui.shared.neocom.wallet.panels.baseTransactionsPanel import TransactionsScroll, BaseTransaction, BaseTransactionsList, BaseTransactionsPanel, GetTransactionKeyVal
from eve.client.script.ui.shared.neocom.wallet.transactionsUtil import GetTransactionHint
from eve.client.script.ui.shared.neocom.wallet.walletConst import WALLET_CORPTRANSACTIONS_SCROLLID
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.common.lib import appConst as const
from eve.common.script.util.walletEntryFormat import FmtWalletEntry
from eveaccounting import get_accounting_key_for_name
from eveservices.menu import GetMenuService
from localization import GetByLabel
from timeDateHelpers.const import MONTHANDYEAR_NAME_TEXT
DATE_FILTER_LAST30DAYS = (None, None)

class Transaction(BaseTransaction):

    def __init__(self, transactionData):
        super(Transaction, self).__init__(transactionData)
        self.amount = self.data.amount
        self.balance = self.data.balance
        refType = sm.GetService('account').GetRefTypeKeyByID(self.data.entryTypeID)
        self.dateString = GetByLabel('UI/Wallet/WalletWindow/FmtWalletDate', dt=self.data.transactionDate)
        self.typeString = refType.entryTypeName
        self.amountString = FmtWalletCurrency(self.data.amount, self.data.currency)
        self.balanceString = FmtWalletCurrency(self.data.balance, self.data.currency)
        self.descriptionString = FmtWalletEntry(self.data.entryTypeID, self.data.ownerID1, self.data.ownerID2, self.data.referenceID, amount=self.data.amount, reason=self.data.description)
        self.hint = GetTransactionHint(self.data)
        if self.hint:
            self.descriptionString = GetByLabel('UI/Wallet/WalletWindow/HintExtraReference', refText=self.descriptionString)


class TransactionsList(BaseTransactionsList):

    def __init__(self, scrollHeaders):
        super(TransactionsList, self).__init__(scrollHeaders)
        self._entryTypes = set()

    def LoadTransactions(self, transactions):
        super(TransactionsList, self).LoadTransactions(transactions)
        self._entryTypes = set([ transaction.data.entryTypeID for transaction in self._allTransactions ])

    def GetAvailableEntryTypes(self):
        return self._entryTypes


class TransactionsPanel(BaseTransactionsPanel):
    default_name = 'TransactionsPanel'

    def ApplyAttributes(self, attributes):
        super(TransactionsPanel, self).ApplyAttributes(attributes)
        self.scroll.sr.id = WALLET_CORPTRANSACTIONS_SCROLLID

    def _BuildOptionsCont(self):
        return Container(name='transactionsOptionsCont', parent=self, align=uiconst.TOTOP, height=32, idx=1)

    def _BuildScroll(self):
        scroll = TransactionsScroll(parent=self, padTop=8)
        scroll.onSort.connect(self._OnSort)
        return scroll

    def _BuildTransactionsList(self, scrollHeaders):
        return TransactionsList(scrollHeaders)

    def GetScrollHeaders(self):
        return [(GetByLabel('UI/Common/Date'), 'dateString'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderType'), 'typeString'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderAmount'), 'amount'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderBalance'), 'balance'),
         (GetByLabel('UI/Wallet/WalletWindow/ColHeaderDescription'), 'descriptionString')]

    def Close(self):
        super(TransactionsPanel, self).Close()
        settings.user.ui.Set('accountreftype', None)

    def ConstructLayout(self):
        self.referenceTypeCombo = Combo(parent=self.transactionsOptionsCont, name='accountreftype', callback=self.OnCombo, width=110, align=uiconst.TOLEFT, padRight=6)
        self.dateCombo = Combo(parent=self.transactionsOptionsCont, name='dateCombo', callback=self.OnDateCombo, width=130, align=uiconst.TOLEFT, padRight=6, options=self.GetDateComboOptions())
        super(TransactionsPanel, self).ConstructLayout()

    def GetDateComboOptions(self):
        options = []
        for year, month in transactionsUtil.GetLastNYearMonthTuples(6)[1:]:
            options.append((GetByLabel(MONTHANDYEAR_NAME_TEXT[month], year=year), (year, month + 1)))

        options.insert(0, (GetByLabel('UI/Wallet/WalletWindow/Last30Days'), DATE_FILTER_LAST30DAYS))
        return options

    def OnDateCombo(self, *args):
        self.UpdateTransactionsAndPopulateScroll()

    def OnDateEditReturn(self, *args):
        self.UpdateTransactionsAndPopulateScroll()

    def OnCombo(self, entry, header, value, *args):
        settings.user.ui.Set('accountreftype', value)
        self.UpdateTransactionsAndPopulateScroll()

    def UpdateTransactions(self):
        transactions = self._GetTransactions()
        transactionKeyVals = [ GetTransactionKeyVal(t) for t in transactions ]
        ownerIDs = set()
        for t in transactionKeyVals:
            ownerIDs.add(t.ownerID1)
            ownerIDs.add(t.ownerID2)

        cfg.eveowners.Prime(ownerIDs)
        transactions = []
        for t in transactionKeyVals:
            try:
                transactions.append(Transaction(t))
            except AttributeError as exc:
                log.LogWarn('Wallet Journal: failed to load data for entryType {}, error: {}'.format(t.entryTypeID, exc))
                continue

        self._transactionsList.LoadTransactions(transactions)
        self.UpdateReferenceTypeCombo(self._transactionsList.GetAvailableEntryTypes())
        self.UpdateTransactionsByPage()

    def IsTransactionVisible(self, transaction):
        filterValue = self.referenceTypeCombo.GetValue()
        if not filterValue:
            return True
        else:
            return transaction.data.entryTypeID == self.referenceTypeCombo.GetValue()

    def _GetDateTimeSelection(self):
        return self.dateCombo.GetValue()

    def _GetTransactions(self):
        raise NotImplementedError

    def GetScrollEntry(self, transaction):
        refType = sm.GetService('account').GetRefTypeKeyByID(transaction.data.entryTypeID)
        originalType = self.referenceTypeCombo.GetValue()
        if originalType and refType.entryTypeID != originalType:
            return None
        if not refType:
            log.LogWarn('Wallet Journal: No entryType found for entryTypeID', transaction.data.entryTypeID)
            return None
        textList = [transaction.dateString, transaction.typeString]
        color = eveColor.HOT_RED_HEX if transaction.data.amount < 0 else eveColor.SUCCESS_GREEN_HEX
        amountString = '<right><color=%s>%s</color>' % (color, transaction.amountString)
        textList.append(amountString)
        balanceString = '<color=0xffffffff>%s</color>' % transaction.balanceString
        textList.append(balanceString)
        descString = '<left>%s' % transaction.descriptionString
        textList.append(descString)
        isClickable = transactionsUtil.ShouldTransactionTextBeClickable(transaction.data.entryTypeID)
        return GetFromClass(Generic, {'rec': transaction.data,
         'label': '<t>'.join(textList),
         'labelState': uiconst.UI_NORMAL if isClickable else uiconst.UI_DISABLED,
         'name': 'transaction_{}'.format(transaction.data.entryTypeID),
         'sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderAmount'): transaction.data.amount,
         'sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderBalance'): transaction.data.balance,
         'sort_%s' % GetByLabel('UI/Common/Date'): (transaction.data.transactionDate, transaction.data.sortValue),
         'sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderCurrency'): transaction.data.currency,
         'hint': transaction.hint,
         'GetMenu': self._GetMenuForTransactionScrollEntity})

    def _GetMenuForTransactionScrollEntity(self, scrollEntity):
        if scrollEntity.sr.node.rec.entryTypeID != const.refPlayerDonation:
            return []
        transactionSenderID = scrollEntity.sr.node.rec.ownerID1
        transactionReceiverID = scrollEntity.sr.node.rec.ownerID2
        sender = cfg.eveowners.Get(transactionSenderID)
        receiver = cfg.eveowners.Get(transactionReceiverID)
        menuSvc = GetMenuService()
        menuList = []
        menuList.append((sender.name, ('isDynamic', menuSvc.GetMenuFromItemIDTypeID, (transactionSenderID, sender.typeID))))
        menuList.append((receiver.name, ('isDynamic', menuSvc.GetMenuFromItemIDTypeID, (transactionReceiverID, receiver.typeID))))
        return menuList

    def GetNow(self):
        return FmtDate(blue.os.GetWallclockTime(), 'sn')

    def _GetCashAccountingKeys(self):
        accountKeys = [get_accounting_key_for_name('cash')]
        for i in range(2, 8):
            keyID = get_accounting_key_for_name('cash%d' % i)
            accountKeys.append(keyID)

        return accountKeys

    def _GetAccountKeyList(self):
        divisions = sm.GetService('corp').GetDivisionNames()
        keylist = []
        accountingKeys = self._GetCashAccountingKeys()
        for keyID, desc in zip(accountingKeys, [ divisions[i] for i in xrange(8, 15) ]):
            if keyID == session.corpAccountKey or session.corprole & (const.corpRoleAccountant | const.corpRoleJuniorAccountant):
                keylist.append([desc, keyID])

        return keylist

    def UpdateReferenceTypeCombo(self, entryTypes):
        options = self.GetReferenceTypeComboOptions(entryTypes)
        self.referenceTypeCombo.LoadOptions(options, settings.user.ui.Get('accountreftype', None))

    def GetReferenceTypeComboOptions(self, entryTypes = None):
        reflist = []
        for refTypeID in entryTypes:
            refType = sm.GetService('account').GetRefTypeKeyByID(refTypeID)
            if refType and refType.entryTypeID not in walletConst.SKIP_REF_TYPES and refType.entryTypeID < const.refMaxEve:
                reflist.append((refType.entryTypeName.lower(), [refType.entryTypeName, refType.entryTypeID]))

        reflist = SortListOfTuples(reflist)
        reflist.insert(0, (GetByLabel('UI/Wallet/WalletWindow/AccountKeyAllTypes'), None))
        return reflist

    def ShowTransactions(self, accountKey = None):
        self.UpdateTransactionsAndPopulateScroll()
