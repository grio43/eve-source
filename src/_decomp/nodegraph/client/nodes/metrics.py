#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\metrics.py
from logging import getLogger
import threadutils
from nodegraph.client.metrics import publish_datapoint_event
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import OutPort
logger = getLogger(__name__)

class ReportContext(Node):
    node_type_id = 43

    def __init__(self, **kwargs):
        super(ReportContext, self).__init__(**kwargs)
        self.datapoint = self.get_node_parameter_value(self.node_parameters, 'datapoint')

    def start(self, **kwargs):
        super(ReportContext, self).start(**kwargs)
        if self.datapoint:
            self._publish_event()
        self._start_connection(OutPort.output, **kwargs)

    @threadutils.threaded
    def _publish_event(self):
        try:
            node_graph_id = int(self.graph.graph_id)
        except ValueError:
            logger.debug('Custom Node Graph Datapoint Triggered: %s', self.datapoint)
            return

        publish_datapoint_event(self.datapoint, node_graph_id)

    @classmethod
    def get_subtitle(cls, node_data):
        datapoint = cls.get_node_parameter_value(node_data.nodeParameters, 'datapoint')
        if datapoint:
            return u'{}'.format(datapoint)
        return ''
