#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\utility.py
from collections import defaultdict
import uthread2
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import OutPort

class CountNode(Node):
    node_type_id = 23

    def __init__(self, **kwargs):
        super(CountNode, self).__init__(**kwargs)
        self.count = self.get_node_parameter_value(self.node_parameters, 'count')
        self.counter = 0

    def start(self, **kwargs):
        if self.counter >= self.count:
            return
        super(CountNode, self).start(**kwargs)
        self.counter += 1
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        return 'Count: {}'.format(cls.get_node_parameter_value(node_data.nodeParameters, 'count'))


class OnceNode(CountNode):
    node_type_id = 10

    def __init__(self, **kwargs):
        super(OnceNode, self).__init__(**kwargs)
        self.count = 1

    @classmethod
    def get_subtitle(cls, node_data):
        return ''


class DelayNode(Node):
    node_type_id = 17

    def __init__(self, **kwargs):
        super(DelayNode, self).__init__(**kwargs)
        self.delay = self.get_node_parameter_value(self.node_parameters, 'delay')
        self._thread = None

    def start(self, **kwargs):
        super(DelayNode, self).start(**kwargs)
        self._stop_thread()
        self._thread = uthread2.start_tasklet(self._start_thread, **kwargs)

    def stop(self, **kwargs):
        super(DelayNode, self).stop(**kwargs)
        self._stop_thread()

    def _stop_thread(self):
        if self._thread:
            self._thread.kill()
            self._thread = None

    def _start_thread(self, **kwargs):
        self.mark_active()
        uthread2.sleep(self.delay)
        self.mark_inactive()
        self._thread = None
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        return '{} sec'.format(cls.get_node_parameter_value(node_data.nodeParameters, 'delay'))


