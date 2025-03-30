#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\client\banners.py
import requests
import logging
from xml.etree import ElementTree
from eveexceptions.exceptionEater import ExceptionEater
log = logging.getLogger(__name__)
BANNER_FEED_LANGUAGE_CODES = {'EN': 'en-us',
 'DE': 'de-de',
 'RU': 'ru-ru'}
BANNER_FEED_URL = 'INSERT_URL'
BANNER_FEED_NAMESPACES = {'atom': 'http://www.w3.org/2005/Atom',
 'media': 'http://search.yahoo.com/mrss/',
 'ccpmedia': 'http://ccp/media'}

def GetBanners(language_id, region):
    feed_url = _get_banner_feed_url(language_id, region)
    try:
        resp = requests.get(feed_url)
    except requests.RequestException as e:
        log.warn('GetBanners failed to GET feed from %s: %s', feed_url, e)
        return []

    if resp.status_code != 200:
        log.warn('GetBanners could not read from banner feed %s - Error code:%s', feed_url, resp.status_code)
        return []
    banners = _parse_banner_feed(resp.text)
    return banners


def _get_banner_feed_url(language_id, region):
    if region == 'optic':
        url = 'http://eve.tiancity.com/client'
    else:
        language_code = BANNER_FEED_LANGUAGE_CODES.get(language_id, BANNER_FEED_LANGUAGE_CODES['EN'])
        url = BANNER_FEED_URL
    return url


def _parse_banner_feed(feed):
    root = ElementTree.fromstring(feed)
    banners = []
    for element in root.findall('atom:entry', namespaces=BANNER_FEED_NAMESPACES):
        with ExceptionEater('Failed to parse store banner element'):
            description_element = element.find('ccpmedia:group/ccpmedia:description', namespaces=BANNER_FEED_NAMESPACES)
            action = description_element.text
            image_element = element.find('ccpmedia:group/ccpmedia:content', namespaces=BANNER_FEED_NAMESPACES)
            image_url = image_element.attrib['url']
            banners.append((image_url, action))

    return banners
