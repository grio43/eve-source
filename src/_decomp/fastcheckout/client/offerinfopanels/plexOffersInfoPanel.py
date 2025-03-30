#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\offerinfopanels\plexOffersInfoPanel.py
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from fastcheckout.client.offerinfopanels.baseOfferInfoPanel import BaseOfferInfoPanel
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import LazyUrlSprite
PLEX_OFFER_ICON_BY_QUANTITY = {110: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-110_%s.png',
 240: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-200_%s.png',
 500: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-500_%s.png',
 1100: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-1100_%s.png',
 2860: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-2860_%s.png',
 7430: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-7430_%s.png',
 15400: 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-15400_%s.png'}
DEFAULT_PLEX_OFFER_ICON = 'res:/UI/Texture/classes/PlexVault/offers/PLEXCrates-110_%s.png'

def get_plex_icon_for_quantity(quantity, size = 128):
    for icon_quantity, icon in sorted(PLEX_OFFER_ICON_BY_QUANTITY.items()):
        if icon_quantity >= quantity:
            return icon % size

    return DEFAULT_PLEX_OFFER_ICON % size


class PlexOffersInfoPanel(BaseOfferInfoPanel):
    default_name = 'PlexOfferInfoPanel'

    def ApplyAttributes(self, attributes):
        super(PlexOffersInfoPanel, self).ApplyAttributes(attributes)
        self.free_plex = 0
        self.expanded = False
        self.construct_layout()
        self.set_labels()
        self.offer_name.SetAlign(uiconst.TOLEFT)
        self.offer_price.SetAlign(uiconst.TOLEFT)
        self.offer_name.left = 15
        self.offer_price.left = 15

    def construct_layout(self):
        self.construct_icon()
        self.construct_name()
        self.construct_price()

    def construct_icon(self):
        super(PlexOffersInfoPanel, self).construct_icon()
        if self.offer.imageUrl is not None:
            self.icon = LazyUrlSprite(parent=self.iconContainer, align=uiconst.CENTER, width=128, height=128, imageUrl=self.offer.imageUrl, state=uiconst.UI_DISABLED)
        else:
            self.icon = Sprite(name='PlexIcon', parent=self.iconContainer, align=uiconst.CENTER, width=128, height=128, texturePath=get_plex_icon_for_quantity(self.offer['quantity']), state=uiconst.UI_DISABLED)

    def animate_purchase(self):
        animations.MorphScalar(self.price_container, attrName='top', startVal=self.price_container.top, endVal=-30)
