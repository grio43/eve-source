#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\objectives.py
from .base import Action
from storylines.client.objectives.loader import ObjectivesData

class BaseInfoPanelAction(Action):
    atom_id = None

    def __init__(self, info_panel = None, **kwargs):
        super(BaseInfoPanelAction, self).__init__(**kwargs)
        self.info_panel = info_panel

    def _clear_objectives(self):
        if self.info_panel:
            from storylines.client.objectives.controller import clear_objectives_in_tracker
            clear_objectives_in_tracker(self.info_panel)


class ShowInfoPanelObjective(BaseInfoPanelAction):
    atom_id = 454

    def __init__(self, goal_id = None, objective_id = None, completed = None, warp_client_action = None, node_graph_id = None, objective_values = None, **kwargs):
        super(ShowInfoPanelObjective, self).__init__(**kwargs)
        self.goal_id = goal_id
        self.objective_id = objective_id
        self.completed = self.get_atom_parameter_value('completed', completed)
        self.warp_client_action = warp_client_action
        self.node_graph_id = node_graph_id
        self.objective_values = objective_values

    def start(self, **kwargs):
        super(ShowInfoPanelObjective, self).start()
        self._set_objective()

    def _set_objective(self):
        if self.goal_id and self.objective_id and self.info_panel:
            from storylines.client.objectives.controller import set_objective_in_tracker
            warp_function = self._request_warp if self.warp_client_action else None
            set_objective_in_tracker(self.info_panel, self.goal_id, self.objective_id, self.completed, warp_function, self.objective_values)

    def _request_warp(self):
        node_graph = sm.GetService('node_graph').get_active_node_graph_by_id(self.node_graph_id)
        if not node_graph:
            raise ValueError('Cannot send action to server graph from inactive client graph %s' % self.node_graph_id)
        node_graph.send_message_to_server_graph('client_action', self.warp_client_action)

    def stop(self):
        super(ShowInfoPanelObjective, self).stop()
        self._clear_objectives()

    @classmethod
    def get_subtitle(cls, goal_id = None, objective_id = None, info_panel = None, completed = None, **kwargs):
        objective_name = ObjectivesData.get_name(objective_id) if objective_id else ''
        return u'{}'.format(objective_name)


class ClearInfoPanelObjectives(BaseInfoPanelAction):
    atom_id = 455

    def start(self, **kwargs):
        super(ClearInfoPanelObjectives, self).start(**kwargs)
        self._clear_objectives()
