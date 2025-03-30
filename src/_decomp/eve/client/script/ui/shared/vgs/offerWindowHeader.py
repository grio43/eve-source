#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\offerWindowHeader.py
import localization
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.shared.vgs.aurBalance import AurBalance
from eve.client.script.ui.shared.vgs.headerButton import HeaderButton

class OfferWindowHeader(Container):
    default_height = 50

    def ApplyAttributes(self, attributes):
        super(OfferWindowHeader, self).ApplyAttributes(attributes)
        self.onExit = attributes.get('onExit')
        self.onBack = attributes.get('onBack')
        self.ConstructLayout()

    def ConstructLayout(self):
        Fill(bgParent=self, color=(0.08, 0.08, 0.08, 1.0))
        Sprite(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=171, height=40, padLeft=10, texturePath='res:/UI/Texture/Vgs/storeLogoOfferWindow.png')
        exit = HeaderButton(parent=self, align=uiconst.TOPRIGHT, left=8, top=8, texturePath='res:/UI/Texture/Vgs/exit.png', hint=localization.GetByLabel('UI/Common/Buttons/Close'), onClick=self.onExit)
        self.backButton = HeaderButton(parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, left=8, top=exit.top + exit.height + 2, texturePath='res:/UI/Texture/Vgs/back.png', hint=localization.GetByLabel('UI/VirtualGoodsStore/BackToPickOffer'), onClick=self.onBack, opacity=0.0)
        AurBalance(name='AurumBalance', parent=self, align=uiconst.TOPRIGHT, left=8 + exit.width + 16, top=12, account=sm.GetService('vgsService').GetStore().GetAccount())

    def EnableBackButton(self):
        self.backButton.disabled = False
        self.backButton.state = uiconst.UI_NORMAL
        animations.FadeIn(self.backButton)

    def DisableBackButton(self):
        self.backButton.disabled = True
        self.backButton.state = uiconst.UI_DISABLED
        animations.FadeOut(self.backButton)
