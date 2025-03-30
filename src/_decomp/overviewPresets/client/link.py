#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\overviewPresets\client\link.py
import evelink.client
from carbon.common.script.sys.serviceManager import ServiceManager
SCHEME = 'overviewPreset'

def overview_preset_link(preset_key, name):
    return evelink.Link(url=format_overview_preset_url(preset_key), text=name)


def register_link_handlers(registry):
    registry.register(SCHEME, handle_link, hint='UI/Overview/ProfileLinkHint', color_info=evelink.settings_link_color_info, accept_link_text=True)


def handle_link(url, link_text):
    parts = url[len(SCHEME) + 1:].split('//')
    if len(parts) == 2:
        preset_key = (parts[0], int(parts[1]))
        get_overview_preset_service().LoadSharedOverviewProfile(preset_key, link_text)


def get_overview_preset_service():
    return ServiceManager.Instance().GetService('overviewPresetSvc')


def format_overview_preset_url(preset_key):
    return '{}:{}//{}'.format(SCHEME, preset_key[0], preset_key[1])
