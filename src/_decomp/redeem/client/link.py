#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\client\link.py
from redeem.link import SCHEME

def register_link_handlers(registry):
    registry.register(SCHEME, handle_redeem_link, hint='UI/FastCheckout/OpenRedeemingQueue')


def handle_redeem_link(url):
    sm.GetService('redeem').OpenRedeemWindow()
