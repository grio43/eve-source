#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\loaders\fsd_behavior_loader.py
from collections import namedtuple
from behaviors import BehaviortreeStorage
from behaviors.behaviortree import BehaviorTree
from behaviors.loaders import BehaviorDoesNotExistError, IncompatibleScopeTypeError, TaskAttributeMissingError
from behaviors.registry import get_task_registry
from ccpProfile import TimedFunction
from functoolsext import lru_cache
import logging
logger = logging.getLogger(__name__)
EMPTY_LIST = []

class CircularReferenceError(Exception):
    pass


def get_parameter_name(attribute_name):
    return attribute_name.split('.')[1]


def get_behavior_tree_data(behavior_id, scope_type):
    storage = BehaviortreeStorage()
    try:
        behavior_tree_data = storage.get(behavior_id)
    except ValueError:
        raise BehaviorDoesNotExistError()

    if behavior_tree_data is None:
        raise BehaviorDoesNotExistError()
    if scope_type and scope_type != behavior_tree_data['scopeType']:
        raise IncompatibleScopeTypeError()
    return behavior_tree_data


def get_id_and_names_by_scope(scope_type):
    storage = BehaviortreeStorage()
    ids_and_names = []
    for behavior_id in storage:
        behavior_tree_data = storage[behavior_id]
        if behavior_tree_data.get('scopeType', None) != scope_type:
            continue
        ids_and_names.append((str(behavior_id), '[FSD] %s (%d)' % (behavior_tree_data.get('name', '<Unnamed FSD Behavior>'), behavior_id)))

    return ids_and_names


def get_attributes_with_overrides(node, overrides_by_uuid):
    task_uuid = node.get('uuid', None)
    overrides = overrides_by_uuid.get(task_uuid, {})
    attributes = node['attributes'].copy()
    for attribute_name, attribute_value in overrides.iteritems():
        attributes[attribute_name] = attribute_value

    return attributes


def get_attribute_overrides_by_uuid(parameter_overrides, parameters_values):
    overrides_by_uuid = {}
    for parameter in parameter_overrides:
        for override in parameter['attributeOverrideList']:
            task_uuid = override['taskUuid']
            if task_uuid not in overrides_by_uuid:
                overrides_by_uuid[task_uuid] = {}
            attribute_name = override['attributeName']
            parameter_name = parameter['parameterName']
            if parameter_name in parameters_values:
                overrides_by_uuid[task_uuid][attribute_name] = parameters_values[parameter_name]

    return overrides_by_uuid


def get_parameter_values_with_overrides(parameters, overrides):
    if not overrides:
        return parameters
    updated_parameters = parameters.copy()
    logger.debug('applying overrides to %s with overrides %s', parameters, overrides)
    for parameter_name, parameter_value in overrides.iteritems():
        if '.' not in parameter_name:
            continue
        updated_parameters[get_parameter_name(parameter_name)] = parameter_value

    return updated_parameters


class FsdBehaviorLoader(object):

    def __init__(self):
        self.registry = get_task_registry()
        self.attribute_tuple_by_task_class = {}
        self._subtree_stack = []

    @TimedFunction('behaviors::loaders::FsdBehaviorLoader::load')
    def load(self, behavior_id, scope_type = None):
        logger.debug('loading behavior tree %s with with scope type %s', behavior_id, scope_type)
        behavior_tree_data = get_behavior_tree_data(behavior_id, scope_type)
        root_node = behavior_tree_data['root']
        tree = BehaviorTree(behaviorId=behavior_id, scopeType=scope_type)
        self._subtree_stack = []
        root_task = self._instantiate_tree(root_node, {})
        tree.StartRootTask(root_task)
        return tree

    @TimedFunction('behaviors::loaders::FsdBehaviorLoader::load_reference_subtree')
    def load_reference_subtree(self, behavior_id, scope_type, parameters_values):
        if behavior_id in self._subtree_stack:
            raise CircularReferenceError('Detected circular references while loading subtree %s. Stack was %s' % (behavior_id, self._subtree_stack))
        self._subtree_stack.append(behavior_id)
        logger.debug('loading subtree %s with parameter values %s', behavior_id, parameters_values)
        behavior_tree_data = get_behavior_tree_data(behavior_id, scope_type)
        root_node = behavior_tree_data['root']
        parameter_overrides = behavior_tree_data.get('parameters', [])
        overrides_by_uuid = get_attribute_overrides_by_uuid(parameter_overrides, parameters_values)
        root_task = self._instantiate_tree(root_node, overrides_by_uuid)
        self._subtree_stack.pop()
        return root_task

    @TimedFunction('behaviors::loaders::FsdBehaviorLoader::_instantiate_tree')
    def _instantiate_tree(self, node, overrides_by_uuid):
        task_name = node['taskClass']
        task_class = self.get_task_class(task_name)
        attributes = self._get_task_attributes(node, task_name, overrides_by_uuid)
        task = task_class(attributes)
        if task_name.endswith('ReferenceSubtree'):
            subtree_id = attributes.behaviorTreeId
            parameter_values = get_parameter_values_with_overrides(attributes.parameters, overrides_by_uuid.get(node['uuid']))
            task = self.load_reference_subtree(subtree_id, None, parameter_values)
        else:
            self._instantiate_child_tasks(node, task, overrides_by_uuid)
        return task

    def _instantiate_child_tasks(self, node, task, overrides_by_uuid):
        for child_node in node.get('subTasks', EMPTY_LIST):
            child_task = self._instantiate_tree(child_node, overrides_by_uuid)
            task.AddSubTask(child_task)

    def _get_task_attributes(self, node, task_name, overrides_by_uuid):
        attribute_wrapper = self._get_attribute_wrapper(task_name)
        node_attributes = get_attributes_with_overrides(node, overrides_by_uuid)
        try:
            attributes = attribute_wrapper(**self._get_converted_attributes(task_name, attribute_wrapper, node_attributes))
        except:
            raise

        return attributes

    @lru_cache(maxsize=None)
    def get_task_class(self, task_name):
        task_class = self.registry.get_class_from_name(task_name)
        return task_class

    @lru_cache(maxsize=None)
    def _get_attribute_wrapper(self, task_name):
        task_attributes = self.registry.get_class_attributes(task_name)
        attribute_tuple = namedtuple('%s_AttributeTuple' % task_name.split('.')[-1], ['name'] + task_attributes.keys())
        return attribute_tuple

    def get_id_and_names_by_scope(self, scope_type):
        return get_id_and_names_by_scope(scope_type)

    def _get_converted_attributes(self, task_name, attribute_wrapper, node_attributes):
        attributes = {}
        for name in attribute_wrapper._fields:
            if name == 'name':
                value = node_attributes.get(name, '')
            elif name in node_attributes:
                value = self._convert_fsd_value(task_name, name, node_attributes[name])
            elif self._is_optional(task_name, name):
                value = None
            else:
                raise TaskAttributeMissingError()
            attributes[name] = value

        return attributes

    def _convert_fsd_value(self, task_name, name, value):
        task_attributes = self.registry.get_class_attributes(task_name)
        attribute = task_attributes[name]
        try:
            return attribute.convert_fsd_to_attribute(value)
        except:
            logger.exception('task %s failed to convert fsd attribute %s with value %s' % (task_name, name, value))
            raise

    def _is_optional(self, task_name, name):
        task_attributes = self.registry.get_class_attributes(task_name)
        attribute = task_attributes[name]
        return attribute.is_optional
