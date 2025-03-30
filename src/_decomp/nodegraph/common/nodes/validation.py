#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\validation.py
from nodegraph.common.nodes.base import Node, AtomNode
from nodegraph.common.nodedata import OutPort

class ValidationNode(AtomNode):
    node_type_id = 9

    def __init__(self, **kwargs):
        super(ValidationNode, self).__init__(**kwargs)
        self.atom = self.get_atom_class(self.atom_id)(**self.atom_parameters)
        self.is_not = self.get_node_parameter_value(self.node_parameters, 'is_not', False)

    def start(self, **kwargs):
        super(ValidationNode, self).start(**kwargs)
        self.mark_active()
        valid = self.atom.validate(**kwargs)
        if self.is_not:
            valid = not valid
        self.mark_inactive()
        if valid:
            self._start_connection(OutPort.on_success, **kwargs)
            return True
        else:
            self._start_connection(OutPort.on_failure, **kwargs)
            return False

    @classmethod
    def get_title(cls, node_data):
        title = super(ValidationNode, cls).get_title(node_data)
        if cls.get_node_parameter_value(node_data.nodeParameters, 'is_not'):
            return u'NOT {}'.format(title)
        return title


class ValidationGroupNode(Node):
    node_type_id = 7

    def __init__(self, **kwargs):
        super(ValidationGroupNode, self).__init__(**kwargs)
        self.require_all = self.get_node_parameter_value(self.node_parameters, 'require_all')
        self.run_all = self.get_node_parameter_value(self.node_parameters, 'run_all')

    def start(self, **kwargs):
        super(ValidationGroupNode, self).start(**kwargs)
        if self.require_all:
            valid = self._validate_all(**kwargs)
        else:
            valid = self._validate_any(**kwargs)
        if valid:
            self._start_connection(OutPort.on_success, **kwargs)
            return True
        else:
            self._start_connection(OutPort.on_failure, **kwargs)
            return False

    def _validate_any(self, **kwargs):
        any_valid = False
        for node_id in self.connections.get(OutPort.validation, []):
            valid = self.graph.start_node(node_id, **kwargs)
            if valid:
                if not self.run_all:
                    return True
                any_valid = True

        return any_valid

    def _validate_all(self, **kwargs):
        all_valid = True
        for node_id in self.connections.get(OutPort.validation, []):
            valid = self.graph.start_node(node_id, **kwargs)
            if not valid:
                if not self.run_all:
                    return False
                all_valid = False

        return all_valid

    @classmethod
    def get_subtitle(cls, node_data):
        return 'Require {} {}'.format('ALL' if cls.get_node_parameter_value(node_data.nodeParameters, 'require_all') else 'ANY', '- run all' if cls.get_node_parameter_value(node_data.nodeParameters, 'run_all') else '')
