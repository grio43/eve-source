#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\util.py
from uihider import CommandBlockerService

def is_blocked(action, window_id):
    command_blocker = CommandBlockerService.instance()
    return command_blocker.is_blocked(['window', 'window.{}'.format(action), 'window.{}.{}'.format(action, window_id)])
