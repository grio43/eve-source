#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evebannerads\banner_ad_retrieval.py
import log
import requests
import uthread2
from evebannerads.const import NO_NES_OFFER_ID, AD_DEFAULT_ROTATION_INTERVAL, AD_MIN_ROTATION_INTERVAL, AD_MAX_ROTATION_INTERVAL
from evebannerads.exceptions import NoResponseException, ResponseFailureException, InvalidResponseDataException
AD_GLARE_CAMPAIGNS = 'campaigns'
AD_GLARE_CREATIVE_DATA = 'creative_data'
AD_GLARE_CREATIVE_DATA_IMAGE_HEIGHT = 'height'
AD_GLARE_CREATIVE_DATA_IMAGE_URL = 'image_url'
AD_GLARE_CREATIVE_DATA_IMAGE_WIDTH = 'width'
AD_GLARE_CREATIVE_DATA_LANDING_URL = 'landing_url'
AD_GLARE_CREATIVE_ID = 'crID'
AD_GLARE_CUSTOM_FIELDS = 'custom_fields'
AD_GLARE_CUSTOM_FIELD_NES_LINK = 'nes_link'
AD_GLARE_CUSTOM_FIELD_NES_OFFER = 'nes_offer_id'
AD_GLARE_CUSTOM_FIELD_ROTATION_INTERVAL = 'rotation_interval'

def retrieve_adglare_ad(banner_url, language_id, rotation_settings):
    ad_data = _retrieve_adglare_ad_by_language(banner_url, language_id)
    creative_data = ad_data[AD_GLARE_CREATIVE_DATA]
    custom_fields = ad_data[AD_GLARE_CUSTOM_FIELDS] or {}
    landing_url = creative_data[AD_GLARE_CREATIVE_DATA_LANDING_URL]
    image_data = ImageData(creative_data[AD_GLARE_CREATIVE_DATA_IMAGE_URL], ad_data[AD_GLARE_CREATIVE_DATA_IMAGE_HEIGHT], ad_data[AD_GLARE_CREATIVE_DATA_IMAGE_WIDTH])
    ad_id = ad_data[AD_GLARE_CREATIVE_ID]
    nes_link, nes_offer_id = _retrieve_nes_data(custom_fields)
    rotation_interval = _retrieve_rotation_interval(custom_fields, rotation_settings, ad_id)
    return AdData(landing_url, image_data, ad_id, nes_link, nes_offer_id, rotation_interval)


def _retrieve_adglare_ad_by_language(banner_url, language_id):
    response = requests.get(url=banner_url, headers={'User-Agent': 'client',
     'Accept-Language': language_id.lower()})
    log.LogInfo('Retrieved banner ad response from: %s' % banner_url)
    if not response.ok:
        raise NoResponseException('No response from AdGlare')
    response_data = response.json().get('response')
    if not response_data:
        raise ResponseFailureException('Invalid response data from AdGlare - empty response data')
    if response_data.get('success') == 0:
        error_message = response_data.get('errormsg')
        if error_message:
            raise ResponseFailureException('Invalid response data from AdGlare - %s' % error_message)
        else:
            raise ResponseFailureException('Invalid response data from AdGlare - empty response data')
    campaign_data = response_data.get(AD_GLARE_CAMPAIGNS)
    if not campaign_data:
        raise InvalidResponseDataException('Invalid campaign data AdGlare')
    return campaign_data[0]


def _retrieve_nes_data(ad_custom_fields):
    nes_link = False
    nes_offer_id = NO_NES_OFFER_ID
    if AD_GLARE_CUSTOM_FIELD_NES_OFFER in ad_custom_fields:
        nes_link = True
        nes_offer_id = ad_custom_fields[AD_GLARE_CUSTOM_FIELD_NES_OFFER]
    elif AD_GLARE_CUSTOM_FIELD_NES_LINK in ad_custom_fields:
        nes_link = ad_custom_fields[AD_GLARE_CUSTOM_FIELD_NES_LINK]
    return (nes_link, nes_offer_id)


def _retrieve_rotation_interval(ad_custom_fields, rotation_settings, ad_id):
    rotation_interval = ad_custom_fields.get(AD_GLARE_CUSTOM_FIELD_ROTATION_INTERVAL, rotation_settings.default_rotation_interval)
    if rotation_interval < rotation_settings.min_rotation_interval:
        rotation_interval = rotation_settings.min_rotation_interval
        log.LogError('BannerAd=%s has invalid rotation timer, setting to minimum of %s seconds.' % (ad_id, rotation_settings.min_rotation_interval))
    elif rotation_interval > rotation_settings.max_rotation_interval:
        rotation_interval = rotation_settings.max_rotation_interval
        log.LogError('BannerAd=%s has invalid rotation timer, setting to maximum of %s seconds.' % (ad_id, rotation_settings.max_rotation_interval))
    return rotation_interval


def click_nes_offer(offer_id):
    vgs_service = sm.GetService('vgsService')
    vgs_service.ToggleStore()
    if offer_id > NO_NES_OFFER_ID:
        vgs_service.ShowOffer(offer_id)


def click_external_ad(url_click_method, url):
    if url.startswith(('https://', 'http://')):
        uthread2.start_tasklet(url_click_method, url)
    else:
        log.LogError('Not valid ad path, no ad displayed. Path = ', url)


class ImageData(object):

    def __init__(self, image_url, image_height, image_width):
        self.image_url = image_url
        self.image_height = image_height
        self.image_width = image_width


class AdData(object):

    def __init__(self, landing_url, image_data, ad_id, nes_link, nes_offer_id, rotation_interval):
        self.landing_url = landing_url
        self.image_url = image_data.image_url
        self.image_width = int(image_data.image_height)
        self.image_height = int(image_data.image_width)
        self.ad_id = int(ad_id)
        self.nes_link = bool(nes_link)
        self.nes_offer_id = int(nes_offer_id)
        self.rotation_interval = float(rotation_interval)


class AdRotationSettings(object):

    def __init__(self, default_rotation = AD_DEFAULT_ROTATION_INTERVAL, min_rotation = AD_MIN_ROTATION_INTERVAL, max_rotation = AD_MAX_ROTATION_INTERVAL):
        self.default_rotation_interval = default_rotation
        self.min_rotation_interval = min_rotation
        self.max_rotation_interval = max_rotation
