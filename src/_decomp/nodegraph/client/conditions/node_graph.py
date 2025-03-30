#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\node_graph.py
from .base import Condition

class IsNodeGraphActive(Condition):
    atom_id = 486

    def __init__(self, node_graph_id = None, **kwargs):
        super(Condition, self).__init__(**kwargs)
        self.node_graph_id = self.get_atom_parameter_value('node_graph_id', node_graph_id)

    def validate(self, **kwargs):
        return self.node_graph_id in {x.graph_id for x in sm.GetService('node_graph').get_active_node_graphs().itervalues()}

    @classmethod
    def get_subtitle(cls, node_graph_id = None, **kwargs):
        return node_graph_id
