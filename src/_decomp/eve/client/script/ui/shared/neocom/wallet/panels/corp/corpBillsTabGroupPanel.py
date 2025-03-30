#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpBillsTabGroupPanel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsAutoPaidPanel import CorpBillsAutoPaidPanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsAutoPaySettingsPanel import CorpBillsAutoPaySettings
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsPayablePanel import CorpBillsPayablePanel
from eve.client.script.ui.shared.neocom.wallet.panels.corp.corpBillsReceivablePanel import CorpBillsReceivablePanel
from localization import GetByLabel

class CorpBillsTabGroupPanel(Container):
    default_name = 'CorpBillsTabGroupPanel'

    def ApplyAttributes(self, attributes):
        super(CorpBillsTabGroupPanel, self).ApplyAttributes(attributes)
        self.isInitialized = False

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.tabGroup.AutoSelect()

    def ConstructLayout(self):
        self.tabGroup = TabGroup(name='tabparent', parent=self, align=uiconst.TOTOP, groupID=walletConst.PANEL_CORPBILLS)
        mainCont = Container(name='mainCont', parent=self)
        self.billsPayablePanel = CorpBillsPayablePanel(parent=mainCont, state=uiconst.UI_HIDDEN)
        self.billsReceivablePanel = CorpBillsReceivablePanel(parent=mainCont, state=uiconst.UI_HIDDEN)
        self.billsAutoPaidPanel = CorpBillsAutoPaidPanel(parent=mainCont, state=uiconst.UI_HIDDEN)
        self.billsAutoPaySettingsPanel = CorpBillsAutoPaySettings(parent=mainCont, state=uiconst.UI_HIDDEN)
        tabs = ((GetByLabel('UI/Wallet/WalletWindow/TabPayable'),
          self.billsPayablePanel,
          self,
          walletConst.PANEL_CORPBILLS_PAYABLE),
         (GetByLabel('UI/Wallet/WalletWindow/TabReceivable'),
          self.billsReceivablePanel,
          self,
          walletConst.PANEL_CORPBILLS_RECEIVABLE),
         (GetByLabel('UI/Wallet/WalletWindow/TabAutomaticallyPaid'),
          self.billsAutoPaidPanel,
          self,
          walletConst.PANEL_CORPBILLS_AUTOPAY),
         (GetByLabel('UI/Wallet/WalletWindow/TabAutomaticPaySettings'),
          self.billsAutoPaySettingsPanel,
          self,
          walletConst.PANEL_CORPBILLS_AUTOPAYSETTINGS))
        self.tabGroup.Startup(tabs)
