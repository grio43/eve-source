#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpLPPanel.py
from carbonui import uiconst
from carbonui.control.tabGroup import GetTabData, TabGroup
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpDonateLPPanel import CorpDonateLPPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.lpPanel import LPEntry
from eve.client.script.ui.shared.neocom.wallet.panels.personal.lpPanel import LPBalancePanel
from localization import GetByLabel

class CorpLPPanel(Container):
    panelID = walletConst.PANEL_CORPLP

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

    def Update(self):
        self.balancePanel.Update()

    def ConstructLayout(self):
        self.balancePanel = CorpLPBalancePanel(parent=self, state=uiconst.UI_HIDDEN)
        self.donatePanel = CorpDonateLPPanel(parent=self, state=uiconst.UI_HIDDEN)
        tabs = (GetTabData(label=GetByLabel('UI/Wallet/WalletWindow/TabOverview'), panel=self.balancePanel, tabID=walletConst.PANEL_CORP_LP_BALANCE), GetTabData(label=GetByLabel('UI/Wallet/WalletWindow/TabDonate'), panel=self.donatePanel, tabID=walletConst.PANEL_CORP_LP_DONATE))
        self.tabGroup = TabGroup(name='WalletCorpLPTabGroup', parent=self, tabs=tabs, padBottom=16, groupID='WalletCorpLPTabs', idx=0)


class CorpLPBalancePanel(LPBalancePanel):
    __notifyevents__ = ['OnCorporationLPBalanceChange_Local']

    def GetMyLoyaltyPointsData(self):
        return self.loyaltyPointsWalletSvc.GetAllCorporationLPBalancesExcludingEvermarks()

    def OnCorporationLPBalanceChange_Local(self, _issuerCorpID):
        self.Update()

    def GetScrollEntry(self, corpID, lpAmount, nearestStationID):
        return GetFromClass(CorpLPEntry, {'lpAmount': lpAmount,
         'corpID': corpID,
         'sortValues': LPEntry.GetColumnSortValues(corpID, lpAmount),
         'nearestStationID': nearestStationID})


class CorpLPEntry(LPEntry):

    def GetMenu(self, *args):
        return [(GetByLabel('UI/Commands/ShowInfo'), self.ShowCorpInfo)]
