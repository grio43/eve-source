#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\marketSvc.py
from carbon.common.script.sys.service import Service
from utillib import KeyVal

class Market(Service):
    __guid__ = 'svc.market'
    __servicename__ = 'Market'
    __displayname__ = 'Market Service'
    __dependencies__ = []
    __notifyevents__ = ['OnOwnOrdersChanged', 'OnSessionReset']

    def Run(self, memStream = None):
        self.personalMarketTransactionCache = {}

    def GetPersonalMarketTransactions(self, fromDate = None):
        if fromDate in self.personalMarketTransactionCache:
            return self.personalMarketTransactionCache[fromDate]
        transactions = sm.GetService('marketQuote').GetMarketProxy().CharGetTransactions(fromDate)
        transactions = [ self._GetPersonalTransactionKeyVal(transaction) for transaction in transactions ]
        self.personalMarketTransactionCache[fromDate] = transactions
        return transactions

    def GetCorpMarketTransactions(self, fromDate = None, accountKey = None):
        transactions = sm.GetService('marketQuote').GetMarketProxy().CorpGetTransactions(fromDate, accountKey)
        transactions = [ self._GetCorpTransactionKeyVal(transaction) for transaction in transactions ]
        return transactions

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        self.personalMarketTransactionCache = {}

    def OnSessionReset(self):
        self.personalMarketTransactionCache = {}

    def _GetCorpTransactionKeyVal(self, transaction):
        transaction = KeyVal(transaction)
        transaction.isBuyTransaction = transaction.accountID == transaction.buyerAccountID
        transaction.characterID = transaction.buyerID if transaction.isBuyTransaction else transaction.sellerID
        transaction.clientID = transaction.sellerID if transaction.isBuyTransaction else transaction.buyerID
        transaction.totalPrice = transaction.price * transaction.quantity
        transaction.isForCorp = False
        if transaction.isBuyTransaction:
            transaction.totalPrice *= -1
        return transaction

    def _GetPersonalTransactionKeyVal(self, transaction):
        transaction = KeyVal(transaction)
        transaction.isBuyTransaction = transaction.buyerID == session.charid
        if transaction.isBuyTransaction:
            transaction.isForCorp = transaction.accountID != transaction.buyerAccountID
        else:
            transaction.isForCorp = transaction.accountID != transaction.sellerAccountID
        transaction.characterID = transaction.buyerID if transaction.isBuyTransaction else transaction.sellerID
        transaction.clientID = transaction.sellerID if transaction.isBuyTransaction else transaction.buyerID
        transaction.totalPrice = transaction.price * transaction.quantity
        if transaction.isBuyTransaction:
            transaction.totalPrice *= -1
        return transaction
