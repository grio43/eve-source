#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\qa.py
from logging import getLogger
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import OutPort
logger = getLogger('node_graph')

class BaseTestTrackerNode(Node):
    node_type_id = None
    MESSAGE_KEY = ''

    def __init__(self, **kwargs):
        super(BaseTestTrackerNode, self).__init__(**kwargs)
        self.step = self.get_node_parameter_value(self.node_parameters, 'step')

    def start(self, **kwargs):
        super(BaseTestTrackerNode, self).start(**kwargs)
        self._notify_client()
        self._send_message_to_graph()
        self._log()
        self._start_connection(OutPort.output, **kwargs)

    def _send_message_to_graph(self):
        self.graph.context.send_message(self.MESSAGE_KEY, self.step)

    def _notify_client(self):
        raise NotImplementedError('Must implement _notify_client in derived class')

    def _log(self):
        raise NotImplementedError('Must implement _log in derived class')

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{step}'.format(step=cls.get_node_parameter_value(node_data.nodeParameters, 'step', 'MISSING step'))


class TestStartedNode(BaseTestTrackerNode):
    node_type_id = 50
    MESSAGE_KEY = 'test_started'

    def __init__(self, **kwargs):
        super(TestStartedNode, self).__init__(**kwargs)
        self.timeout = self.get_node_parameter_value(self.node_parameters, 'timeout')

    def _notify_client(self):
        from nodditests.common.tracker import TestTracker
        TestTracker().start_test(self.step, self.timeout)

    def _log(self):
        logger.debug('Test Started: {}'.format(self.step))


class TestSucceededNode(BaseTestTrackerNode):
    node_type_id = 46
    MESSAGE_KEY = 'test_succeeded'

    def _notify_client(self):
        from nodditests.common.tracker import TestTracker
        TestTracker().pass_test(self.step)

    def _log(self):
        logger.debug('Test Succeeded: {}'.format(self.step))


class TestFailedNode(BaseTestTrackerNode):
    node_type_id = 47
    MESSAGE_KEY = 'test_failed'

    def __init__(self, **kwargs):
        super(TestFailedNode, self).__init__(**kwargs)
        self.reason = self.get_node_parameter_value(self.node_parameters, 'reason')

    def _notify_client(self):
        from nodditests.common.tracker import TestTracker
        TestTracker().fail_test(self.step, self.reason)

    def _log(self):
        logger.debug('Test Failed: {} - {}'.format(self.step, self.reason))

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{step}: {reason}'.format(step=cls.get_node_parameter_value(node_data.nodeParameters, 'step', 'MISSING step'), reason=cls.get_node_parameter_value(node_data.nodeParameters, 'reason', 'MISSING reason'))


class TestLogMetadataNode(BaseTestTrackerNode):
    node_type_id = 57

    def __init__(self, **kwargs):
        super(TestLogMetadataNode, self).__init__(**kwargs)
        self.key = self.get_node_parameter_value(self.node_parameters, 'key')
        self.value = self.get_node_parameter_value(self.node_parameters, 'value')

    def _send_message_to_graph(self):
        pass

    def _notify_client(self):
        from nodditests.common.tracker import TestTracker
        TestTracker().log_test_metadata(self.step, self.key, self.value)

    def _log(self):
        logger.debug('Test Metadata: {} - {} ({})'.format(self.key, self.value, self.step))

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{key}: {value} ({step})'.format(key=cls.get_node_parameter_value(node_data.nodeParameters, 'key', 'MISSING key'), value=cls.get_node_parameter_value(node_data.nodeParameters, 'value', 'MISSING value'), step=cls.get_node_parameter_value(node_data.nodeParameters, 'step', 'MISSING step'))
