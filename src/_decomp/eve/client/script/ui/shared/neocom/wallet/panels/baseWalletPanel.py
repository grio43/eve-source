#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\baseWalletPanel.py
from carbonui import uiconst
from carbonui.primitives.container import Container

class BaseWalletPanel(Container):
    default_name = 'BaseWalletPanel'
    default_state = uiconst.UI_HIDDEN
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(BaseWalletPanel, self).ApplyAttributes(attributes)
        self.isInitialized = False
        self.tabGroup = None
        self.ConstructBaseLayout()
        self.ConstructLayout()

    def ConstructBaseLayout(self):
        self.ConstructPanelContainer()

    def ConstructLayout(self):
        self.ConstructPanels()

    def ConstructPanelContainer(self):
        self.panelContainer = Container(name='panelContainer', parent=self, clipChildren=True)

    def ConstructPanels(self):
        pass
