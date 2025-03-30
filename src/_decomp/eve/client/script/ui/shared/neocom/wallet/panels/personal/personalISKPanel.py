#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalISKPanel.py
from carbonui import uiconst
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.ISKPanel import ISKPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.giveIskPanel import GiveIskPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.overviewPanel import OverviewPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalMarketTransactionsPanel import PersonalMarketTransactionsPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalPaySettingsPanel import PersonalPaySettingsPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalSharesPanel import PersonalSharesPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalTransactionsPanel import PersonalTransactionsPanel
from localization import GetByLabel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst

class PersonalISKPanel(ISKPanel):
    default_name = 'PersonalISKPanel'
    panelID = walletConst.PANEL_PERSONALISK

    def GetMainTabs(self):
        return ({'label': GetByLabel('UI/Wallet/WalletWindow/TabOverview'),
          'panel': self.overviewPanel,
          'code': self,
          'tabID': walletConst.PANEL_OVERVIEW},
         {'label': GetByLabel('UI/Wallet/WalletWindow/TabTransactions'),
          'panel': self.transactionsPanel,
          'code': self,
          'tabID': walletConst.PANEL_TRANSACTIONS,
          'uniqueName': pConst.UNIQUE_NAME_WALLET_TRANSACTIONS_TAB},
         {'label': GetByLabel('UI/Wallet/WalletWindow/MarketTransactions'),
          'panel': self.marketTransactionsPanel,
          'code': self,
          'tabID': walletConst.PANEL_MARKETTRANSACTIONS,
          'uniqueName': pConst.UNIQUE_NAME_WALLET_MARKET_TRANSACTIONS},
         {'label': GetByLabel('UI/Wallet/WalletWindow/TabShares'),
          'panel': self.sharesPanel,
          'code': self,
          'tabID': walletConst.PANEL_SHARES},
         {'label': GetByLabel('UI/Wallet/WalletWindow/PersonalAutoPayment'),
          'panel': self.paySettings,
          'code': self,
          'tabID': walletConst.PANEL_PAYSETTINGS},
         {'label': GetByLabel('UI/Wallet/WalletWindow/GiveMoney'),
          'panel': self.giveIskPanel,
          'code': self,
          'tabID': walletConst.PANEL_GIVEISK})

    def ConstructPanels(self):
        self.overviewPanel = OverviewPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.transactionsPanel = PersonalTransactionsPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.sharesTabs = None
        self.marketTransactionsPanel = PersonalMarketTransactionsPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.sharesPanel = PersonalSharesPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.paySettings = PersonalPaySettingsPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.giveIskPanel = GiveIskPanel(parent=self, state=uiconst.UI_HIDDEN)

    def GetIskBalance(self):
        return sm.GetService('wallet').GetWealth()
