#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\achievements\common\eventExceptionEater.py
from contextlib import contextmanager

@contextmanager
def AchievementEventExceptionEater():
    try:
        yield
    except Exception as e:
        import log
        log.LogTraceback('Failed when recording event, e = %s' % e)
