#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\metrics.py
from carbon.common.script.sys.serviceManager import ServiceManager
from logging import getLogger
from nodegraph.client.message_bus.event_messenger import EventMessenger
logger = getLogger(__name__)

def publish_datapoint_event(datapoint, node_graph_id):
    sm = ServiceManager.Instance()
    public_gateway = sm.GetService('publicGatewaySvc')
    event_messenger = EventMessenger(public_gateway)
    event_messenger.datapoint_triggered(datapoint, node_graph_id)
    logger.debug('Node Graph Datapoint Triggered: %s', datapoint)
