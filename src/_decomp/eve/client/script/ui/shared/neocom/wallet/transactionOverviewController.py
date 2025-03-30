#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\transactionOverviewController.py
import collections
import evetypes
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
REFTYPEID_BLACKLIST = [appConst.refMarketTransaction, appConst.refMarketEscrow]
NAME_BY_REFGROUPID = {appConst.refGroupCorpAlliance: 'UI/Wallet/WalletWindow/TransactionGroups/CorpAlliance',
 appConst.refGroupAgentsAndMissions: 'UI/Wallet/WalletWindow/TransactionGroups/AgentsAndMissions',
 appConst.refGroupTrade: 'UI/Wallet/WalletWindow/TransactionGroups/Trade',
 appConst.refGroupBounty: 'UI/Wallet/WalletWindow/TransactionGroups/Bounty',
 appConst.refGroupIndustry: 'UI/Wallet/WalletWindow/TransactionGroups/Industry',
 appConst.refGroupTransfer: 'UI/Wallet/WalletWindow/TransactionGroups/Transfers',
 appConst.refGroupMisc: 'UI/Wallet/WalletWindow/TransactionGroups/Miscellaneous',
 appConst.refGroupHypernetRelay: 'UI/HyperNet/WindowTitle'}
Transaction = collections.namedtuple('Transaction', 'amount, refTypeID, refGroupID, name, groupName, categoryID')

