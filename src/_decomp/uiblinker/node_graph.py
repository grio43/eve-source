#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\node_graph.py
import collections
import weakref
from uiblinker.blinker import BlinkerType
from uiblinker.reference.path import UiPathReference
from uiblinker.reference.ui_name import UniqueNameReference
from uthread2 import call_after_wallclocktime_delay
NODE_GRAPH_BLINKER_GROUP = 'node_graph_blinkers'

class NodeGraphBlinkerStore(object):

    def __init__(self, ui_blinker_service):
        self._ui_blinker_service = ui_blinker_service
        self._blinkers = set()
        self._blinkers_by_group = collections.defaultdict(weakref.WeakSet)
        self._groups_by_blinker = weakref.WeakKeyDictionary()
        self._clear_threads = {}

    def start_blinker_by_path(self, ui_element_path, blinker_type = BlinkerType.box, group = 'global', seconds_til_fadeout = None):
        if self.reuse_existing_blinker(ui_element_path, group):
            return
        handle = self._ui_blinker_service.start_blinker(reference=UiPathReference(ui_element_path), blinker_type=blinker_type, group=NODE_GRAPH_BLINKER_GROUP)
        self._start_blinker(handle, ui_element_path, group, seconds_til_fadeout)

    def _start_blinker(self, handle, ui_element_path, group, seconds_til_fadeout):
        handle.on_disposed.connect(self._on_blinker_disposed)
        blinker = BlinkerEntry(handle=handle, ui_element_path=ui_element_path)
        self._blinkers.add(blinker)
        self._blinkers_by_group[group].add(blinker)
        self._groups_by_blinker.setdefault(blinker, set()).add(group)
        if seconds_til_fadeout:
            self._clear_threads[ui_element_path] = call_after_wallclocktime_delay(tasklet_func=self.stop_blinker_by_path, delay=seconds_til_fadeout, ui_element_path=ui_element_path)

    def reuse_existing_blinker(self, ui_element_path, group):
        blinker = self._find_blinker_by_path(ui_element_path)
        if blinker is not None:
            self._blinkers_by_group[group].add(blinker)
            self._groups_by_blinker.setdefault(blinker, set()).add(group)
            return True
        return False

    def start_blinker_by_name(self, unique_ui_name, blinker_type = BlinkerType.box, group = 'global', seconds_til_fadeout = None, chain_blinks = False):
        if self.reuse_existing_blinker(unique_ui_name, group):
            return
        handle = self._ui_blinker_service.start_unique_name_blinker(reference=UniqueNameReference(unique_ui_name, chain_blinks=chain_blinks), blinker_type=blinker_type, group=NODE_GRAPH_BLINKER_GROUP)
        self._start_blinker(handle, unique_ui_name, group, seconds_til_fadeout)

    def _schedule_stop_blinker(self, ui_element_path, seconds_til_fadeout):
        self._unschedule_stop_blinker(ui_element_path)
        self._clear_threads[ui_element_path] = call_after_wallclocktime_delay(tasklet_func=self.stop_blinker_by_path, delay=seconds_til_fadeout, ui_element_path=ui_element_path)

    def _unschedule_stop_blinker(self, ui_element_path):
        if ui_element_path in self._clear_threads:
            self._clear_threads[ui_element_path].kill()
            self._clear_threads[ui_element_path] = None

    def stop_blinker_by_path(self, ui_element_path, group = 'global'):
        blinker = self._find_blinker_by_path(ui_element_path)
        if blinker is not None:
            self._stop_blinker(blinker, group)

    def stop_all_blinkers_in_group(self, group):
        for blinker in list(self._blinkers_by_group[group]):
            self._stop_blinker(blinker, group)

    def stop_all_blinkers(self):
        for blinker in self._iter_blinkers():
            blinker.handle.stop()

    def _stop_blinker(self, blinker, group):
        self._blinkers_by_group[group].discard(blinker)
        groups = self._groups_by_blinker.get(blinker, set())
        groups.discard(group)
        if len(groups) == 0:
            blinker.handle.stop()
        self._unschedule_stop_blinker(blinker.ui_element_path)

    def _on_blinker_disposed(self, handle):
        blinker = self._find_blinker_by_handle(handle)
        if blinker is None:
            return
        self._blinkers.discard(blinker)
        groups = self._groups_by_blinker.get(blinker, set())
        for group in groups:
            self._blinkers_by_group[group].discard(blinker)

        groups.clear()

    def _find_blinker_by_path(self, ui_element_path):
        for blinker in self._iter_blinkers():
            if blinker.ui_element_path == ui_element_path:
                return blinker

    def _find_blinker_by_handle(self, handle):
        for blinker in self._iter_blinkers():
            if blinker.handle == handle:
                return blinker

    def _iter_blinkers(self):
        pending_remove = []
        try:
            for blinker in self._blinkers:
                if blinker.handle.disposed:
                    pending_remove.append(blinker)
                yield blinker

        finally:
            for blinker in pending_remove:
                self._blinkers.discard(blinker)


class BlinkerEntry(object):

    def __init__(self, handle, ui_element_path):
        self.handle = handle
        self.ui_element_path = ui_element_path
