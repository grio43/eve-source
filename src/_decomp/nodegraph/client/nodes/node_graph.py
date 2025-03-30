#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\node_graph.py
import logging
import threadutils
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import OutPort
logger = logging.getLogger('node_graph')

class SendMessageToServerGraph(Node):
    node_type_id = 33

    def __init__(self, **kwargs):
        super(SendMessageToServerGraph, self).__init__(**kwargs)
        self.message_key = self.get_node_parameter_value(self.node_parameters, 'message_key')
        self.message_value = self.get_node_parameter_value(self.node_parameters, 'message_value')

    def start(self, **kwargs):
        super(SendMessageToServerGraph, self).start(**kwargs)
        self._start_thread()

    @threadutils.threaded
    def _start_thread(self, **kwargs):
        if not session.charid:
            return
        self.graph.send_message_to_server_graph(self.message_key, self.message_value)
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{}: {}'.format(cls.get_node_parameter_value(node_data.nodeParameters, 'message_key', ''), cls.get_node_parameter_value(node_data.nodeParameters, 'message_value', ''))
