#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\neocom2\walletPopupManager.py
from collections import defaultdict
from neocom2.transaction import IskTransaction, LpTransaction

class WalletPopupManager(object):

    def __init__(self, settingsContainer, neocom, uiClass, compressionEnabled = True):
        self.isShowingWalletPopup = False
        self.settingsContainer = settingsContainer
        self.uiClass = uiClass
        self.neocom = neocom
        self.usingCompression = compressionEnabled
        self.ResetWaitingTransactions()

    def ResetWaitingTransactions(self):
        self.waitingIskTransactions = []
        self.waitingLpTransactionsByCorp = defaultdict(list)

    def TurnOnCompression(self):
        self.usingCompression = True

    def _AreLiveBalanceUpdatesEnabled(self):
        return self.settingsContainer.Get('walletShowBalanceUpdates', True)

    def _IsBalanceUpdateRelevant(self, transaction):
        threshold = self.settingsContainer.Get('iskNotifyThreshold', 0)
        enabled = self._AreLiveBalanceUpdatesEnabled()
        return enabled and abs(transaction) >= threshold and int(abs(transaction)) > 0

    def OnPersonalAccountChangedClient(self, newBalance, transaction):
        if self._IsBalanceUpdateRelevant(transaction):
            self.waitingIskTransactions.append(IskTransaction(newBalance, transaction))

    def OnLpUpdated(self, corpID, lpBefore, lpAfter):
        transaction = lpAfter - lpBefore
        if self._IsBalanceUpdateRelevant(transaction):
            self.waitingLpTransactionsByCorp[corpID].append(LpTransaction(corpID, lpAfter, transaction))

    def ShowWalletPopup(self, iskTransaction = None, lpTransactionByCorp = None):
        if not self.neocom.display:
            return
        self.isShowingWalletPopup = True
        self.ShowTheActualThing(iskTransaction, lpTransactionByCorp)

    def ShowTheActualThing(self, iskTransaction, lpTransactionByCorp):
        transactions = []
        if iskTransaction:
            transactions.append(iskTransaction)
        for transaction in lpTransactionByCorp.values():
            if transaction:
                transactions.append(transaction)

        updater = self.uiClass(transactions, finishedCallBack=self.OnWalletFinished)
        updater.ShowBalanceChange(self.neocom)

    def OnWalletFinished(self):
        self.isShowingWalletPopup = False
        self.ProcessWaitingTransactions()

    def ProcessWaitingTransactions(self):
        if self.isShowingWalletPopup:
            return
        if not self.waitingIskTransactions and not self.waitingLpTransactionsByCorp:
            return
        if self.usingCompression:
            iskTransaction = None
            if self.waitingIskTransactions:
                iskTransaction = IskTransaction(new_balance=self.waitingIskTransactions[-1].new_balance, transaction=sum((t.transaction for t in self.waitingIskTransactions)))
            lpTransactionByCorp = {}
            for corpID, lpTransactions in self.waitingLpTransactionsByCorp.iteritems():
                lpTransactionByCorp[corpID] = LpTransaction(corporation_id=corpID, new_balance=lpTransactions[-1].new_balance, transaction=sum((t.transaction for t in lpTransactions)))

            self.ResetWaitingTransactions()
            self.ShowWalletPopup(iskTransaction=iskTransaction, lpTransactionByCorp=lpTransactionByCorp)
        elif self.waitingIskTransactions:
            iskTransaction = self.waitingIskTransactions.pop(0)
            self.ShowWalletPopup(iskTransaction=iskTransaction)
        elif self.waitingLpTransactionsByCorp:
            corpID = self.waitingLpTransactionsByCorp.keys()[0]
            if self.waitingLpTransactionsByCorp[corpID]:
                lpTransaction = self.waitingLpTransactionsByCorp[corpID].pop(0)
                lpTransactionByCorp = {corpID: lpTransaction}
                self.ShowWalletPopup(lpTransactionByCorp=lpTransactionByCorp)
            if not self.waitingLpTransactionsByCorp[corpID]:
                del self.waitingLpTransactionsByCorp[corpID]
