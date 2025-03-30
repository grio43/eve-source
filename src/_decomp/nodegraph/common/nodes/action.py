#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\action.py
import uthread2
from nodegraph.common.nodes.base import AtomNode
from nodegraph.common.nodedata import OutPort

class ActionNode(AtomNode):
    node_type_id = 4

    def __init__(self, **kwargs):
        super(ActionNode, self).__init__(**kwargs)
        self.track_action = self.get_node_parameter_value(self.node_parameters, 'track_action')
        if self.track_action:
            on_end = self._on_action_ended
        else:
            on_end = None
        action_class = self.get_atom_class(self.atom_id)
        self.atom = action_class(on_end=on_end, **self.atom_parameters)
        self._thread = None
        self._cached_output = {}

    def get_values(self):
        return self._cached_output

    def start(self, **kwargs):
        super(ActionNode, self).start(**kwargs)
        self._stop_thread()
        self._thread = uthread2.start_tasklet(self._start_thread, **kwargs)

    def stop(self, **kwargs):
        super(ActionNode, self).stop(**kwargs)
        self._stop_thread()
        if self.track_action:
            self.atom.stop()
        self.mark_inactive()

    def _stop_thread(self):
        if self._thread:
            self._thread.kill()
            self._thread = None

    def _start_thread(self, **kwargs):
        if self.track_action:
            self.mark_active()
        if self.atom:
            result = self.atom.start(**kwargs)
            if result:
                kwargs.update(result)
                self._cached_output = kwargs
        self._thread = None
        self._start_connection(OutPort.output, **kwargs)

    def _on_action_ended(self):
        self.mark_inactive()
