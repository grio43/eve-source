#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\local_service\handler.py
import urlparse
from evelink.client.handlers.local_service.endpoints import EndpointRegistry
from evelink.format.local_service import SCHEME

def register_local_service_handlers(registry):
    registry.register(SCHEME, handle_local_service_link)


def handle_local_service_link(url):
    kwargs = parse_local_service_url(url)
    EndpointRegistry.instance().resolve(**kwargs)


def parse_local_service_url(url):
    kwargs = urlparse.parse_qs(url[url.index(':') + 1:], keep_blank_values=True)
    return {k:(v if len(v) > 1 else v[0]) for k, v in kwargs.iteritems()}
