#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\link.py
import evelink
from raffles.client.localization import Text
from raffles.client.util import get_item_name
SCHEME = 'hyperNet'

def get_raffle_link(raffle):
    return evelink.Link(url=format_raffle_url(raffle.raffle_id), text=Text.link(item_name=get_item_name(type_id=raffle.type_id, item_id=raffle.item_id)))


def register_link_handlers(registry):
    registry.register(SCHEME, handle_raffle_link, hint=get_link_hint)


def handle_raffle_link(url):
    raffle_id = parse_raffle_url(url)
    sm.GetService('raffleSvc').open_link(raffle_id)


def get_link_hint(url):
    return Text.link_hint()


def format_raffle_url(raffle_id):
    return u'{}:{}'.format(SCHEME, raffle_id)


def parse_raffle_url(url):
    start = url.index(':') + 1
    return url[start:]
