#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpEverMarkPanel.py
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpDonateEMPanel import CorpDonateEMPanel
from localization import GetByLabel
from carbonui import uiconst
from carbonui.control.tabGroup import TabGroup, GetTabData
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.neocom.wallet import walletConst

class CorpEverMarkPanel(Container):
    panelID = walletConst.PANEL_CORPEVERMARKS

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isInitialized = False
        self.tabGroup = None

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        if self.tabGroup:
            self.tabGroup.AutoSelect()
        self.RefreshDonatePanel()

    def RefreshDonatePanel(self):
        if hasattr(self, 'donatePanel') and self.donatePanel:
            self.donatePanel.on_tab_select()

    def ConstructLayout(self):
        self.donatePanel = CorpDonateEMPanel(parent=self, state=uiconst.UI_HIDDEN)
        tabs = (GetTabData(label=GetByLabel('UI/Wallet/WalletWindow/TabDonateToAlliance'), panel=self.donatePanel, tabID=walletConst.PANEL_CORP_EM_DONATE),)
        self.tabGroup = TabGroup(name='WalletCorpEMTabGroup', parent=self, tabs=tabs, padBottom=16, groupID='WalletCorpEMTabs', idx=0)
