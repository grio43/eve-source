#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\vgs\button.py
import numbers
import localization
import log
import uthread
from carbonui import const as uiconst
from eve.client.script.ui.control.eveLabel import EveHeaderMedium, EveHeaderSmall
from eve.client.script.ui.plex.textures import PLEX_12_SOLID_WHITE, PLEX_20_SOLID_WHITE
from eve.client.script.ui.shared.vgs.buttonCore import ButtonCore
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX, COLOR_ISK
from eve.client.script.ui.shared.vgs.label import VgsButtonLabelMedium

class VgsBuyButton(ButtonCore):
    default_color = COLOR_PLEX
    default_padding = (14, 4, 14, 4)
    default_labelClass = VgsButtonLabelMedium


class BuyButtonAurCore(ButtonCore):
    default_color = COLOR_PLEX
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenOfferWindow
        super(BuyButtonAurCore, self).ApplyAttributes(attributes)
        self.offers = None
        self.types = attributes.get('types', None)
        if callable(self.types):
            self.types = self.types()
        if isinstance(self.types, numbers.Number):
            self.types = [self.types]
        if self.types is not None:
            uthread.new(self.FindOffersAndReveal)

    def FindOffersAndReveal(self):
        try:
            store = sm.GetService('vgsService').GetStore()
            self.offers = store.SearchOffersByTypeIDs(self.types)
            if self.offers:
                self.AnimShow()
        except Exception as e:
            if len(e.args) >= 1 and e.args[0] == 'tokenMissing':
                log.LogInfo('Failed to search the NES for offers due to missing token')
            else:
                log.LogException('Failed to search the NES for offers')

    def OpenOfferWindow(self):
        sm.GetService('vgsService').OpenStore(typeIds=self.types)


class BuyButtonAur(BuyButtonAurCore):
    default_contentSpacing = 4
    default_padding = (4, 4, 5, 3)
    default_iconSize = (16, 16)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelTop = 1
    default_text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/BuyNow')
    default_texturePath = PLEX_20_SOLID_WHITE


class BuyButtonAurSmall(BuyButtonAurCore):
    default_contentSpacing = 3
    default_padding = (3, 2, 6, 1)
    default_iconSize = (12, 12)
    default_labelClass = EveHeaderSmall
    default_labelShadow = True
    default_labelTop = 0
    default_text = localization.GetByLabel('UI/Skins/BuyWithAur')
    default_texturePath = PLEX_12_SOLID_WHITE


class BuyButtonIskCore(ButtonCore):
    default_name = 'BuyButtonIskCore'
    default_color = COLOR_ISK

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenMarketWindow
        super(BuyButtonIskCore, self).ApplyAttributes(attributes)
        self.typeID = attributes.get('typeID', None)

    def OpenMarketWindow(self):
        sm.GetService('marketutils').ShowMarketDetails(self.typeID, None)


class BuyButtonIsk(BuyButtonIskCore):
    default_name = 'BuyButtonIsk'
    default_contentSpacing = 4
    default_padding = (4, 4, 5, 3)
    default_iconSize = (16, 16)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelTop = 1
    default_text = localization.GetByLabel('UI/VirtualGoodsStore/Buttons/ViewInMarket')
    default_texturePath = 'res:/UI/Texture/Vgs/isk_16.png'


class BuyButtonIskSmall(BuyButtonIskCore):
    default_name = 'BuyButtonIskSmall'
    default_contentSpacing = 3
    default_padding = (3, 2, 6, 1)
    default_iconSize = (12, 12)
    default_labelClass = EveHeaderSmall
    default_labelShadow = True
    default_labelTop = 0
    default_text = localization.GetByLabel('UI/Skins/BuyWithIsk')
    default_texturePath = 'res:/UI/Texture/classes/skins/isk_12.png'
