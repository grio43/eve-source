#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletSvc.py
import logging
import blue
from carbon.common.script.sys.service import Service
from carbon.common.script.util.logUtil import LogInfo
from eve.client.script.ui.shared.neocom.wallet import walletConst, walletSignals
from eve.client.script.ui.shared.neocom.wallet.noneNPCAccountOwnerDialog import NoneNPCAccountOwnerDialog
from eve.client.script.ui.shared.neocom.wallet.transferMoneyWnd import TransferMoneyWnd
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetSettingValue, HaveAccessToCorpWallet, HaveReadAccessToCorpWalletDivision
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from eve.common.lib import appConst
from eveaccounting import get_accounting_key_for_name
from eveexceptions import UserError
from localization import GetByLabel
logger = logging.getLogger(__name__)

class WalletSvc(Service):
    __guid__ = 'svc.wallet'
    __notifyevents__ = ['OnBillReceived',
     'OnAccountChange',
     'OnShareChange',
     'ProcessSessionReset']
    __servicename__ = 'wallet'
    __displayname__ = 'Wallet Client Service'
    __dependencies__ = ['window']
    __update_on_reload__ = 0

    def __init__(self):
        super(WalletSvc, self).__init__()
        self._wealth = None
        self.corpWealthByAccountKey = {}

    def Run(self, memStream = None):
        self.LogInfo('Starting Wallet')
        self._wealth = sm.RemoteSvc('account').GetCashBalance(0)

    @property
    def wealth(self):
        if self._wealth is None:
            self._wealth = sm.RemoteSvc('account').GetCashBalance(0)
        return self._wealth

    def ProcessSessionReset(self):
        self._wealth = None
        self.corpWealthByAccountKey = {}

    def OnBillReceived(self, *args):
        if not HaveAccessToCorpWallet():
            return
        if GetSettingValue('notifyBillChange'):
            sm.GetService('neocom').Blink('wallet', GetByLabel('UI/Neocom/Blink/NewBillReceived'))
        self.TriggerOnCorpBillsChanged()

    def OnShareChange(self, shareholderID, corporationID, change):
        if session.charid == shareholderID:
            self._OnShareChangeChar()
        elif session.corpid in (shareholderID, corporationID) and HaveAccessToCorpWallet():
            self._OnShareChangeCorp()

    def _OnShareChangeCorp(self):
        if GetSettingValue('notifyShareChangeCorp'):
            sm.GetService('neocom').Blink('wallet', GetByLabel('UI/Neocom/Blink/CorpSharesChanged'))

    def _OnShareChangeChar(self):
        if GetSettingValue('notifyShareChange'):
            sm.GetService('neocom').Blink('wallet', GetByLabel('UI/Neocom/Blink/SharesChanged'))

    def OnAccountChange(self, accountKey, ownerID, balance):
        LogInfo('Wallet::OnAccountChange', accountKey, ownerID, balance)
        if balance is not None:
            if accountKey == 'cash' and ownerID == session.charid:
                self._OnCharAccountChange(balance)
            elif accountKey in ('cash', 'cash2', 'cash3', 'cash4', 'cash5', 'cash6', 'cash7') and ownerID == session.corpid:
                self._OnCorpAccountChange(accountKey, balance)
        sm.ScatterEvent('OnAccountChange_Local', accountKey, ownerID, balance)

    def _OnCharAccountChange(self, newBalance):
        if GetSettingValue('notifyAccountChange'):
            sm.GetService('neocom').Blink('wallet', GetByLabel('UI/Neocom/Blink/ISKBalanceChanged'))
            self.BlinkPersonalWallet(walletConst.PANEL_TRANSACTIONS)
        difference = newBalance - self.wealth
        sm.ScatterEvent('OnPersonalAccountChangedClient', newBalance, difference)
        self._wealth = newBalance
        walletSignals.on_personal_isk_balance_changed(newBalance, difference)

    def _OnCorpAccountChange(self, accountKey, balance):
        if not HaveAccessToCorpWallet():
            return
        corpAccountKey = self._GetCorpAccountKey(accountKey)
        if not HaveReadAccessToCorpWalletDivision(corpAccountKey):
            return
        if GetSettingValue('notifyAccountChangeCorp'):
            sm.GetService('neocom').Blink('wallet', GetByLabel('UI/Neocom/Blink/CorpISKBalanceChanged'))
            self.BlinkCorpWallet()
        difference = balance - self.GetCorpWealthCached1Min(corpAccountKey)
        sm.ScatterEvent('OnCorpAccountChangedClient', balance, corpAccountKey, difference)
        walletSignals.on_corp_isk_balance_changed(balance, corpAccountKey, difference)

    def _GetCorpAccountKey(self, accountKey):
        return get_accounting_key_for_name(accountKey, 1000)

    def PayBill(self, bill):
        if bill.debtorID == session.charid:
            sm.RemoteSvc('billMgr').CharPayBill(bill.billID)
        elif bill.debtorID == session.corpid:
            if appConst.corpRoleAccountant & session.corprole == appConst.corpRoleAccountant:
                sm.RemoteSvc('billMgr').PayCorporationBill(bill.billID, fromAccountKey=session.corpAccountKey)
                self.TriggerOnCorpBillsChanged()
        elif bill.debtorID == session.allianceid:
            if session.allianceid and appConst.corpRoleAccountant & session.corprole == appConst.corpRoleAccountant:
                sm.GetService('alliance').PayBill(bill.billID, fromAccountKey=session.corpAccountKey)
                self.TriggerOnCorpBillsChanged()

    def TriggerOnCorpBillsChanged(self):
        sm.ScatterEvent('OnCorpWalletBillsChanged')

    def TransferMoney(self, fromID, fromAccountKey, toID, toAccountKey):
        if toID is None:
            dlg = NoneNPCAccountOwnerDialog.Open()
            dlg.ShowModal()
            if not dlg.ownerID:
                return
            toID = dlg.ownerID
        TransferMoneyWnd.CloseIfOpen()
        TransferMoneyWnd.Open(fromID=fromID, fromAccountKey=fromAccountKey, toID=toID, toAccountKey=toAccountKey)

    def GetWealth(self):
        return self.wealth

    def GetCorpWealth(self, accountKey = None):
        try:
            return sm.RemoteSvc('account').GetCashBalance(1, accountKey=accountKey)
        except UserError:
            logger.exception('Unable to fetch corp wealth')
            return 0

    def GetCorpWealthCached1Min(self, accountKey):
        balance, cacheTime = self.corpWealthByAccountKey.get(accountKey, (None, None))
        if balance is None or blue.os.GetTime() - cacheTime > appConst.MIN:
            self.corpWealthByAccountKey[accountKey] = (self.GetCorpWealth(accountKey), blue.os.GetTime())
        return self.corpWealthByAccountKey[accountKey][0]

    def BlinkPersonalWallet(self, panelID = None):
        WalletWindow.BlinkPersonalWallet(panelID)

    def BlinkCorpWallet(self, subtabname = None, subsubtabname = None):
        WalletWindow.BlinkCorpWallet(subtabname)
