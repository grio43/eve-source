#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\lib\signal.py
import sys
if sys.platform != 'PS3':
    raise RuntimeError('This is not the proper signal module!')
