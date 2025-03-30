#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\podGuide\link.py
from eve.client.script.ui.podGuide.podGuideUtil import OpenPodGuide, GetTermShortText
import localization
SCHEME_POD_GUIDE = 'podGuideLink'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_POD_GUIDE, handler=handle_pod_guide_link, hint=get_pod_guide_hint)


def handle_pod_guide_link(url):
    pod_guide_id = parse_pod_guide_url(url)
    OpenPodGuide(pod_guide_id)


def get_pod_guide_hint(url):
    pod_guide_id = parse_pod_guide_url(url)
    return localization.GetByMessageID(GetTermShortText(pod_guide_id))


def parse_pod_guide_url(url):
    pod_guide_id = int(url.split(':')[1])
    return pod_guide_id


def format_pod_guide_url(pod_guide_id):
    return u'{}:{}'.format(SCHEME_POD_GUIDE, pod_guide_id)
