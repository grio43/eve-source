#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\const.py
from destiny import DSTBALL_FOLLOW, DSTBALL_ORBIT, DSTBALL_GOTO, DSTBALL_STOP
NAVIGATION_MODES_BY_STATE = {'Approach': [DSTBALL_FOLLOW],
 'KeepAtRange': [DSTBALL_FOLLOW],
 'Orbit': [DSTBALL_ORBIT],
 'MoveTowards': [DSTBALL_FOLLOW, DSTBALL_ORBIT],
 'MoveTowardsPoint': [DSTBALL_GOTO],
 'Align': [DSTBALL_GOTO],
 'Stop': [DSTBALL_STOP]}
