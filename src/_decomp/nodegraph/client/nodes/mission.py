#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\mission.py
from nodegraph.common.nodes.base import Node

class MissionObjectiveNode(Node):
    node_type_id = 52

    def __init__(self, **kwargs):
        super(MissionObjectiveNode, self).__init__(**kwargs)
        self.objective_id = self.get_node_parameter_value(self.node_parameters, 'objective_id')
        self._objective_chain = None
        self._objective = None
        self.graph.start_active_node_ids.insert(0, self.node_id)

    def __del__(self):
        if self._objective_chain:
            self._objective_chain.context.unsubscribe_from_message('on_objectives_changed', self._on_objectives_changed)
            self._objective_chain.context.unsubscribe_from_message('on_objective_state_changed', self._on_objective_state_changed)
        self._objective_chain = None
        self._objective = None

    def start(self, **kwargs):
        if not self._objective_chain:
            self._initialize()
            return
        super(MissionObjectiveNode, self).start(**kwargs)
        self._objective_chain.start_objective(self.objective_id)

    def stop(self, **kwargs):
        if not self._objective_chain:
            return
        super(MissionObjectiveNode, self).stop(**kwargs)
        self._objective_chain.stop_objective(self.objective_id)

    def _initialize(self):
        mission = sm.GetService('missionObjectivesTracker').agentMissions.get(self.graph.context.get_value('agent_id'))
        if not mission:
            return
        self._objective_chain = mission.objective_chain
        self._objective_chain.context.subscribe_to_message('on_objectives_changed', self._on_objectives_changed)
        self._objective_chain.context.subscribe_to_message('on_objective_state_changed', self._on_objective_state_changed)
        self._on_objectives_changed()
        if self._objective:
            if self._objective.completed:
                self._start_connection('on_complete')
            elif self._objective.is_active:
                self._start_connection('on_start')

    def _on_objectives_changed(self, **kwargs):
        objective = self._objective_chain.objectives.get(self.objective_id)
        if objective == self._objective:
            return
        self._objective = objective
        if self._objective:
            self.mark_active()
        else:
            self.mark_inactive()

    def _on_objective_state_changed(self, objective, reason, **kwargs):
        if objective != self._objective:
            return
        self._start_connection(reason)

    @classmethod
    def get_subtitle(cls, node_data):
        return cls.get_node_parameter_value(node_data.nodeParameters, 'objective_id', 'MISSING objective_id')
