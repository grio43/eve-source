#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\link.py
try:
    import localization
except ImportError:
    localization = None

SCHEME = 'redeem'

def format_open_redeem_queue_url():
    return u'<a href="{}:">{}</a>'.format(SCHEME, localization.GetByLabel('Notifications/RedeemingQueue'))
