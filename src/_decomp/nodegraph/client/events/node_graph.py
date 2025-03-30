#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\node_graph.py
from .base import Event

class NodeGraphStateChanged(Event):
    atom_id = 487
    __notifyevents__ = ['OnNodeGraphStarted', 'OnNodeGraphStopped']

    def OnNodeGraphStarted(self, instance_id, node_graph_id):
        self.invoke(node_graph_id=node_graph_id)

    def OnNodeGraphStopped(self, instance_id, node_graph_id):
        self.invoke(node_graph_id=node_graph_id)
