#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\base.py
from nodegraph.common.atom import Atom

class Event(Atom):
    __notifyevents__ = []

    def __init__(self, callback, keep_listening = False, conditions = None, **kwargs):
        self.is_active = False
        self.callback = callback
        self.keep_listening = keep_listening
        self.conditions = conditions or []

    def start(self):
        if self.is_active:
            return
        self.is_active = True
        self._register()

    def stop(self):
        if not self.is_active:
            return
        self.is_active = False
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)

    def _unregister(self):
        sm.UnregisterNotify(self)

    def invoke(self, **kwargs):
        for condition in self.conditions:
            valid = condition.validate(**kwargs)
            if not valid:
                return

        if not self.keep_listening:
            self.stop()
        self.callback(**kwargs)
