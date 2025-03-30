#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\ISKPanel.py
from carbonui.control.tabGroup import TabGroup
import uthread
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.neocom.wallet.walletUtil import CheckSetDefaultWalletDivision

class ISKPanel(Container):
    default_name = 'ISKPanel'
    panelID = None
    __notifyevents__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.isInitialized = False
        self.tabGroup = None

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        if self.tabGroup:
            self.tabGroup.AutoSelect()

    def ConstructLayout(self):
        self.ConstructPanels()
        maintabs = self.GetMainTabs()
        if len(maintabs) > 0:
            self.tabGroup = TabGroup(name='IskPanelTabGroup', parent=self, align=uiconst.TOTOP, idx=0, padBottom=16, UIIDPrefix='IskPanelTab_')
            self.tabGroup.Startup(maintabs, self.panelID, autoselecttab=0, UIIDPrefix='IskPanelTab_')
        uthread.new(CheckSetDefaultWalletDivision)

    def ConstructPanels(self):
        raise NotImplementedError

    def GetMainTabs(self):
        raise NotImplementedError

    def BlinkPanelByIDs(self, panelIDs):
        if self.isInitialized:
            for panelID in panelIDs:
                self.tabGroup.BlinkPanelByID(panelID)

    def GetIskBalance(self):
        raise NotImplementedError