class RepeatNode(Node):
    node_type_id = 15

    def __init__(self, **kwargs):
        super(RepeatNode, self).__init__(**kwargs)
        self.repeat_count = self.get_node_parameter_value(self.node_parameters, 'repeat_count')
        self.delay = self.get_node_parameter_value(self.node_parameters, 'delay')
        self.counter = defaultdict(int)
        self._threads = {}

    def start(self, from_node_id = None, **kwargs):
        if 0 < self.repeat_count < self.counter[from_node_id]:
            return
        super(RepeatNode, self).start(**kwargs)
        if from_node_id in self._threads:
            self._threads[from_node_id].kill()
        self._threads[from_node_id] = uthread2.start_tasklet(self._start_thread, from_node_id=from_node_id, **kwargs)

    def stop(self, **kwargs):
        super(RepeatNode, self).stop(**kwargs)
        for thread in self._threads.itervalues():
            thread.kill()

        self._threads.clear()

    def _start_thread(self, from_node_id, **kwargs):
        if self.delay:
            self.mark_active()
            uthread2.sleep(self.delay)
            self.mark_inactive()
        del self._threads[from_node_id]
        self.counter[from_node_id] += 1
        self.graph.start_node(from_node_id, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        repeat_count = cls.get_node_parameter_value(node_data.nodeParameters, 'repeat_count')
        return 'Repeat:{} - Delay:{} sec'.format('infinite' if repeat_count == 0 else repeat_count, cls.get_node_parameter_value(node_data.nodeParameters, 'delay'))


class RootNode(Node):
    node_type_id = 1

    def __init__(self, **kwargs):
        super(RootNode, self).__init__(**kwargs)
        self.graph.start_active_node_ids.append(self.node_id)

    def start(self, **kwargs):
        super(RootNode, self).start(**kwargs)
        self._start_connection(OutPort.output, **kwargs)


class StopNode(Node):
    node_type_id = 24

    def start(self, **kwargs):
        super(StopNode, self).start(**kwargs)
        self._stop_connection(OutPort.nodes)
        self._start_connection(OutPort.output, **kwargs)


class RestartNode(Node):
    node_type_id = 38

    def start(self, **kwargs):
        super(RestartNode, self).start(**kwargs)
        from uthread2 import call_after_wallclocktime_delay
        self._stop_connection(OutPort.output)
        call_after_wallclocktime_delay(self._start_connection, 1.0, OutPort.output)


class IteratorNode(Node):
    node_type_id = 34

    def __init__(self, **kwargs):
        super(IteratorNode, self).__init__(**kwargs)
        self.items = self.get_node_parameter_value(self.node_parameters, 'items')
        self.index = -1

    def get_values(self):
        return {'item': self.items[self.index],
         'index': self.index}

    def _update_variables_from_connections(self):
        if self.index == -1:
            super(IteratorNode, self)._update_variables_from_connections()

    def start(self, **kwargs):
        super(IteratorNode, self).start(**kwargs)
        if self.items is None:
            return
        self._start_item_connections()

    def stop(self, **kwargs):
        super(IteratorNode, self).stop(**kwargs)
        self.index = -1

    def _start_item_connections(self):
        self.index += 1
        if self.index >= len(self.items):
            self.index = -1
            self._start_connection(OutPort.on_end)
        else:
            self._start_connection(OutPort.on_next)


class FormatString(Node):
    node_type_id = 36

    def __init__(self, **kwargs):
        super(FormatString, self).__init__(**kwargs)
        self.string_template = self.get_node_parameter_value(self.node_parameters, 'string_template')
        self.value_a = self.get_node_parameter_value(self.node_parameters, 'value_a')
        self.value_b = self.get_node_parameter_value(self.node_parameters, 'value_b')

    def get_values(self):
        return {'formatted_string': unicode(self.string_template).format(value_a=self.value_a, value_b=self.value_b)}

    @classmethod
    def get_subtitle(cls, node_data):
        return cls.get_node_parameter_value(node_data.nodeParameters, 'string_template', '')


class SyncNode(Node):
    node_type_id = 49

    def __init__(self, **kwargs):
        super(SyncNode, self).__init__(**kwargs)
        self._activated_nodes = set()

    def start(self, **kwargs):
        super(SyncNode, self).start(**kwargs)
        from_node_id = kwargs.get('from_node_id')
        if from_node_id:
            self._activated_nodes.add(from_node_id)
        if self._activated_nodes == self.input_connections:
            self._start_connection(OutPort.output, **kwargs)

    def stop(self, **kwargs):
        super(SyncNode, self).stop(**kwargs)
        self._activated_nodes.clear()


class DebounceNode(Node):
    node_type_id = 54

    def __init__(self, **kwargs):
        super(DebounceNode, self).__init__(**kwargs)
        self.wait_time = self.get_node_parameter_value(self.node_parameters, 'wait_time')
        self._thread = None

    def start(self, **kwargs):
        super(DebounceNode, self).start(**kwargs)
        if self._thread:
            self._thread.kill()
        self._thread = uthread2.start_tasklet(self._start)

    def stop(self, **kwargs):
        super(DebounceNode, self).stop(**kwargs)
        if self._thread:
            self._thread.kill()
            self._thread = None

    def _start(self):
        self.mark_active()
        uthread2.sleep(self.wait_time)
        self._start_connection(OutPort.output)
        self._thread = None
        self.mark_inactive()

    @classmethod
    def get_subtitle(cls, node_data):
        return cls.get_node_parameter_value(node_data.nodeParameters, 'wait_time', '')


class ThrottleNode(Node):
    node_type_id = 55

    def __init__(self, **kwargs):
        super(ThrottleNode, self).__init__(**kwargs)
        self.wait_time = self.get_node_parameter_value(self.node_parameters, 'wait_time')
        self._thread = None

    def start(self, **kwargs):
        super(ThrottleNode, self).start(**kwargs)
        if self._thread:
            return
        self._thread = uthread2.start_tasklet(self._start)
        self._start_connection(OutPort.output)

    def stop(self, **kwargs):
        super(ThrottleNode, self).stop(**kwargs)
        if self._thread:
            self._thread.kill()
            self._thread = None

    def _start(self):
        self.mark_active()
        uthread2.sleep(self.wait_time)
        self._thread = None
        self.mark_inactive()

    @classmethod
    def get_subtitle(cls, node_data):
        return cls.get_node_parameter_value(node_data.nodeParameters, 'wait_time', '')
