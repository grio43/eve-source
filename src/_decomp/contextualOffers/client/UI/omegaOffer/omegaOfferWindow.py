#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\omegaOffer\omegaOfferWindow.py
from carbonui import uiconst
from contextualOffers.client.UI.bracketBorderWindow import BracketBorderWindow
from contextualOffers.client.UI.omegaOffer.omegaPurchaseContainer import OmegaPurchaseContainer
from contextualOffers.client.UI.omegaOffer.omegaConfirmationContainer import OmegaConfirmationContainer
from localization import GetByLabel
from evephotosvc.const import NONE_PATH
import logging
log = logging.getLogger(__name__)
DEFAULT_IMAGE = 'res:/UI/Texture/Vgs/missing_image.png'

class OmegaOfferWindow(BracketBorderWindow):
    default_name = 'omegaOfferWindow'

    def ApplyAttributes(self, attributes):
        BracketBorderWindow.ApplyAttributes(self, attributes)
        self.activeOfferID = -1

    def ConstructContent(self):
        self.purchaseCont = OmegaPurchaseContainer(name='purchaseCont', parent=self.innerCont, align=uiconst.CENTER, height=self.frameCont.height, width=self.frameCont.width, onButtonClick=self.OnPurchaseButtonClicked, idx=0)
        self.confirmationCont = OmegaConfirmationContainer(name='purchaseCont', parent=self.innerCont, align=uiconst.CENTER, height=self.frameCont.height, width=self.frameCont.width, onButtonClick=self.CloseButtonClicked, idx=0)

    def _load_texture_from_url(self, url):
        if not url:
            raise AttributeError('UrlSprite requires image URL as a parameter')
        photo_service = sm.GetService('photo')
        texture, width, height = photo_service.GetTextureFromURL(url, retry=False)
        if texture is None or texture.resPath == NONE_PATH:
            texture, width, height = photo_service.GetTextureFromURL(DEFAULT_IMAGE, retry=False)
        self.bannerSprite.texture = texture
        self.bannerSprite.width = width
        self.bannerSprite.height = height

    def _set_background(self, uri):
        if uri:
            if uri.startswith('res:'):
                self.SetBackgroundImage(uri)
            elif uri.startswith('https:'):
                self._load_texture_from_url(uri)
            elif uri.startswith('http:'):
                from eveprefs import prefs
                if prefs.clusterMode == 'LOCAL':
                    self._load_texture_from_url(uri)
                else:
                    raise AttributeError(u'Insecure background URLs are only allowed when testing locally')
            else:
                raise AttributeError(u'Unknown background uri schema in %r' % uri)

    def OnPurchaseButtonClicked(self):
        try:
            sm.GetService('contextualOfferSvc').OnBuyClicked(self.activeOfferID)
        except Exception:
            raise UserError('FailedToOpenOfferUrl')

    def OpenPurchaseView(self, message):
        self._set_background(message.get('purchaseBackground', None))
        self.activeOfferID = message.get('offerID', -1)
        self.purchaseCont.LoadOffer(offerID=self.activeOfferID, title=message.get('purchaseTitle', ''), description=message.get('purchaseDescription', ''), offerPrice=message.get('offerPrice', ''), originalPrice=message.get('originalPrice', ''), discount=message.get('discount', ''), buttonText=message.get('purchaseButtonLabel', ''), remainingText=GetByLabel('UI/Common/Remaining'), tooltipHeader=message.get('tooltipHeader', ''), tooltipDescription=message.get('tooltipDescription', ''))
        self.purchaseCont.SetState(uiconst.UI_NORMAL)
        self.confirmationCont.SetState(uiconst.UI_HIDDEN)

    def OpenConfirmationView(self, message):
        self.SetBackgroundImage(message.get('confirmationBackground', None))
        self.confirmationCont.SetTitleText(message.get('confirmationTitle', ''))
        self.confirmationCont.SetDescriptionText(message.get('confirmationDescription', ''))
        self.confirmationCont.SetButtonText(message.get('confirmationButtonLabel', ''))
        self.purchaseCont.SetState(uiconst.UI_HIDDEN)
        self.confirmationCont.SetState(uiconst.UI_NORMAL)

    def PostAnimEnter(self):
        self.purchaseCont.AnimateIn()

    def OnTimerUpdated(self, value):
        self.purchaseCont.OnTimerUpdated(value)