class TransactionOverviewController(object):

    def __init__(self, refGroupID = None):
        self.refGroupID = refGroupID
        self.incomeTransactions = []
        self.incomeTransactionGroups = []
        self.expenditureTransactions = []
        self.expenditureTransactionGroups = []
        self._Update()

    def GetIncomeTransactionGroups(self):
        return self.incomeTransactionGroups

    def GetExpenditureTransactionGroups(self):
        return self.expenditureTransactionGroups

    def GetIncomeGroupValues(self):
        return [ group.amount for group in self.incomeTransactionGroups ]

    def GetExpenditureGroupValues(self):
        return [ group.amount for group in self.expenditureTransactionGroups ]

    def GetTotalIncome(self):
        return sum(self.GetIncomeGroupValues())

    def GetTotalExpenses(self):
        return sum(self.GetExpenditureGroupValues())

    def _Update(self):
        self._UpdateWalletTransactions()
        self._UpdateMarketTransactions()
        self.incomeTransactionGroups = self._GetTransactionGroupsSorted(self.incomeTransactions, reverseSort=True)
        self.expenditureTransactionGroups = self._GetTransactionGroupsSorted(self.expenditureTransactions, reverseSort=False)

    def _GetTransactionGroupsSorted(self, transactions, reverseSort = True):
        if self.refGroupID:
            transactionGroups = self._GetTransactionGroupsByRefTypeID(transactions)
        else:
            transactionGroups = self._GetTransactionGroupsByRefGroupID(transactions)
        totalAmount = sum([ group.amount for group in transactionGroups ])
        for group in transactionGroups:
            group.UpdateRatio(totalAmount)

        return sorted(transactionGroups, key=lambda group: group.amount, reverse=reverseSort)

    def _GetTransactionGroupsByRefTypeID(self, transactions):
        groupsByID = {}
        for transaction in transactions:
            self._AddToTransactionGroupByRefTypeID(groupsByID, transaction)

        return groupsByID.values()

    def _AddToTransactionGroupByRefTypeID(self, groupsByID, tr):
        if (tr.refTypeID, tr.categoryID) not in groupsByID:
            group = TransactionGroup(tr.name, tr.refTypeID, self.refGroupID, tr.categoryID)
            groupsByID[tr.refTypeID, tr.categoryID] = group
        groupsByID[tr.refTypeID, tr.categoryID].AddAmount(tr.amount)

    def _GetTransactionGroupsByRefGroupID(self, transactions):
        groupsByID = {}
        for transaction in transactions:
            self._AddToTransactionGroupByRefGroupID(groupsByID, transaction)

        return groupsByID.values()

    def _AddToTransactionGroupByRefGroupID(self, groupsByID, tr):
        if tr.refGroupID not in groupsByID:
            group = TransactionGroup(tr.groupName, None, tr.refGroupID, tr.categoryID)
            groupsByID[tr.refGroupID] = group
        groupsByID[tr.refGroupID].AddAmount(tr.amount)

    def _UpdateMarketTransactions(self):
        transactions = sm.GetService('market').GetPersonalMarketTransactions()
        refTypeID = appConst.refMarketTransaction
        for transaction in transactions:
            if self.IsFilteredOut(refTypeID) or transaction.isForCorp:
                continue
            categoryID = evetypes.GetCategoryID(transaction.typeID)
            name = evetypes.GetCategoryName(transaction.typeID)
            if transaction.isBuyTransaction:
                name = GetByLabel('UI/Wallet/WalletWindow/ItemsBought', groupName=name)
                self._AddExpenditureEntry(transaction.totalPrice, refTypeID, name, categoryID)
            else:
                name = GetByLabel('UI/Wallet/WalletWindow/ItemsSold', groupName=name)
                self._AddIncomeEntry(transaction.totalPrice, refTypeID, name, categoryID)

    def _UpdateWalletTransactions(self):
        tranactions = sm.GetService('account').GetPersonalTransactions()
        for transaction in tranactions:
            refTypeID = transaction.entryTypeID
            if self.IsFilteredOut(refTypeID) or refTypeID in REFTYPEID_BLACKLIST:
                continue
            name = self.GetTypeName(transaction)
            if name is None:
                continue
            if transaction.amount < 0:
                self._AddExpenditureEntry(transaction.amount, refTypeID, name)
            else:
                self._AddIncomeEntry(transaction.amount, refTypeID, name)

    def IsFilteredOut(self, refTypeID):
        groupID = self.GetGroupID(refTypeID)
        return self.refGroupID and groupID != self.refGroupID

    def GetTypeName(self, transaction):
        refType = sm.GetService('account').GetRefTypeKeyByID(transaction.entryTypeID)
        if not hasattr(refType, 'entryTypeName'):
            return None
        return refType.entryTypeName

    def GetGroupID(self, refTypeID):
        return appConst.refGroupByRefType.get(refTypeID, appConst.refGroupMisc)

    def GetGroupName(self):
        if self.refGroupID:
            return GetByLabel(NAME_BY_REFGROUPID[self.refGroupID])

    def _AddIncomeEntry(self, amount, refTypeID, name, categoryID = None):
        transaction = self._GetTransaction(amount, refTypeID, name, categoryID)
        self.incomeTransactions.append(transaction)

    def _AddExpenditureEntry(self, amount, refTypeID, name, categoryID = None):
        transaction = self._GetTransaction(amount, refTypeID, name, categoryID)
        self.expenditureTransactions.append(transaction)

    def _GetTransaction(self, amount, refTypeID, name, categoryID = None):
        refGroupID = self.GetGroupID(refTypeID)
        groupName = GetByLabel(NAME_BY_REFGROUPID[refGroupID])
        return Transaction(amount=amount, refTypeID=refTypeID, name=name, refGroupID=refGroupID, groupName=groupName, categoryID=categoryID)


class TransactionGroup(object):

    def __init__(self, name, refTypeID, refGroupID, categoryID = None):
        self.refTypeID = refTypeID
        self.refGroupID = refGroupID
        self.name = name
        self.amount = 0.0
        self.ratio = 0.0
        self.categoryID = categoryID

    def AddAmount(self, value):
        self.amount += value

    def UpdateRatio(self, totalAmount):
        if not totalAmount:
            self.ratio = 0.0
        else:
            self.ratio = self.amount / totalAmount

    def GetID(self):
        return (self.refGroupID, self.refTypeID, self.categoryID)

    def GetHint(self):
        return "%.1f%% %s\n<color='#ffffffff'>%s</color>" % (self.ratio * 100, self.name, FmtISK(self.amount))
