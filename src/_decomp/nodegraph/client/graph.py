#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\graph.py
from logging import getLogger
from nodegraph.common.graph import BaseNodeGraph
from nodegraph.client.nodes import get_node_class
logger = getLogger(__name__)

class ClientNodeGraph(BaseNodeGraph):

    def send_message_to_server_graph(self, message_key, message_value):
        if not message_key.startswith('client_'):
            raise ValueError('Incorrect format of client->server graph message')
        server_graph_instance_id = self.context.get_value('server_graph_instance_id')
        logger.debug('send_message_to_server_graph server_instance=%s key=%s value=%s', server_graph_instance_id, message_key, message_value)
        if server_graph_instance_id:
            sm.RemoteSvc('node_graph').process_client_graph_message(self.graph_id, server_graph_instance_id, message_key, message_value)

    def _get_node_class(self, node_type):
        return get_node_class(node_type)
