#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\purchaseProgressPanel.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import VgsLabelLarge

class PurchaseProgressPanel(BasePurchasePanel):
    default_name = 'purchaseProgressPanel'

    def ApplyAttributes(self, attributes):
        super(PurchaseProgressPanel, self).ApplyAttributes(attributes)
        cont = Container(parent=self, align=uiconst.TOTOP, height=72, padTop=4)
        LoadingWheel(parent=cont, align=uiconst.CENTER, width=64, height=64)
        captionCont = Container(parent=self, align=uiconst.TOTOP, height=40)
        VgsLabelLarge(parent=captionCont, align=uiconst.CENTER, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/Processing'))
