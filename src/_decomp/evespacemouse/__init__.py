#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evespacemouse\__init__.py
import logging
import blue
import localization
import spacemouse
import trinity
import uthread2
_isEnabled = False
_listeners = []
_position = (0, 0, 0)
_rotation = (0, 0, 0)

class ActionGroup(object):

    def __init__(self, uid, label, children = ()):
        self.uid = uid
        self.label = localization.GetByLabel(label).encode('utf8')
        self.children = list(children)

    def GetTuple(self):
        return (self.uid,
         self.label,
         '',
         [ x.GetTuple() for x in self.children ])


class ActionSet(ActionGroup):
    pass


class Action(object):

    def __init__(self, uid, label, description = ''):
        self.uid = uid
        self.label = localization.GetByLabel(label).encode('utf8')
        self.description = localization.GetByLabel(description).encode('utf8') if description else ''

    def GetTuple(self):
        return (self.uid, self.label, self.description)


def Enable():
    global _isEnabled
    if _isEnabled:
        return
    title = localization.GetByLabel('UI/SystemMenu/AboutEve/ReleaseTitle').encode('utf8')
    try:
        spacemouse.RegisterWindow(title, trinity.app.hwnd, _OnSpaceMousePosition, _OnSpaceMouseAction)
    except RuntimeError:
        return

    _isEnabled = True
    logging.debug('Registered window with space mouse driver')


def Disable():
    global _isEnabled
    if _isEnabled:
        return
    spacemouse.UnRegisterWindow(trinity.app.hwnd)
    _isEnabled = False
    del _listeners[:]


def IsEnabled():
    return _isEnabled


class _Listener(object):

    def __init__(self, onPosition, onAction, priority = 0):
        self.onPosition = onPosition
        self.onAction = onAction
        self.priority = priority

    def __eq__(self, other):
        return self.onPosition == other.onPosition and self.onAction == other.onAction

    def __cmp__(self, other):
        return -cmp(self.priority, other.priority)


def StartListening(actions, onPosition, onAction, priority = 0):
    if not _isEnabled:
        return
    if actions:
        spacemouse.AddActionSet(trinity.app.hwnd, actions.GetTuple())
        spacemouse.ActivateActionSet(trinity.app.hwnd, actions.uid)
    listener = _Listener(onPosition, onAction, priority)
    try:
        _listeners[_listeners.index(listener)] = listener
    except ValueError:
        _listeners.append(listener)

    _listeners.sort()
    if len(_listeners) == 1:
        uthread2.StartTasklet(_CallListeners)


class StopPropagation(Exception):
    pass


def _CallListeners():
    global _rotation
    global _position
    prevTime = blue.os.GetWallclockTime()
    while _listeners:
        uthread2.Yield()
        nowTime = blue.os.GetWallclockTime()
        dt = blue.os.TimeAsDouble(nowTime - prevTime)
        prevTime = nowTime
        for listener in _listeners:
            if listener.onPosition:
                try:
                    listener.onPosition(dt, _position, _rotation)
                except StopPropagation:
                    break
                except BaseException:
                    logging.exception('Exception when executing space mouse position listener')


def StopListening(onPosition, onAction):
    try:
        _listeners.remove(_Listener(onPosition, onAction))
    except ValueError:
        return

    _listeners.sort()


def _OnSpaceMousePosition(tx, ty, tz, rx, ry, rz):
    global _rotation
    global _position
    _position = (tx, ty, tz)
    _rotation = (rx, ry, rz)


def _OnSpaceMouseAction(name):
    try:
        for listener in _listeners:
            if listener.onAction:
                try:
                    listener.onAction(name)
                except StopPropagation:
                    break
                except BaseException:
                    logging.exception('Exception when executing space mouse action listener')

    except:
        logging.exception('Exception when executing space mouse action listener')
