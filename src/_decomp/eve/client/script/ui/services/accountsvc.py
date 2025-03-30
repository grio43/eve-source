#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\accountsvc.py
import blue
import localization
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from carbonui import uiconst
from eve.client.script.ui.shared.neocom.wallet.transactionsUtil import GetDerivedTransactions
from eve.common.lib import appConst
from eveexceptions import UserError

class Account(Service):
    __exportedcalls__ = {'GetEntryTypes': [],
     'GetWalletDivisionsInfo': [],
     'GetDefaultContactCost': [],
     'SetDefaultContactCost': [],
     'AskYesNoQuestion': [ROLE_SERVICE]}
    __guid__ = 'svc.account'
    __notifyevents__ = ['ProcessSessionChange', 'OnAccountChange', 'ProcessUIRefresh']
    __servicename__ = 'account'
    __displayname__ = 'Accounting Service'

    def __init__(self):
        Service.__init__(self)
        self.dataLifeTime = appConst.MIN * 1
        self.data = {}
        self.walletDivisionsInfo = None
        self.defaultContactCost = None
        self.blocked = None
        self.nocharge = None
        self.transactionCache = {}
        self.corpTransactionCache = {}

    def Init(self):
        self.dataLifeTime = appConst.MIN * 1
        self.data = {}
        self.walletDivisionsInfo = None
        self.defaultContactCost = None
        self.blocked = None
        self.nocharge = None
        self.transactionCache = {}
        self.corpTransactionCache = {}

    def Run(self, memStream = None):
        self.LogInfo('Starting AccountSvc')
        self.ReleaseAccountSvc()

    def Stop(self, memStream = None):
        self.ReleaseAccountSvc()

    def ProcessSessionChange(self, isremote, session, change):
        if 'charid' in change and change['charid'][1] is not None:
            self.ReleaseAccountSvc()
            self.Init()

    def OnAccountChange(self, accountKey, ownerID, balance):
        self.transactionCache = {}
        self.corpTransactionCache = {}

    def GetAccountMgr(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            return self.moniker
        self.moniker = sm.RemoteSvc('account')
        return self.moniker

    def ReleaseAccountSvc(self):
        if hasattr(self, 'moniker') and self.moniker is not None:
            self.moniker = None
            self.data = {}

    def ProcessUIRefresh(self):
        self.data = {}

    def GetStaticData(self, itemName, trCol = None, trID = None, *args):
        if not self.data.has_key(itemName):
            account = self.GetAccountMgr()
            data = getattr(account, itemName)(*args)
            for rec in data:
                messageID = getattr(rec, trID, None)
                translated = localization.GetByMessageID(messageID)
                setattr(rec, trCol, translated)

            self.data[itemName] = data
        return self.data[itemName]

    def GetEntryTypes(self):
        return self.GetStaticData('GetEntryTypes', 'entryTypeName', 'entryTypeNameID')

    def GetRefTypeKeyByID(self, entryTypeID):
        for rec in self.GetEntryTypes():
            if rec.entryTypeID == entryTypeID:
                return rec

    def GetPersonalTransactions(self, year = None, month = None):
        key = (year, month)
        if key in self.transactionCache:
            return self.transactionCache[key]
        self.transactionCache[key] = self._GetPersonalTransactions(year, month)
        return self.transactionCache[key]

    def _GetPersonalTransactions(self, year, month):
        transactions = self.GetAccountMgr().GetTransactions(appConst.accountingKeyCash, year, month, False)
        derivedTransactions = []
        for transaction in transactions:
            derivedTransactions.extend(GetDerivedTransactions(transaction))

        return derivedTransactions + transactions

    def GetCorpTransactions(self, accountKey, year, month):
        key = (accountKey, year, month)
        if key in self.corpTransactionCache:
            return self.corpTransactionCache[key]
        self.corpTransactionCache[key] = self.GetAccountMgr().GetTransactions(accountKey, year, month, True)
        return self.corpTransactionCache[key]

    def GetWalletDivisionsInfo(self, force = False):
        now = blue.os.GetWallclockTime()
        if self.walletDivisionsInfo is None or self.walletDivisionsInfo.expires < now or force:
            self.walletDivisionsInfo = utillib.KeyVal(info=self.GetAccountMgr().GetWalletDivisionsInfo(), expires=now + 5 * appConst.MIN)
        return self.walletDivisionsInfo.info

    def AskYesNoQuestion(self, question, props, defaultChoice = 1):
        if defaultChoice:
            defaultChoice = uiconst.ID_YES
        else:
            defaultChoice = uiconst.ID_NO
        return eve.Message(question, props, uiconst.YESNO, defaultChoice) == uiconst.ID_YES

    def SetDefaultContactCost(self, cost):
        if cost < 0:
            raise UserError('ContactCostNegativeAmount')
        self.GetAccountMgr().SetContactCost(cost)
        self.defaultContactCost = cost

    def GetDefaultContactCost(self):
        if self.defaultContactCost is None:
            self.defaultContactCost = self.GetAccountMgr().GetDefaultContactCost()
            if self.defaultContactCost is None:
                self.defaultContactCost = -1
        return self.defaultContactCost

    def BlockAll(self):
        self.GetAccountMgr().SetContactCost(None)
        self.defaultContactCost = -1
