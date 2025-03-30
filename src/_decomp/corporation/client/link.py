#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\link.py
import evelink
SCHEME_RECRUITMENT_AD = 'recruitmentAd'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_RECRUITMENT_AD, handler=handle_recruitment_ad_link, hint='UI/Corporations/CorporationWindow/Recruitment/OpenCorpAd')


def handle_recruitment_ad_link(url):
    corp_id, ad_id = parse_recruitment_ad_url(url)
    sm.GetService('corp').OpenCorpAdInNewWindow(corp_id, ad_id)


def parse_recruitment_ad_url(url):
    corp_id, ad_id = url[url.index(':') + 1:].split('//')
    return (int(corp_id), int(ad_id))


def recruitment_ad_link(corp_id, ad_id, title):
    text = u'{} - {}'.format(cfg.eveowners.Get(corp_id).name, title)
    return evelink.Link(url=format_recruitment_ad_url(corp_id, ad_id), text=text)


def format_recruitment_ad_url(corp_id, ad_id):
    return u'{}:{}//{}'.format(SCHEME_RECRUITMENT_AD, corp_id, ad_id)
