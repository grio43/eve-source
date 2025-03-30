#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\format\local_service.py
import urllib
from evelink.link import Link
SCHEME = 'localsvc'

def local_service_link(method, text, **kwargs):
    return Link(url=format_local_service_url(method, **kwargs), text=text)


def format_local_service_url(method, **kwargs):
    kwargs['method'] = method
    return u'{}:{}'.format(SCHEME, urllib.urlencode(kwargs))
