#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalWalletPanel.py
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.baseWalletPanel import BaseWalletPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.evermarkPanel import EverMarkPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.lpPanel import PersonalLPPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalISKPanel import PersonalISKPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.plexPanel import PlexPanel
from eve.client.script.ui.shared.neocom.wallet.tabs.evermarkTab import EverMarkTab
from eve.client.script.ui.shared.neocom.wallet.tabs.iskTab import IskTab
from eve.client.script.ui.shared.neocom.wallet.tabs.lpTab import LoyaltyPointsTab
from eve.client.script.ui.shared.neocom.wallet.tabs.plexTab import PlexTab
from eve.client.script.ui.shared.neocom.wallet.walletTabGroup import WalletTabGroup
from localization import GetByLabel

class PersonalWalletPanel(BaseWalletPanel):
    default_name = 'PersonalWalletPanel'

    def ConstructLayout(self):
        tabGroupParent = Container(name='tabGroupParent', parent=self, align=uiconst.TOTOP, height=76, idx=0)
        self.tabGroup = WalletTabGroup(name='personalWalletTabGroup', parent=tabGroupParent, align=uiconst.TOALL, showLine=False, settingsID='personalWalletTabGroup', UIIDPrefix='PersonalWalletTab_')

    def Load(self, *args):
        if self.isInitialized:
            return
        self.ConstructPanels()
        self.tabGroup.AddTab(GetByLabel('UI/Common/ISK'), self.iskPanel, self, walletConst.PANEL_PERSONALISK, tabClass=IskTab)
        self.tabGroup.AddTab(GetByLabel('UI/Common/PLEX'), self.plexPanel, self, walletConst.PANEL_PLEX, tabClass=PlexTab)
        self.tabGroup.tabAlign = uiconst.TOTOP_PROP
        self.tabGroup.AddTab(GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints'), self.lpPanel, self, walletConst.PANEL_LP, tabClass=LoyaltyPointsTab)
        self.tabGroup.AddTab(GetByLabel('UI/Wallet/WalletWindow/EverMarks'), self.everMarkPanel, self, walletConst.PANEL_EVERMARKS, tabClass=EverMarkTab)
        self.tabGroup.AutoSelect(useCallback=False)
        self.isInitialized = True

    def OnTabSelect(self):
        self.Load()

    def ConstructPanels(self):
        self.iskPanel = PersonalISKPanel(parent=self.panelContainer, state=uiconst.UI_HIDDEN, top=16)
        self.plexPanel = PlexPanel(parent=self.panelContainer, state=uiconst.UI_HIDDEN, top=16)
        self.lpPanel = PersonalLPPanel(parent=self.panelContainer, state=uiconst.UI_HIDDEN, top=16)
        self.everMarkPanel = EverMarkPanel(parent=self.panelContainer, state=uiconst.UI_HIDDEN, top=16)

    def BlinkPanelByIDs(self, panelIDs):
        if self.isInitialized:
            for panelID in panelIDs:
                self.tabGroup.BlinkPanelByID(panelID)

    def SelectTab(self, panelID):
        self.tabGroup.SelectByID(panelID)
