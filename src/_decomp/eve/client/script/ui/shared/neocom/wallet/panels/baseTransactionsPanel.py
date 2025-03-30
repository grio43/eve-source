#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\baseTransactionsPanel.py
import math
import utillib
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.walletConst import NUM_TRANSACTIONS_PER_PAGE
from eve.common.lib import appConst
from localization import GetByLabel
from signals import signal

def GetTransactionKeyVal(transaction):
    keyVal = utillib.KeyVal(transaction)
    keyVal.currency = appConst.creditsISK
    keyVal.sortValue = transaction.transactionID
    return keyVal


class BaseTransaction(object):

    def __init__(self, transactionData):
        self.data = transactionData


class BaseTransactionsList(object):

    def __init__(self, scrollHeaders):
        self._allTransactions = []
        self._sortedAndFiltered = []
        self._filterMethod = None
        self._sorting = None
        self._reverse = False
        self._scrollHeaders = scrollHeaders

    def LoadTransactions(self, transactions):
        self._allTransactions = transactions
        self._UpdateSortedAndFiltered()

    def Sort(self, sorting, reverse):
        self._sorting = sorting
        self._reverse = reverse
        self._UpdateSortedAndFiltered()

    def SetFilter(self, filterMethod):
        self._filterMethod = filterMethod
        self._UpdateSortedAndFiltered()

    def GetTransactionsRange(self, fromIdx, count, applySortingAndFiltering = True):
        transactions = self._sortedAndFiltered if applySortingAndFiltering else self._allTransactions
        if fromIdx > len(transactions):
            return []
        toIdx = min(fromIdx + count, len(transactions) + count)
        return transactions[fromIdx:toIdx]

    def GetTotalCount(self, applySortingAndFiltering = True):
        transactions = self._sortedAndFiltered if applySortingAndFiltering else self._allTransactions
        return len(transactions)

    def _UpdateSortedAndFiltered(self):
        if self._filterMethod:
            self._sortedAndFiltered = filter(self._filterMethod, self._allTransactions)
        else:
            self._sortedAndFiltered = [ t for t in self._allTransactions ]
        if self._sorting:
            self._sortedAndFiltered.sort(cmp=self._Cmp, reverse=self._reverse)

    def _Cmp(self, a, b):
        for header, attr in self._scrollHeaders:
            if header == self._sorting and hasattr(a, attr) and hasattr(b, attr):
                return cmp(getattr(a, attr), getattr(b, attr))

        return 0


class TransactionsScroll(Scroll):

    def ApplyAttributes(self, attributes):
        super(TransactionsScroll, self).ApplyAttributes(attributes)
        self.onSort = signal.Signal(signalName='onSort')

    def _Sort(self, by = None, reversesort = 0):
        self.onSort(by, reversesort)


class BaseTransactionsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isInitialized = False
        self._transactionsList = self._BuildTransactionsList(self.GetScrollHeaders())
        self._transactionsList.SetFilter(self.IsTransactionVisible)
        self.currPage = 0
        self.pageCount = 1
        self.transactionsOptionsCont = self._BuildOptionsCont()
        self.scroll = self._BuildScroll()

    def _BuildOptionsCont(self):
        raise NotImplementedError

    def _BuildScroll(self):
        raise NotImplementedError

    def _BuildTransactionsList(self, scrollHeaders):
        raise NotImplementedError

    def IsTransactionVisible(self, transaction):
        raise NotImplementedError

    def GetScrollHeaders(self):
        raise NotImplementedError

    def UpdateTransactionsAndPopulateScroll(self, *args):
        self.UpdateTransactions()
        self.PopulateScroll()

    def UpdateTransactionsByPage(self):
        self.currPage = 0
        self.pageCount = int(math.ceil(self._transactionsList.GetTotalCount() / float(NUM_TRANSACTIONS_PER_PAGE)))

    def _GetTransactions(self, fromDate):
        raise NotImplementedError

    def UpdateTransactions(self):
        raise NotImplementedError

    def PopulateScroll(self, reverse = 1, scrollToTop = 1, ignoreSort = False):
        scrolllist = []
        startIndex = self.currPage * NUM_TRANSACTIONS_PER_PAGE
        transactionsOnCurrentPage = self._transactionsList.GetTransactionsRange(startIndex, NUM_TRANSACTIONS_PER_PAGE)
        for transaction in transactionsOnCurrentPage:
            entry = self.GetScrollEntry(transaction)
            if entry:
                scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, reversesort=reverse, headers=[ x[0] for x in self.GetScrollHeaders() ], noContentHint=GetByLabel('UI/Wallet/WalletWindow/HintNoTransactionsFound'), scrolltotop=scrollToTop, ignoreSort=ignoreSort)
        self.UpdateBrowseButtonState()

    def GetScrollEntry(self, transaction):
        raise NotImplementedError

    def _OnSort(self, by, reverse):
        self._transactionsList.Sort(by, reverse)
        self.PopulateScroll(reverse=reverse, scrollToTop=0, ignoreSort=True)

    def UpdateBrowseButtonState(self):
        if self.pageCount <= 1:
            self.browseCont.Hide()
            return
        self.browseCont.Show()
        if self.pageCount > 1 and self.currPage < self.pageCount - 1:
            self.fwdBtn.Enable()
        else:
            self.fwdBtn.Disable()
        if self.currPage > 0:
            self.backBtn.Enable()
        else:
            self.backBtn.Disable()
        self.UpdateNumEntriesLabel()

    def UpdateNumEntriesLabel(self):
        numTotal = self._transactionsList.GetTotalCount()
        numFirst = self.currPage * NUM_TRANSACTIONS_PER_PAGE + 1
        numLast = min(numTotal, (self.currPage + 1) * NUM_TRANSACTIONS_PER_PAGE)
        text = GetByLabel('UI/Wallet/WalletWindow/ShowingTransactions', numFirst=numFirst, numLast=numLast, numTotal=numTotal)
        self.numEntriesLabel.SetText(text)

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.UpdateTransactionsAndPopulateScroll()

    def ConstructLayout(self):
        self.ConstructBrowseButtons()

    def ConstructBrowseButtons(self):
        self.browseCont = Container(name='sidepar', parent=self, align=uiconst.TOBOTTOM, height=20, idx=0, padding=(0, 6, 0, 2))
        self.backBtn = Button(parent=self.browseCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/Icons/23_64_1.png', iconSize=24, width=18, hint=GetByLabel('UI/Common/Previous'), func=self.BrowseBack)
        self.fwdBtn = Button(parent=self.browseCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/Icons/23_64_2.png', iconSize=24, width=18, hint=GetByLabel('UI/Common/ViewMore'), func=self.BrowseForward)
        cont = Container(parent=self.browseCont)
        self.numEntriesLabel = Label(parent=cont, align=uiconst.CENTERLEFT, left=4)

    def BrowseBack(self, *args):
        self.currPage = max(0, self.currPage - 1)
        return self.PopulateScroll()

    def BrowseForward(self, *args):
        self.currPage = min(self.pageCount - 1, self.currPage + 1)
        return self.PopulateScroll()
