#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\manager.py
import logging
log = logging.getLogger(__name__)
from regionalui import onlogin
from regionalui import onsplash

class RegionalUserInterfaceManager(object):

    def __init__(self, game_ui_service):
        self.game_ui_service = game_ui_service
        self.element_map = {}

    def on_splash_screen(self, user_session):
        try:
            log.debug(u'Runing on_splash_screen for %r', user_session)
            elements = onsplash.doRegionalSplash(user_session.countryCode)
            if elements and isinstance(elements, dict):
                self.element_map.update(elements)
        except Exception as ex:
            log.exception(u'Regional splash screen seems to have crashed: %r' % ex)

    def on_login(self, user_session):
        try:
            log.debug(u'Runing on_login for %r', user_session)
            elements = onlogin.doRegionalLogin(user_session.countryCode)
            if elements and isinstance(elements, dict):
                self.element_map.update(elements)
        except Exception as ex:
            log.exception(u'Regional login scripts seem to have crashed: %r' % ex)
