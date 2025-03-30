#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\message_bus\event_messenger.py
from eveProto.generated.eve_public.app.eveonline.nodegraph.action.datapoint_pb2 import Triggered
from logging import getLogger
logger = getLogger(__name__)

class EventMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def datapoint_triggered(self, datapoint_name, node_graph_id):
        proto = Triggered()
        proto.datapoint_name = datapoint_name
        proto.nodegraph.sequential = int(node_graph_id)
        self.public_gateway.publish_event_payload(proto)
        logger.debug('Node Graph Datapoint Triggered: %s', datapoint_name)
