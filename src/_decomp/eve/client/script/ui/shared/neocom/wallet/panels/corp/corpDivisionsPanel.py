#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpDivisionsPanel.py
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from menu import MenuLabel
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet.walletConst import WALLET_DIVISIONS_SCROLLID
from eve.client.script.ui.shared.neocom.wallet.walletUtil import GetDivisionName, FmtWalletCurrency, HaveAccessToCorpWalletDivision, AmAccountantOrTrader
from eve.common.lib import appConst
from localization import GetByLabel
from utillib import KeyVal

class CorpDivisionsPanel(Container):
    default_name = 'CorpDivisionsPanel'
    __notifyevents__ = ['OnCorpAccountChangedClient']

    def ApplyAttributes(self, attributes):
        super(CorpDivisionsPanel, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self)
        self.scroll.sr.id = WALLET_DIVISIONS_SCROLLID

    def OnTabSelect(self):
        self.PopulateScroll()

    def PopulateScroll(self, force = False):
        scrolllist = []
        for i, division in enumerate(sm.GetService('account').GetWalletDivisionsInfo(force=force)):
            entry = self.GetScrollEntry(division, i + 1)
            scrolllist.append(entry)

        self.scroll.Load(contentList=scrolllist, headers=[GetByLabel('UI/Wallet/WalletWindow/ColHeaderDivision'), GetByLabel('UI/Wallet/WalletWindow/ColHeaderBalance')], noContentHint=GetByLabel('UI/Wallet/WalletWindow/HintNoTransactionsFound'))

    def GetScrollEntry(self, division, divisionNum):
        data = KeyVal()
        divName = GetDivisionName(division.key)
        label = [GetByLabel('UI/Wallet/WalletWindow/DivisionNameIdx', divName=divName, idx=divisionNum), '<t>', FmtWalletCurrency(division.balance, appConst.creditsISK)]
        data.label = label
        data.GetMenu = self.OnDivisionMenu
        data.key = division.key
        data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderDivision'), division.key)
        entry = GetFromClass(Generic, data)
        return entry

    def SetAccountKey(self, combo, label, value, *args):
        if value is not None:
            sm.GetService('corp').SetAccountKey(value)

    def DoSetAccountKey(self, key):
        sm.GetService('corp').SetAccountKey(key)

    def OnDivisionMenu(self, entry):
        m = []
        if HaveAccessToCorpWalletDivision(entry.sr.node.key):
            m.append((MenuLabel('UI/Wallet/WalletWindow/MenuSetActiveWallet'), lambda : self.DoSetAccountKey(entry.sr.node.key)))
            m.append(None)
        if AmAccountantOrTrader():
            m.append((MenuLabel('UI/Wallet/WalletWindow/MenuViewTransactions'), self.OnDivision_ShowTransactions, (entry.sr.node.key,)))
            m.append((MenuLabel('UI/Wallet/WalletWindow/MenuViewMarketTransactions'), self.OnDivision_ShowMarketTransactions, (entry.sr.node.key,)))
        if HaveAccessToCorpWalletDivision(entry.sr.node.key):
            m.append((MenuLabel('UI/Wallet/WalletWindow/MenuTransferToCorp'), self.OnDivision_GiveMoney, (entry.sr.node.key,)))
            m.append((MenuLabel('UI/Wallet/WalletWindow/MenuTransferFromCorp'), self.OnDivision_TakeMoney, (entry.sr.node.key,)))
        return m

    def OnDivision_ShowTransactions(self, key):
        self.parent.ShowCorpTransactions(key)

    def OnDivision_ShowMarketTransactions(self, key):
        self.parent.ShowCorpMarketTransactions(key)

    def OnDivision_GiveMoney(self, key):
        sm.GetService('wallet').TransferMoney(session.corpid, session.corpAccountKey, session.corpid, key)

    def OnDivision_TakeMoney(self, key):
        sm.GetService('wallet').TransferMoney(session.corpid, key, session.corpid, session.corpAccountKey)

    def OnCorpAccountChangedClient(self, balance, accountKey, difference):
        if accountKey == session.corpAccountKey:
            self.PopulateScroll(force=True)
