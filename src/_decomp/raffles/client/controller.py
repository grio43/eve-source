#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\controller.py
import signals
import caching
import proper
from eve.client.script.ui.control.historyBuffer import HistoryBuffer
from .storage import RaffleStorage
from .browse.controller import BrowsePageController
from .create.controller import CreatePageController
from .details.controller import DetailsPageController
from .history.controller import HistoryPageController

class RaffleWindowController(object):

    def __init__(self):
        self._storage = RaffleStorage()
        sm.GetService('raffleSvc').on_open()
        self.on_drop_item = signals.Signal(signalName='on_drop_item')
        self.on_drag_enter = signals.Signal(signalName='on_drag_enter')
        self.on_drag_exit = signals.Signal(signalName='on_drag_exit')
        self.on_focus_window = signals.Signal(signalName='on_focus_window')
        self.on_close = signals.Signal(signalName='on_close')

    def close(self):
        self.on_close()
        sm.GetService('raffleSvc').on_close()
        self._storage.close()

    def focus(self):
        self.on_focus_window()

    @caching.lazy_property
    def navigation_controller(self):
        return NavigationController()

    @caching.lazy_property
    def browse_page_controller(self):
        return BrowsePageController(self._storage)

    @caching.lazy_property
    def create_page_controller(self):
        controller = CreatePageController(storage=self._storage, focus_window=self.on_focus_window)
        self.on_close.connect(controller.close)
        self.on_drop_item.connect(controller.on_drop_item)
        self.on_drag_enter.connect(controller.on_drag_enter)
        self.on_drag_exit.connect(controller.on_drag_exit)
        return controller

    @caching.lazy_property
    def details_page_controller(self):
        return DetailsPageController(self._storage)

    @caching.lazy_property
    def history_page_controller(self):
        return HistoryPageController(self._storage)


class NavigationController(proper.Observable):

    def __init__(self, **kwargs):
        self.on_page_change = signals.Signal(signalName='on_page_change')
        self.on_focus_window = signals.Signal(signalName='on_focus_window')
        self._history = HistoryBuffer()
        super(NavigationController, self).__init__(**kwargs)

    @proper.ty(default=None)
    def page_id(self):
        pass

    @proper.ty(default=None)
    def current_page_title(self):
        pass

    @proper.alias
    def is_back_available(self):
        return self._history.IsBackEnabled()

    @proper.alias
    def is_forward_available(self):
        return self._history.IsForwardEnabled()

    def go_forward(self):
        if not self.is_forward_available:
            return
        page_id, kwargs = self._history.GoForward()
        self._change_page(page_id, append_history=False, **kwargs)

    def go_back(self):
        if not self.is_back_available:
            return
        page_id, kwargs = self._history.GoBack()
        self._change_page(page_id, append_history=False, **kwargs)

    def focus_window(self):
        self.on_focus_window()

    def open_details_page(self, raffle_id):
        self._change_page('details', raffle_id=raffle_id)

    def open_create_page(self):
        self._change_page('create')

    def open_history_page(self):
        self._change_page('history')

    def open_browse_page(self, type_id = None):
        self._change_page('browse', type_id=type_id, save_kwargs=False)

    def open_page(self, page_id):
        if page_id != self.page_id:
            self._change_page(page_id)

    def _change_page(self, page_id, append_history = True, save_kwargs = True, **kwargs):
        self.page_id = page_id
        self.current_page_title = None
        if append_history:
            if save_kwargs:
                self._history.Append((page_id, kwargs))
            else:
                self._history.Append((page_id, {}))
        self._dispatch_back_forward_available()
        self.on_page_change(page_id, **kwargs)

    def _dispatch_back_forward_available(self):
        if self.is_back_available != self._history.IsBackEnabled():
            self.dispatch('is_back_available')
        if self.is_forward_available != self._history.IsForwardEnabled():
            self.dispatch('is_forward_available')
