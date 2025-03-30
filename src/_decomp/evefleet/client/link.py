#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\client\link.py
import evelink.client
import localization
SCHEME = 'fleet'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_fleet_link, hint='UI/Fleet/ClickToJoinFleet', color_info=evelink.invite_link_color_info)


def handle_fleet_link(url):
    fleet_id = parse_fleet_url(url)
    sm.GetService('fleet').AskJoinFleetFromLink(fleet_id)


def parse_fleet_url(url):
    content = url[url.index(':') + 1:]
    fleet_id = int(content)
    return fleet_id


def format_fleet_url(fleet_id):
    return u'{}:{}'.format(SCHEME, fleet_id)


def get_fleet_link(fleet_id, name = None):
    if name is None:
        name = localization.GetByLabel('UI/Common/Unknown')
    return evelink.Link(url=format_fleet_url(fleet_id), text=name)
