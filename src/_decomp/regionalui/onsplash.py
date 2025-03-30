#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\onsplash.py
from regionalui import kr
import logging
log = logging.getLogger(__name__)
SPLASH_MAP = {'KR': kr.korean_splash}

def doRegionalSplash(userRegionCode):
    try:
        log.debug(u'doRegionalSplash:userRegionCode=%s', userRegionCode)
        regionalHandler = SPLASH_MAP.get(userRegionCode, None)
        if regionalHandler:
            log.debug(u'doRegionalSplash:userRegionCode=%r', regionalHandler)
            regionalHandler()
        else:
            log.debug(u'doRegionalSplash:userRegionCode No handler :D')
        log.debug(u'doRegionalSplash:done!')
    except Exception as ex:
        log.exception(u'Exception while trying to run regional (userRegionCode=%r) splash screen: %r', userRegionCode, ex)
