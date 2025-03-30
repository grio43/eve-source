#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpWalletPanel.py
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.baseWalletPanel import BaseWalletPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpISKPanel import CorpISKPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpLPPanel import CorpLPPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpEverMarkPanel import CorpEverMarkPanel
from eve.client.script.ui.shared.neocom.wallet.tabs.corpISKTab import CorpISKTab
from eve.client.script.ui.shared.neocom.wallet.tabs.corpLPTab import CorpLPTab
from eve.client.script.ui.shared.neocom.wallet.tabs.evermarkTab import CorpEverMarkTab
from eve.client.script.ui.shared.neocom.wallet.walletTabGroup import WalletTabGroup
from localization import GetByLabel

class CorpWalletPanel(BaseWalletPanel):
    default_name = 'CorpWalletPanel'

    def ConstructLayout(self):
        self.ConstructPanels()
        self.ConstructHeader()
        self.isInitialized = True

    def ConstructHeader(self):
        self.headerParent = Container(name='headerParent', parent=self, align=uiconst.TOTOP, height=76, idx=0)
        self.tabGroup = WalletTabGroup(name='corpWalletTabGroup', parent=self.headerParent, align=uiconst.TOALL, showLine=False, settingsID='personalWalletTabGroup')
        corpISKTab = self.tabGroup.AddTab('', self.corpISKPanel, self, walletConst.PANEL_CORPISK, tabClass=CorpISKTab)
        self.tabGroup.tabAlign = uiconst.TOTOP_PROP
        self.tabGroup.AddTab(GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints'), self.corpLPPanel, self, walletConst.PANEL_CORPLP, tabClass=CorpLPTab)
        self.tabGroup.AddTab('', self.corpEverMarkPanel, self, walletConst.PANEL_CORPEVERMARKS, tabClass=CorpEverMarkTab)
        self.tabGroup.AutoSelect(useCallback=False)
        corpISKTab.Update()

    def ConstructPanels(self):
        self.corpISKPanel = CorpISKPanel(parent=self.panelContainer, padTop=16)
        self.corpLPPanel = CorpLPPanel(parent=self.panelContainer, top=16)
        self.corpEverMarkPanel = CorpEverMarkPanel(parent=self.panelContainer, padTop=16)

    def LoadTabPanel(self, args, panel, group):
        if args == walletConst.PANEL_CORPLP:
            uthread2.StartTasklet(panel.Update)

    def OnTabSelect(self):
        if hasattr(self, 'corpLPPanel'):
            self.corpLPPanel.RefreshDonatePanel()
        if hasattr(self, 'corpEverMarkPanel'):
            self.corpEverMarkPanel.RefreshDonatePanel()
