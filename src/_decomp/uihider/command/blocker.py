#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\command\blocker.py
import weakref
from collections import OrderedDict
import signals
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceManager import ServiceManager
from uihider.qa import is_command_blocker_override_enabled, notify_command_block_overridden

class CommandBlockerService(Service):
    __guid__ = 'svc.command_blocker'
    __displayname__ = 'Command Blocker'
    __servicename__ = 'command_blocker'
    __notifyevents__ = ['OnSessionReset']

    @staticmethod
    def instance():
        service_manager = ServiceManager.Instance()
        return service_manager.GetService(CommandBlockerService.__servicename__)

    def is_blocked(self, references):
        if isinstance(references, (str, unicode)):
            references = [references]
        blocked = self.blocker.is_blocked(references)
        if blocked and is_command_blocker_override_enabled():
            notify_command_block_overridden(references)
            return False
        return blocked

    def is_unblocked(self, references):
        if isinstance(references, (str, unicode)):
            references = [references]
        return not self.is_blocked(references)

    def block(self, references):
        if isinstance(references, (str, unicode)):
            references = [references]
        return self.blocker.block(references)

    def unblock(self, references):
        if isinstance(references, (str, unicode)):
            references = [references]
        return self.blocker.unblock(references)

    def subscribe(self, callback):
        self.blocker.on_changed.connect(callback)

    def unsubscribe(self, callback):
        self.blocker.on_changed.disconnect(callback)

    def _initialize(self):
        self.blocker = CommandBlocker()

    def _reset(self):
        self.blocker.clear()
        self._initialize()

    def Run(self, memStream = None):
        super(CommandBlockerService, self).Run(memStream)
        self._initialize()

    def OnSessionReset(self):
        self._reset()


class CommandBlocker(object):

    def __init__(self):
        self.layers = OrderedDict()
        self.on_changed = signals.Signal('CommandBlocker.on_changed')
        self._next_handle = 0

    def block(self, references):
        handle = self._allocate_handle()
        self.layers[handle] = BlockLayer(references=references, block_status=BlockStatus.blocked)
        self.on_changed()
        return BlockToken(self, handle)

    def unblock(self, references):
        handle = self._allocate_handle()
        self.layers[handle] = BlockLayer(references=references, block_status=BlockStatus.unblocked)
        self.on_changed()
        return BlockToken(self, handle)

    def is_blocked(self, references):
        for layer in reversed(self.layers.values()):
            if layer.specifies(references):
                return layer.is_blocked(references)

        return False

    def unblock_with_handle(self, handle):
        try:
            del self.layers[handle]
            self.on_changed()
        except KeyError:
            pass

    def clear(self):
        self.layers.clear()
        self.on_changed()

    def _allocate_handle(self):
        handle = self._next_handle
        self._next_handle += 1
        return handle


class BlockLayer(object):

    def __init__(self, references, block_status):
        self.references = set(references)
        self.block_status = block_status

    def specifies(self, references):
        return bool(self.references.intersection(references))

    def is_blocked(self, references):
        if self.specifies(references):
            return self.block_status == BlockStatus.blocked
        else:
            return False


class BlockStatus(object):
    unblocked = 1
    blocked = 2


class BlockToken(object):

    def __init__(self, blocker, handle):
        self.blocker_ref = weakref.ref(blocker)
        self.handle = handle
        self.disposed = False

    def dispose(self):
        if not self.disposed:
            blocker = self.blocker_ref()
            if blocker:
                blocker.unblock_with_handle(self.handle)
            self.disposed = True

    def __del__(self):
        self.dispose()
