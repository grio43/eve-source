#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\kr\__init__.py
import blue
import time
from carbonui.uicore import uicore
from regionalui.kr import koreansplash
import logging
log = logging.getLogger(__name__)

def korean_splash():
    log.debug('Running Korean splash screen...')
    splash = koreansplash.KoreanSplashScreen(parent=uicore.layer.modal)
    timeout = time.time() + koreansplash.TOTAL_DURATION * 1.5
    while splash and not splash.destroyed:
        log.debug('Korean splash screen WAITING....!! :D')
        if time.time() > timeout:
            log.error('Korean splash screen Timed Out! :(')
            try:
                splash.Close()
            except Exception as ex:
                log.error('Korean splash screen force Close exception: %r', ex)

            break
        blue.pyos.synchro.SleepWallclock(100)

    log.debug('Korean splash screen DONE! :D')
