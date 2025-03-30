#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\onlogin.py
from regionalui import addictionwarningtimer
import logging
log = logging.getLogger(__name__)

def doRegionalLogin(userRegionCode):
    try:
        log.debug(u'doRegionalLogin:userRegionCode=%s', userRegionCode)
        if userRegionCode == 'KR':
            return {'addictionwarningtimer': addictionwarningtimer.AddictionWarningTimer()}
    except Exception as ex:
        log.exception(u'Exception while trying to run regional (userRegionCode=%r) on-login scripts: %r', userRegionCode, ex)

    return {}
