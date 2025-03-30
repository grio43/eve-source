#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpISKPanel.py
from carbonui import AxisAlignment, uiconst
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.primitives.line import Line
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.ISKPanel import ISKPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsTabGroupPanel import CorpBillsTabGroupPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpDivisionsPanel import CorpDivisionsPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpMarketTransactionsPanel import CorpMarketTransactionsPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpSharesTabGroupPanel import CorpSharesTabGroupPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpTransactionsPanel import CorpTransactionsPanel
from eve.client.script.ui.shared.neocom.wallet.walletUtil import AmAccountantOrJuniorAccountant, AmAccountantOrTrader, GetAccessibleCorpWalletDivisionIDs, HaveAccessToCorpWalletDivision, SelectWalletDivision
from localization import GetByLabel

class CorpISKPanel(ISKPanel):
    default_name = 'CorpISKPanel'
    panelID = walletConst.PANEL_CORPISK

    def GetMainTabs(self):
        maintabs = []
        if AmAccountantOrJuniorAccountant():
            maintabs.extend(((GetByLabel('UI/Wallet/WalletWindow/TabBills'),
              self.billsTabGroup,
              self,
              walletConst.PANEL_CORPBILLS), (GetByLabel('UI/Wallet/WalletWindow/TabTransactions'),
              self.transactionsPanel,
              self,
              walletConst.PANEL_CORPTRANSACTIONS)))
        if AmAccountantOrTrader():
            maintabs.append((GetByLabel('UI/Wallet/WalletWindow/MarketTransactions'),
             self.marketTransactionsPanel,
             self,
             walletConst.PANEL_CORPMARKETTRANSACTIONS))
        if AmAccountantOrJuniorAccountant():
            maintabs.extend(((GetByLabel('UI/Corporations/CorpUIHome/Shares'),
              self.corpSharesTabGroupPanel,
              self,
              walletConst.PANEL_CORPSHARES), (GetByLabel('UI/Wallet/WalletWindow/TabWalletDivisions'),
              self.corpDivisionPanel,
              self,
              walletConst.PANEL_CORPWALLETDIVISIONS)))
        return maintabs

    def ConstructPanels(self):
        self.ConstructCorpActionsButtonGroup()
        if AmAccountantOrJuniorAccountant():
            self.billsTabGroup = CorpBillsTabGroupPanel(parent=self, state=uiconst.UI_HIDDEN)
            self.transactionsPanel = CorpTransactionsPanel(parent=self, state=uiconst.UI_HIDDEN)
            self.corpSharesTabGroupPanel = CorpSharesTabGroupPanel(parent=self, state=uiconst.UI_HIDDEN)
            self.corpDivisionPanel = CorpDivisionsPanel(parent=self, state=uiconst.UI_HIDDEN)
        if AmAccountantOrTrader():
            self.marketTransactionsPanel = CorpMarketTransactionsPanel(parent=self, state=uiconst.UI_HIDDEN)

    def TransferMoney(self, fromID, fromAccountKey, toID, toAccountKey):
        sm.GetService('wallet').TransferMoney(fromID, fromAccountKey, toID, toAccountKey)

    def ConstructCorpActionsButtonGroup(self):
        buttonGroup = ButtonGroup(name='corpHeaderButtonGroup', parent=self, align=uiconst.TOBOTTOM, button_size_mode=ButtonSizeMode.DYNAMIC, button_alignment=AxisAlignment.START)
        Line(parent=self, align=uiconst.TOBOTTOM, padding=(0, 8, 0, 8))
        Button(parent=buttonGroup, label=GetByLabel('UI/Wallet/WalletWindow/DepositISK'), func=self.TransferMoney, args=(session.charid,
         None,
         session.corpid,
         session.corpAccountKey))
        if HaveAccessToCorpWalletDivision(session.corpAccountKey):
            Button(parent=buttonGroup, label=GetByLabel('UI/Wallet/WalletWindow/WithdrawISK'), func=self.TransferMoney, args=(session.corpid,
             session.corpAccountKey,
             session.charid,
             None))
            Button(parent=buttonGroup, label=GetByLabel('UI/Wallet/WalletWindow/TransferMoney'), func=self.TransferMoney, args=(session.corpid,
             session.corpAccountKey,
             None,
             None))
        if len(GetAccessibleCorpWalletDivisionIDs()) >= 1:
            Button(parent=buttonGroup, label=GetByLabel('UI/Wallet/WalletWindow/ChangeDivision'), func=SelectWalletDivision, args=None)

    def ShowCorpTransactions(self, accountKey = None):
        self.tabGroup.SelectByID(walletConst.PANEL_CORPTRANSACTIONS, silent=True)
        self.transactionsPanel.ShowTransactions(accountKey)

    def ShowCorpMarketTransactions(self, accountKey = None):
        self.tabGroup.SelectByID(walletConst.PANEL_CORPMARKETTRANSACTIONS, silent=True)
        self.marketTransactionsPanel.ShowMarketTransactions(accountKey)

    def GetIskBalance(self):
        return sm.GetService('wallet').GetCorpWealth()

    def BlinkPanelByIDs(self, panelIDs):
        super(CorpISKPanel, self).BlinkPanelByIDs(panelIDs)
        if self.billsTabGroup:
            for panelID in panelIDs:
                self.billsTabGroup.BlinkPanelByID(panelID)
