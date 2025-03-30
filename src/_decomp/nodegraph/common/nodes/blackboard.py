#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\nodes\blackboard.py
from ast import literal_eval
import threadutils
from nodegraph.common.nodedata import OutPort
from nodegraph.common.nodes.base import Node
from nodegraph.common.util import compare_values, get_object_value_by_path, set_object_value_by_path

class BlackboardEventNode(Node):
    node_type_id = 21

    def __init__(self, **kwargs):
        super(BlackboardEventNode, self).__init__(**kwargs)
        self.blackboard_key = self.get_node_parameter_value(self.node_parameters, 'blackboard_key')
        self.keep_listening = self.get_node_parameter_value(self.node_parameters, 'keep_listening')
        self.validate_on_start = self.get_node_parameter_value(self.node_parameters, 'validate_on_start')

    def get_values(self):
        return {'blackboard_value': self.graph.context.get_value(self.blackboard_key)}

    def start(self, **kwargs):
        if self.is_active:
            return
        super(BlackboardEventNode, self).start(**kwargs)
        self.mark_active()
        self.graph.context.subscribe_to_value(self.blackboard_key, self._value_changed)
        if self.validate_on_start:
            self._value_changed(self.blackboard_key, self.graph.context.get_value(self.blackboard_key))

    def stop(self, **kwargs):
        if not self.is_active:
            return
        super(BlackboardEventNode, self).stop(**kwargs)
        self.graph.context.unsubscribe_from_value(self.blackboard_key, self._value_changed)
        self.mark_inactive()

    @threadutils.threaded
    def _value_changed(self, key, value, *args, **kwargs):
        valid = True
        kwargs['from_node_id'] = self.node_id
        kwargs[key] = value
        validators = self.connections.get(OutPort.validation, [])
        for node_id in validators:
            valid_node = self.graph.start_node(node_id, **kwargs)
            if valid_node is False:
                valid = False
                break

        if not valid:
            return
        if not self.keep_listening:
            self.stop()
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        result = [cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_key') or '']
        if cls.get_node_parameter_value(node_data.nodeParameters, 'keep_listening'):
            result.append('KeepListening')
        if cls.get_node_parameter_value(node_data.nodeParameters, 'validate_on_start'):
            result.append('ValidateOnStart')
        return ' - '.join(result)


class BlackboardValidationNode(Node):
    node_type_id = 22

    def __init__(self, **kwargs):
        super(BlackboardValidationNode, self).__init__(**kwargs)
        self.blackboard_key = self.get_node_parameter_value(self.node_parameters, 'blackboard_key')
        self.blackboard_value = self.get_node_parameter_value(self.node_parameters, 'blackboard_value')
        self.object_path = self.get_node_parameter_value(self.node_parameters, 'object_path')
        self.operator = self.get_node_parameter_value(self.node_parameters, 'operator')
        self.flipped = self.get_node_parameter_value(self.node_parameters, 'flipped')

    def get_values(self):
        blackboard_value = get_blackboard_value(context=self.graph.context, key=self.blackboard_key, path=self.object_path)
        return {'blackboard_value': blackboard_value}

    def start(self, **kwargs):
        super(BlackboardValidationNode, self).start(**kwargs)
        blackboard_value = get_blackboard_value(context=self.graph.context, key=self.blackboard_key, path=self.object_path)
        valid = compare_values(value_a=blackboard_value, value_b=self.blackboard_value, operator=self.operator, flipped=self.flipped)
        if valid:
            self._start_connection(OutPort.on_success, **kwargs)
            return True
        else:
            self._start_connection(OutPort.on_failure, **kwargs)
            return False

    @classmethod
    def get_subtitle(cls, node_data):
        blackboard_key = cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_key')
        if blackboard_key:
            flipped = cls.get_node_parameter_value(node_data.nodeParameters, 'flipped')
            object_path = cls.get_node_parameter_value(node_data.nodeParameters, 'object_path')
            if object_path:
                blackboard_key = u'{}.{}'.format(blackboard_key, object_path)
            return u'{} {} {} {}'.format(blackboard_key, cls.get_node_parameter_value(node_data.nodeParameters, 'operator'), cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_value'), '(flipped)' if flipped else '')
        return ''


class BlackboardWriteNode(Node):
    node_type_id = 19

    def __init__(self, **kwargs):
        super(BlackboardWriteNode, self).__init__(**kwargs)
        self.blackboard_key = self.get_node_parameter_value(self.node_parameters, 'blackboard_key')
        self.blackboard_value = self.get_node_parameter_value(self.node_parameters, 'blackboard_value')
        self.object_path = self.get_node_parameter_value(self.node_parameters, 'object_path')
        self.force_scatter = self.get_node_parameter_value(self.node_parameters, 'force_scatter')

    def get_values(self):
        blackboard_value = get_blackboard_value(context=self.graph.context, key=self.blackboard_key, path=self.object_path)
        return {'blackboard_value': blackboard_value}

    def start(self, **kwargs):
        super(BlackboardWriteNode, self).start(**kwargs)
        if not self.blackboard_key:
            return
        if self.blackboard_value is not None:
            if isinstance(self.blackboard_value, (str, unicode)):
                try:
                    value = literal_eval(self.blackboard_value)
                except:
                    value = self.blackboard_value

            else:
                value = self.blackboard_value
        else:
            value = None
        force_update = self.force_scatter
        if self.object_path:
            blackboard_value = self.graph.context.get_value(self.blackboard_key)
            current_value = get_object_value_by_path(blackboard_value, self.object_path)
            if current_value != value:
                force_update = True
            value = set_object_value_by_path(blackboard_value, self.object_path, value)
        self.graph.context.update_value(self.blackboard_key, value, force_update=force_update)
        self._start_connection(OutPort.output, **kwargs)

    @classmethod
    def get_subtitle(cls, node_data):
        blackboard_key = cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_key', '')
        blackboard_value = cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_value')
        object_path = cls.get_node_parameter_value(node_data.nodeParameters, 'object_path', '')
        if object_path:
            blackboard_key = u'{}.{}'.format(blackboard_key, object_path)
        if blackboard_value:
            return u'{}={}'.format(blackboard_key, blackboard_value)
        input_key = cls.get_node_parameter_value(node_data.nodeParameters, 'input_key')
        if input_key:
            return u'{}->{}'.format(input_key, blackboard_key)
        return blackboard_key


class BlackboardReadNode(Node):
    node_type_id = 18

    def __init__(self, **kwargs):
        super(BlackboardReadNode, self).__init__(**kwargs)
        self.blackboard_key = self.get_node_parameter_value(self.node_parameters, 'blackboard_key')
        self.object_path = self.get_node_parameter_value(self.node_parameters, 'object_path')
        self.default_value = self.get_node_parameter_value(self.node_parameters, 'default_value')

    def get_values(self):
        blackboard_value = get_blackboard_value(context=self.graph.context, key=self.blackboard_key, path=self.object_path, default_value=self.default_value)
        return {'blackboard_value': blackboard_value}

    @classmethod
    def get_subtitle(cls, node_data):
        return u'{} {} {}'.format(cls.get_node_parameter_value(node_data.nodeParameters, 'blackboard_key', ''), cls.get_node_parameter_value(node_data.nodeParameters, 'object_path', ''), cls.get_node_parameter_value(node_data.nodeParameters, 'default_value', ''))


def get_blackboard_value(context, key, path = None, default_value = None):
    blackboard_value = context.get_value(key)
    if path is not None:
        blackboard_value = get_object_value_by_path(blackboard_value, path, default_value)
    if blackboard_value is None:
        return default_value
    return blackboard_value
