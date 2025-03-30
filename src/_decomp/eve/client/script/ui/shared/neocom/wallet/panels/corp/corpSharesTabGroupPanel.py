#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpSharesTabGroupPanel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpShareholdersPanel import CorpShareholdersPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpSharesPanel import CorpSharesPanel
from localization import GetByLabel

class CorpSharesTabGroupPanel(Container):
    default_name = 'CorpSharesTabGroupPanel'

    def ApplyAttributes(self, attributes):
        super(CorpSharesTabGroupPanel, self).ApplyAttributes(attributes)
        self.isInitialized = False

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.tabGroup.AutoSelect()

    def ConstructLayout(self):
        self.tabGroup = TabGroup(name='tabparent', parent=self, align=uiconst.TOTOP, groupID=walletConst.PANEL_CORPSHARES)
        mainCont = Container(name='mainCont', parent=self, padding=4)
        self.sharesPanel = CorpSharesPanel(parent=mainCont, state=uiconst.UI_HIDDEN)
        self.shareholdersPanel = CorpShareholdersPanel(parent=mainCont, state=uiconst.UI_HIDDEN)
        tabs = ((GetByLabel('UI/Wallet/WalletWindow/TabOwnedByCorp'),
          self.sharesPanel,
          self,
          walletConst.PANEL_CORPSHARES_OWNED), (GetByLabel('UI/Wallet/WalletWindow/TabShareholders'),
          self.shareholdersPanel,
          self,
          walletConst.PANEL_CORPSHAREHOLDERS))
        self.tabGroup.Startup(tabs)
