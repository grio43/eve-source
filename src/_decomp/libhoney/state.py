#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\state.py
import logging
G_CLIENT = None
WARNED_UNINITIALIZED = False

def warn_uninitialized():
    global WARNED_UNINITIALIZED
    log = logging.getLogger(__name__)
    if not WARNED_UNINITIALIZED:
        log.warn('global libhoney method used before initialization')
        WARNED_UNINITIALIZED = True
