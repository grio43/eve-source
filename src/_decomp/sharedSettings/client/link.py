#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sharedSettings\client\link.py
import evelink.client
import localization
from sharedSettings import SHARED_SETTING_ITEMS, SHARED_SETTING_BROADCAST
SCHEME = 'sharedSetting'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_shared_settings_link, hint=get_hint, color_info=evelink.settings_link_color_info, accept_link_text=True)


def handle_shared_settings_link(url, link_text):
    settings_key = parse_shared_settings_url(url)
    if settings_key[2] == SHARED_SETTING_ITEMS:
        sm.GetService('itemFilter').LoadSharedFilter(settings_key)
    elif settings_key[2] == SHARED_SETTING_BROADCAST:
        sm.GetService('fleet').LoadSharedBroadcastSettings(settings_key, link_text)


def get_hint(url):
    settings_key = parse_shared_settings_url(url)
    if settings_key[2] == SHARED_SETTING_ITEMS:
        return localization.GetByLabel('UI/Inventory/Filters/SharedItemFilter')
    if settings_key[2] == SHARED_SETTING_BROADCAST:
        return localization.GetByLabel('UI/Fleet/FleetBroadcast/LoadSharedBroadcastSettings')


def parse_shared_settings_url(url):
    parts = url[url.index(':') + 1:].split('//')
    return (parts[0], int(parts[1]), int(parts[2]))


def format_shared_settings_url(settings_key):
    return u'{}:{}//{}//{}'.format(SCHEME, *settings_key)
