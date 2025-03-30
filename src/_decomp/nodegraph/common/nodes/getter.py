#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\getter.py
from nodegraph.common.nodes.base import Node, AtomNode
import logging
logger = logging.getLogger('node_graph')

class GetterNode(AtomNode):
    node_type_id = 30

    def __init__(self, **kwargs):
        super(GetterNode, self).__init__(**kwargs)
        self.cache_values = self.get_node_parameter_value(self.node_parameters, 'cache_values')
        try:
            self.atom = self.get_atom_class(self.atom_id)(**self.atom_parameters)
        except Exception as e:
            logger.exception('atom_id: {} | atom_parameters: {} | get_atom_class returns {} e={}'.format(self.atom_id, self.atom_parameters, self.get_atom_class(self.atom_id), e))

        self._cached_values = None

    def get_values(self):
        if self.cache_values:
            if self._cached_values is None:
                self._cached_values = self.atom.get_values()
            return self._cached_values
        else:
            return self.atom.get_values()
