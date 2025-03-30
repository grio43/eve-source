#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_chain.py
from collections import OrderedDict, defaultdict
import logging
import localization
from objectives.client.objective import get_objective_class
from objectives.common.objectives_data import get_objective_chain_data
from objectives.common.util import fix_fsd_value
logger = logging.getLogger('objectives')

class ObjectiveChain(object):

    def __init__(self, content_id, context, overrides = None):
        self.content_id = content_id
        self.context = context
        self.objectives_info = OrderedDict()
        self.overrides = overrides or {}
        data = self.content_data
        for info in data.objectives:
            self.objectives_info[info.key] = info

        self.objectives = OrderedDict()
        self._subscribed_values = defaultdict(dict)
        self._context_flow_triggers = defaultdict(set)
        self.context.set_default_values(**_get_objective_chain_default_values(data))
        self.context.subscribe_to_message('start_objective', self._trigger_handler)
        self.context.subscribe_to_message('stop_objective', self._trigger_handler)
        self.context.subscribe_to_message('show_objective', self._trigger_handler)
        self.context.subscribe_to_message('hide_objective', self._trigger_handler)
        self.context.subscribe_to_message('start_group', self._trigger_handler)
        self.context.subscribe_to_message('stop_group', self._trigger_handler)
        self.context.subscribe_to_message('show_group', self._trigger_handler)
        self.context.subscribe_to_message('hide_group', self._trigger_handler)
        self.context.subscribe_to_message('show_objective_highlights', self._trigger_handler)
        self.context.subscribe_to_message('hide_objective_highlights', self._trigger_handler)
        self.context.subscribe_to_value('all', self._context_value_changed)
        self.node_graph = None

    @property
    def content_data(self):
        return get_objective_chain_data(self.content_id)

    def start(self):
        node_graph_id = self.content_data.nodeGraph
        if node_graph_id:
            self.node_graph = sm.GetService('node_graph').start_node_graph(node_graph_id, node_graph_parent_id=self.context.get_value('root_node_graph_id'), context=self.context)
        for objective_info in self.objectives_info.itervalues():
            if objective_info.startActive:
                self.start_objective(objective_info.key)
            if objective_info.contextParameterTrigger:
                self._add_context_flow_trigger(objective_info)

    def stop(self):
        if self.node_graph:
            sm.GetService('node_graph').stop_node_graph(self.node_graph.instance_id)
            self.node_graph = None
        for objective in self.objectives.itervalues():
            objective.clear()

        self.context.clear()

    def start_objective(self, objective_id):
        if objective_id not in self.objectives:
            self._construct_objective(objective_id)
        objective = self.objectives.get(objective_id)
        if not objective or objective.is_active:
            return
        self.context.send_message('on_objectives_changed')
        objective.start()

    def stop_objective(self, objective_id):
        objective = self.objectives.get(objective_id)
        if not objective:
            return
        objective.stop()
        objective.on_state_changed.disconnect(self._on_objective_state_changed)
        objective.on_tasks_changed.disconnect(self._on_objective_tasks_changed)
        self._unsubscribe_from_values(objective_id)
        del self.objectives[objective_id]
        self._update_objectives_in_context(objective_id)
        self.context.send_message('on_objectives_changed')

    def show_objective(self, objective_id):
        objective = self.objectives.get(objective_id)
        if not objective:
            return
        objective.hidden = False

    def hide_objective(self, objective_id):
        objective = self.objectives.get(objective_id)
        if not objective:
            return
        objective.hidden = True

    def start_group(self, group_id):
        for objective_info in self.objectives_info.itervalues():
            if group_id in (objective_info.groups or []):
                self.start_objective(objective_info.key)

    def stop_group(self, group_id):
        for objective_info in self.objectives_info.itervalues():
            if group_id in (objective_info.groups or []):
                self.stop_objective(objective_info.key)

    def show_group(self, group_id):
        for objective_id, objective in self.objectives.iteritems():
            if group_id in (self.objectives_info[objective_id].groups or []):
                objective.hidden = False

    def hide_group(self, group_id):
        for objective_id, objective in self.objectives.iteritems():
            if group_id in (self.objectives_info[objective_id].groups or []):
                objective.hidden = True

    def show_objective_highlights(self, objective_id):
        objective = self.objectives.get(objective_id)
        if not objective:
            return
        objective.show_highlights()

    def hide_objective_highlights(self, objective_id):
        objective = self.objectives.get(objective_id)
        if not objective:
            return
        objective.hide_highlights()

    def objective_trigger(self, objective_id, trigger_key):
        triggers = self.objectives_info[objective_id].triggers
        if not triggers or trigger_key not in triggers:
            return
        for trigger in triggers[trigger_key]:
            self._trigger_handler(trigger.action, trigger.objectiveKey)

    def _trigger_handler(self, key, value):
        if key == 'start_objective':
            self.start_objective(value)
        elif key == 'stop_objective':
            self.stop_objective(value)
        elif key == 'show_objective':
            self.show_objective(value)
        elif key == 'hide_objective':
            self.hide_objective(value)
        elif key == 'start_group':
            self.start_group(value)
        elif key == 'stop_group':
            self.stop_group(value)
        elif key == 'show_group':
            self.show_group(value)
        elif key == 'hide_group':
            self.hide_group(value)
        elif key == 'show_objective_highlights':
            self.show_objective_highlights(value)
        elif key == 'hide_objective_highlights':
            self.hide_objective_highlights(value)
        else:
            logger.error('Objective trigger action %s is not supported', key)

    def _on_objective_state_changed(self, objective, objective_id, reason):
        self.objective_trigger(objective_id, reason)
        self._update_objectives_in_context(objective_id)
        self.context.send_message('on_objective_state_changed', objective=objective, objective_id=objective_id, reason=reason)

    def _on_objective_tasks_changed(self, objective, objective_id, task_id, reason):
        self.context.send_message('on_objective_tasks_changed', objective=objective, objective_id=objective_id, task_id=task_id, reason=reason)

    def _construct_objective(self, objective_id):
        objective_info = self.objectives_info.get(objective_id)
        if not objective_info:
            return
        objective_class = get_objective_class(objective_info.objectiveType)
        objective_values = {}
        for key, context_key in objective_info.inputParametersMap.iteritems():
            objective_values[key] = self.context.get_value(context_key)
            self._subscribe_to_value(objective_id, key, context_key)

        overrides = self.overrides.get(objective_id)
        title = getattr(overrides, 'title', objective_info.title)
        if title:
            title = localization.GetByLabel(title)
        description = getattr(overrides, 'description', objective_info.description)
        if description:
            description = localization.GetByLabel(description)
        tooltip = objective_info.tooltip
        if tooltip:
            tooltip = localization.GetByLabel(tooltip)
        task_overrides = {}
        for task_id, task_override in (objective_info.taskOverrides or {}).iteritems():
            task_overrides[task_id] = task_override

        for task_id, task_override in (getattr(overrides, 'taskOverrides', None) or {}).iteritems():
            task_overrides[task_id] = task_override

        objective = objective_class(objective_id=objective_id, objective_content_id=objective_info.objectiveType, objective_values=objective_values, title=title, description=description, tooltip=tooltip, task_overrides=task_overrides, show_completed=bool(objective_info.showCompleted), rendering_order=objective_info.renderingOrder or 5)
        objective.on_state_changed.connect(self._on_objective_state_changed)
        objective.on_tasks_changed.connect(self._on_objective_tasks_changed)
        self.objectives[objective_id] = objective
        self._update_objectives_in_context(objective_id)

    def _subscribe_to_value(self, objective_id, objective_value_key, context_key):
        self._subscribed_values[context_key][objective_id] = objective_value_key

    def _unsubscribe_from_values(self, objective_id):
        objective_info = self.objectives_info.get(objective_id)
        for key, context_key in objective_info.inputParametersMap.iteritems():
            self._subscribed_values[context_key].pop(objective_id, None)

    def _context_value_changed(self, key, value, old_value):
        if key in self._context_flow_triggers:
            for objective_id in self._context_flow_triggers[key]:
                self._check_context_flow_trigger(objective_id)

        if key in self._subscribed_values:
            for objective_id, value_key in self._subscribed_values[key].iteritems():
                if objective_id in self.objectives:
                    self.objectives[objective_id].update_value(value_key, value)

    def _update_objectives_in_context(self, objective_id):
        objective = self.objectives.get(objective_id, None)
        objectives = self.context.get_value('objectives', {})
        if objective:
            objectives[objective_id] = objective.get_status_values()
        else:
            objectives.pop(objective_id, None)
        self.context.update_value('objectives', objectives, force_update=True)

    def _add_context_flow_trigger(self, objective_info):
        objective_id = objective_info.key
        context_key = objective_info.contextParameterTrigger.key
        self._context_flow_triggers[context_key].add(objective_id)
        self._check_context_flow_trigger(objective_id)

    def _check_context_flow_trigger(self, objective_id):
        info = self.objectives_info[objective_id].contextParameterTrigger
        value_a = self.context.get_value(info.key, object_path=info.objectPath)
        value_b = info.value
        if info.flipped:
            value_a, value_b = value_b, value_a
        operator_func = get_operator_function(info.operator)
        if operator_func(value_a, value_b):
            self.start_objective(objective_id)
        else:
            self.stop_objective(objective_id)

    def get_context_menu(self, include_blackboard = False):
        from objectives.client.qa_tools import get_objective_chain_context_menu
        return get_objective_chain_context_menu(self, include_blackboard)


def _get_objective_chain_default_values(data):
    result = {}
    for context_parameter in data.contextParameters:
        if context_parameter.defaultValue is not None:
            result[context_parameter.parameterKey] = fix_fsd_value(context_parameter.defaultValue)

    return result


operator_functions = {'equalTo': lambda a, b: a == b,
 'notEqualTo': lambda a, b: a != b,
 'greaterThan': lambda a, b: a > b,
 'lessThan': lambda a, b: a < b,
 'greaterThanOrEqual': lambda a, b: a >= b,
 'lessThanOrEqual': lambda a, b: a <= b,
 'in': lambda a, b: a in (b or []),
 'notIn': lambda a, b: a not in (b or [])}

def get_operator_function(operator):
    return operator_functions[operator or 'equalTo']
