#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\link.py
from eve.client.script.ui.shared.mapView import mapViewUtil
SCHEME = 'showinmap'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_show_in_map_link)


def handle_show_in_map_link(url):
    solar_system_ids = parse_show_in_map_url(url)
    mapViewUtil.OpenMap(interestID=solar_system_ids[0])


def parse_show_in_map_url(url):
    content = url[url.index(':') + 1:]
    return [ int(solar_system_id) for solar_system_id in content.split('//') ]
