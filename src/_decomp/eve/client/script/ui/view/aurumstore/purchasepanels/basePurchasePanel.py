#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\basePurchasePanel.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.view.aurumstore.shared.const import BOTTOM_PANEL_HEIGHT

class BasePurchasePanel(Container):
    default_align = uiconst.TOPLEFT
    default_height = BOTTOM_PANEL_HEIGHT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(BasePurchasePanel, self).ApplyAttributes(attributes)

    def OnPanelActivated(self):
        pass
