#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\ui.py
from carbonui.control.window import Window
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.ui.objective_task_widget import ButtonTaskWidget

class OpenWindowTask(ObjectiveTask):
    objective_task_content_id = 37
    WIDGET = None
    BUTTON_WIDGET = ButtonTaskWidget

    def __init__(self, window_id = None, **kwargs):
        super(OpenWindowTask, self).__init__(**kwargs)
        self._window_id = None
        self._window = None
        from nodegraph.client.events.window import WindowOpenedOrClosed
        self._event = WindowOpenedOrClosed(callback=self._window_opened_closed, keep_listening=True)
        self.window_id = window_id

    @property
    def window_id(self):
        return self._window_id

    @window_id.setter
    def window_id(self, value):
        if self._window_id == value:
            return
        self._window_id = value
        self._window = _get_window_class(self._window_id)
        if self._window:
            self._title = self._window._GetDefaultCaption()
        else:
            self._title = '-'
        self.update()

    def double_click(self):
        if self._window:
            self._window.Open()

    def _update(self):
        super(OpenWindowTask, self)._update()
        window = Window.GetIfOpen(self._window_id)
        self.completed = window and not window.IsMinimized()

    def _window_opened_closed(self, **kwargs):
        self._update()

    def _register(self):
        super(OpenWindowTask, self)._register()
        self._event.start()

    def _unregister(self):
        super(OpenWindowTask, self)._unregister()
        self._event.stop()


def _get_window_class(window_id):
    if not window_id:
        return
    from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataRaw import BTNDATARAW_BY_ID
    if window_id in BTNDATARAW_BY_ID:
        window_class = BTNDATARAW_BY_ID[window_id].wndCls
        if window_class:
            return window_class
    for window in Window.__subclasses__():
        if window_id == getattr(window, 'default_windowID', None):
            return window
