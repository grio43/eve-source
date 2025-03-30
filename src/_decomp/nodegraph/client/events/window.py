#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\window.py
from .base import Event

class WindowEvent(Event):
    atom_id = None

    @classmethod
    def get_subtitle(cls, window_id = None, **kwargs):
        return window_id


class WindowOpened(WindowEvent):
    atom_id = 92
    __notifyevents__ = ['OnWindowOpened', 'OnWindowMaximized']

    def OnWindowOpened(self, window):
        self.invoke(window_id=window.windowID)

    def OnWindowMaximized(self, window, was_minimized):
        if was_minimized:
            self.invoke(window_id=window.windowID)


class WindowClosed(WindowEvent):
    atom_id = 93
    __notifyevents__ = ['OnWindowClosed', 'OnWindowMinimized']

    def OnWindowClosed(self, window_id, window_instance_id, _window_class):
        self.invoke(window_id=window_id)

    def OnWindowMinimized(self, window):
        self.invoke(window_id=window.windowID)


class WindowOpenedOrClosed(WindowOpened, WindowClosed):
    atom_id = 292
    __notifyevents__ = WindowOpened.__notifyevents__ + WindowClosed.__notifyevents__


class WindowMaximized(WindowEvent):
    atom_id = 291
    __notifyevents__ = ['OnWindowMaximized']

    def OnWindowMaximized(self, window, was_minimized):
        self.invoke(window_id=window.windowID)


class WindowMinimized(WindowEvent):
    atom_id = 94
    __notifyevents__ = ['OnWindowMinimized']

    def OnWindowMinimized(self, window):
        self.invoke(window_id=window.windowID)


class WindowMouseEntered(WindowEvent):
    atom_id = 347
    __notifyevents__ = ['OnWindowMouseEnter']

    def OnWindowMouseEnter(self, window_id):
        self.invoke(window_id=window_id)


class WindowMouseExited(WindowEvent):
    atom_id = 348
    __notifyevents__ = ['OnWindowMouseExit']

    def OnWindowMouseExit(self, window_id):
        self.invoke(window_id=window_id)


class ViewStateChanged(Event):
    atom_id = 95
    __notifyevents__ = ['OnViewStateChanged']

    def OnViewStateChanged(self, from_view, to_view):
        self.invoke(from_view=from_view, to_view=to_view)


class OpenMap(Event):
    atom_id = 71
    __notifyevents__ = ['OnClientEvent_OpenMap']

    def OnClientEvent_OpenMap(self):
        self.invoke()
