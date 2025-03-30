#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\service.py
import signals
import threadutils
import weakref
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from uiblinker.blinker import BlinkerType
from uiblinker.blinker.controller import BlinkerController, BlinkerChainController
from uiblinker.disposable import Disposable
from uiblinker.fsd_loader import UiBlinksData
from uiblinker.layer import get_blink_layer
from uiblinker.node_graph import NodeGraphBlinkerStore
from uiblinker.reference.path import UiPathReference
from uiblinker.reference.ui_name import UniqueNameReference

def get_service():
    from carbon.common.script.sys.serviceManager import ServiceManager
    return ServiceManager.Instance().GetService('ui_blinker')


class UiBlinkerService(Service):
    __guid__ = 'svc.ui_blinker'
    __displayname__ = 'UI Blinker'

    def __init__(self):
        super(UiBlinkerService, self).__init__()
        self._blinker_handles = weakref.WeakSet()
        self._blink_layer = None
        self._blinks_data = None
        self._debug_on_blinkers_changed = None
        self._node_graph_blinker_store = NodeGraphBlinkerStore(ui_blinker_service=self)

    @staticmethod
    def instance():
        return get_service()

    @property
    def blinks_data(self):
        if not self._blinks_data:
            self._blinks_data = UiBlinksData()
        return self._blinks_data

    def _get_blink_by_id(self, blink_id):
        return self.blinks_data.get_ui_blink_by_id(blink_id)

    def start_blinker(self, reference, blinker_type = BlinkerType.box, group = None):
        if isinstance(reference, (str, unicode)):
            reference = UiPathReference(path=reference)
        blinker = BlinkerController(ui_reference=reference, blinker_parent=self._get_blink_layer(), blinker_type=blinker_type, ui_root=uicore.desktop)
        return self._start_blinker(blinker, group)

    def _start_blinker(self, blinkerController, group = None):
        handle = Handle(blinkerController, group, finalizer=self._dispose_blinker)
        self._blinker_handles.add(handle)
        blinkerController.start()
        self._debug_notify_blinkers_changed()
        return handle

    def start_unique_name_blinker(self, reference, blinker_type = BlinkerType.box, group = None, chain_blinks = False):
        if isinstance(reference, (str, unicode)):
            reference = UniqueNameReference(unique_name=reference, chain_blinks=chain_blinks)
        blinker = BlinkerChainController(ui_reference=reference, blinker_parent=self._get_blink_layer(), blinker_type=blinker_type, ui_root=uicore.desktop)
        return self._start_blinker(blinker, group)

    def stop_all_blinkers_in_group(self, group):
        for handle in self._iter_blinker_handles():
            if handle.group == group:
                handle.stop()

    def stop_all_blinkers(self):
        for handle in self._iter_blinker_handles():
            handle.stop()

    def start_blinker_by_id(self, blink_id):
        if blink_id:
            store = self.get_node_graph_blinker_store()
            blink = self._get_blink_by_id(blink_id)
            store.start_blinker_by_path(ui_element_path=blink.uiElementPath, blinker_type=BlinkerType(blink.blinkType), seconds_til_fadeout=getattr(blink, 'secondsTilFadeout', None))

    def start_blinkers_by_id(self, blink_ids):
        if blink_ids:
            store = self.get_node_graph_blinker_store()
            for blink_id in blink_ids:
                blink = self._get_blink_by_id(blink_id)
                store.start_blinker_by_path(ui_element_path=blink.uiElementPath, blinker_type=BlinkerType(blink.blinkType), seconds_til_fadeout=getattr(blink, 'secondsTilFadeout', None))

    def stop_blinkers_by_id(self, blink_ids):
        if blink_ids:
            store = self.get_node_graph_blinker_store()
            for blink_id in blink_ids:
                blink = self._get_blink_by_id(blink_id)
                store.stop_blinker_by_path(blink.uiElementPath)

    def get_node_graph_blinker_store(self):
        return self._node_graph_blinker_store

    def _dispose_blinker(self, blinker):
        blinker.stop()
        self._debug_notify_blinkers_changed()

    def _iter_blinker_handles(self):
        pending_remove = []
        try:
            for handle in self._blinker_handles:
                if handle.disposed:
                    pending_remove.append(handle)
                else:
                    yield handle

        finally:
            for handle in pending_remove:
                self._blinker_handles.discard(handle)

    def _get_blink_layer(self):
        if self._blink_layer is None:
            self._blink_layer = get_blink_layer()
        return self._blink_layer

    def debug_get_active_blinkers(self):
        return [ BlinkerDebugEntry(handle) for handle in self._iter_blinker_handles() ]

    def debug_get_on_blinkers_changed_signal(self):
        if self._debug_on_blinkers_changed is None:
            self._debug_on_blinkers_changed = signals.Signal('debug_on_blinkers_changed')
        return self._debug_on_blinkers_changed

    @threadutils.threaded
    def _debug_notify_blinkers_changed(self):
        if self._debug_on_blinkers_changed is not None:
            self._debug_on_blinkers_changed()


class Handle(Disposable):

    def __init__(self, blinker, group, finalizer):
        self._group = group
        super(Handle, self).__init__(value=blinker, finalizer=finalizer)

    @property
    def group(self):
        return self._group

    def stop(self):
        self.dispose()


class BlinkerDebugEntry(object):

    def __init__(self, handle):
        self._handle_ref = weakref.ref(handle)

    @property
    def group(self):
        handle = self._handle_ref()
        if handle:
            return handle.group

    @property
    def reference(self):
        handle = self._handle_ref()
        if handle:
            return handle._value._ui_reference

    @property
    def blinker_type(self):
        handle = self._handle_ref()
        if handle:
            return handle._value._blinker_type

    @property
    def debug_name(self):
        reference = self.reference
        return '{} at 0x{:x}'.format(str(reference).replace('<', '&lt;'), id(reference))

    def stop(self):
        handle = self._handle_ref()
        if handle:
            handle.stop()
