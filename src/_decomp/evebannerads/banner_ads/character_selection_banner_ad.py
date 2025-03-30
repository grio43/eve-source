#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evebannerads\banner_ads\character_selection_banner_ad.py
import log
import signals
from carbonui.uicore import uicore
from carbonui.primitives.sprite import Sprite
from evebannerads.banner_ad_retrieval import click_nes_offer, click_external_ad, AdRotationSettings
from evebannerads.banner_ad_request import BannerAdRequest
from evebannerads.const import BANNER_URL_CHARACTER_SELECTION_SERENITY, BANNER_URL_CHARACTER_SELECTION_TQ
from evebannerads.const import BANNER_AD_ID_CHARACTER_SELECTION
from evephotosvc.const import NONE_PATH
from eveprefs import boot
from regionalui.regionalutils import in_china
AD_SWITCH_FADE_SPEED = 0.25
AD_SWITCH_MIN_OPACITY = 0.75

class CharacterSelectionBannerAd(Sprite):

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self._ad_data = None
        self.on_hide_sprite = signals.Signal()
        self.on_display_sprite = signals.Signal()

    def request_ad(self, banner_ad_service):
        self._banner_ad_service = banner_ad_service
        if in_china(boot.region):
            banner_url = BANNER_URL_CHARACTER_SELECTION_SERENITY
        else:
            banner_url = BANNER_URL_CHARACTER_SELECTION_TQ
        self.banner_ad_request = BannerAdRequest(BANNER_AD_ID_CHARACTER_SELECTION, self.load_ad, banner_url, session.languageID, rotation_settings=AdRotationSettings(), failure_callback=self._hide_sprite)
        self._banner_ad_service.request_rotating_ads(self.banner_ad_request)

    def Close(self):
        self._banner_ad_service = None
        self.on_hide_sprite.clear()
        self.on_display_sprite.clear()
        Sprite.Close(self)

    def load_ad(self, ad_data):
        if ad_data is None:
            self._hide_sprite()
            return
        self._ad_data = ad_data
        self._fade_out_current_sprite()
        self._open_ad()
        self._fade_in_new_sprite()

    def _fade_out_current_sprite(self):
        uicore.animations.FadeTo(self, startVal=1.0, endVal=AD_SWITCH_MIN_OPACITY, duration=AD_SWITCH_FADE_SPEED, sleep=True)

    def _fade_in_new_sprite(self):
        uicore.animations.FadeTo(self, startVal=AD_SWITCH_MIN_OPACITY, duration=AD_SWITCH_FADE_SPEED)

    def _open_ad(self):
        if self._ad_data is None:
            self._hide_sprite()
            return
        texture = self._get_texture_from_image_url()
        if texture.resPath == NONE_PATH:
            self._hide_sprite()
            log.LogError('Did not get a valid image for the banner ad=%s' % self._ad_data.ad_id)
            return
        self._setup_ad_sprite(self._ad_data, texture)
        self._display_sprite()

    def _hide_sprite(self):
        self.display = False
        self.on_hide_sprite()

    def _display_sprite(self):
        self.display = True
        self.on_display_sprite()

    def _get_texture_from_image_url(self):
        texture, _, _ = sm.GetService('photo').GetTextureFromURL(self._ad_data.image_url)
        return texture

    def _setup_ad_sprite(self, ad_data, texture):
        self.texture = texture
        if ad_data.nes_link:
            self.OnClick = (click_nes_offer, ad_data.nes_offer_id)
        else:
            self.url = ad_data.landing_url
            self.OnClick = (click_external_ad, blue.os.ShellExecute, ad_data.landing_url)
