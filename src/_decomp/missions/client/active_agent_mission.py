#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\missions\client\active_agent_mission.py
import caching
import signals
import uuid
import threadutils
from localization import GetByMessageID
from evemissions.client.data import get_mission
from missions.client.featureFlag import are_mission_objectives_enabled
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext

class ActiveAgentMission(object):

    def __init__(self, mission_info):
        self.mission_state = mission_info[0]
        self.is_story_line_mission = mission_info[1]
        self.mission_type_label = mission_info[2]
        self.agent_id = mission_info[4]
        self.expiration_time = mission_info[5]
        self.bookmarks = mission_info[6]
        self.remote_offerable = mission_info[7]
        self.remote_completable = mission_info[8]
        self.content_id = mission_info[9]
        self.focused = False
        self.current_objective = None
        self.on_objective_changed = signals.Signal('objective_changed')
        self.context = ObjectivesContext()
        self.node_graph = None
        self.objective_chain = None
        self.start()

    @property
    def fsd_data(self):
        return get_mission(self.content_id)

    @property
    def mission_name(self):
        return GetByMessageID(self.fsd_data.nameID)

    @caching.lazy_property
    def node_graph_id(self):
        return self.fsd_data.nodeGraphID

    @property
    def are_objectives_complete(self):
        if not self.current_objective:
            return False
        return self.current_objective[0] == 'AllObjectivesComplete'

    def update_objective(self, objective_info):
        if objective_info == self.current_objective:
            return
        self.current_objective = objective_info
        self.on_objective_changed()
        if not self.context:
            return
        if objective_info:
            objective_key = objective_info[0]
            objective_value = objective_info[1:] if len(objective_info) > 1 else None
            self.context.update_value('objective_key', objective_key, force_update=True)
            self.context.update_value('objective_value', objective_value, force_update=True)
        else:
            self.context.update_value('objective_key', '')
            self.context.update_value('objective_value', None)

    @threadutils.threaded
    def start(self):
        sm.RegisterForNotifyEvent(self, 'OnExpandedMissionChanged')
        self.OnExpandedMissionChanged(**sm.GetService('infoPanel').GetExpandedMission())
        if not self.node_graph_id and not self.fsd_data.clientObjectives:
            return
        agent_info = sm.GetService('agents').GetAgentByID(self.agent_id)
        blackboard_values = {'agent_id': self.agent_id,
         'agent_mission_id': self.content_id,
         'agent_location_id': agent_info.stationID or agent_info.solarsystemID,
         'agent_solar_system_id': agent_info.solarsystemID,
         'mission_instance_id': str(uuid.uuid4()),
         'mission_content_id': self.content_id,
         'objective_key': ''}
        fsd_data = self.fsd_data
        if fsd_data.initialAgentGiftTypeID:
            blackboard_values['initial_gift'] = {'type_id': fsd_data.initialAgentGiftTypeID,
             'quantity': fsd_data.initialAgentGiftQuantity or 1}
        kill_mission = fsd_data.killMission
        if kill_mission:
            blackboard_values['dungeon_id'] = kill_mission.dungeonID
            if kill_mission.objectiveTypeID:
                blackboard_values['deliver_items'] = {'type_id': kill_mission.objectiveTypeID,
                 'quantity': kill_mission.objectiveQuantity or 1}
            if kill_mission.dropItemInMissionContainer:
                blackboard_values['loot_container'] = {'type_id': kill_mission.dropItemInMissionContainer}
        courier_mission = fsd_data.courierMission
        if courier_mission:
            blackboard_values['deliver_items'] = {'type_id': courier_mission.objectiveTypeID,
             'quantity': courier_mission.objectiveQuantity or 1}
        for bookmark in self.bookmarks:
            if bookmark['locationType'] == 'objective.destination' and 'complete_mission_location_id' not in blackboard_values:
                blackboard_values['complete_mission_location_id'] = bookmark.itemID
            if bookmark['locationType'] == 'dungeon' and 'dungeon_bookmark' not in blackboard_values:
                blackboard_values['dungeon_bookmark'] = bookmark
                blackboard_values['dungeon_location_id'] = bookmark.locationID

        if 'complete_mission_location_id' not in blackboard_values:
            blackboard_values['complete_mission_location_id'] = blackboard_values['agent_location_id']
        self.context.set_default_values(**blackboard_values)
        self._start_node_graph()
        self._start_objectives()

    def stop(self):
        sm.UnregisterForNotifyEvent(self, 'OnExpandedMissionChanged')
        if self.node_graph:
            sm.GetService('node_graph').stop_node_graph(self.node_graph.instance_id)
            self.node_graph = None
        if self.objective_chain:
            self.objective_chain.stop()
            self.objective_chain = None
        if self.context:
            self.context.clear()
            self.context = None

    def _start_node_graph(self):
        if self.node_graph_id:
            from nodegraph.common.nodedata import is_client_graph
            if is_client_graph(self.node_graph_id):
                self.node_graph = sm.GetService('node_graph').start_node_graph(node_graph_id=self.node_graph_id, context=self.context)

    def _start_objectives(self):
        if not are_mission_objectives_enabled():
            return
        client_objectives = self.fsd_data.clientObjectives
        if client_objectives:
            from objectives.common.util import fix_fsd_value
            for context_parameter in client_objectives.contextParameters or []:
                self.context.update_value(context_parameter.key, fix_fsd_value(context_parameter.value))

            self.objective_chain = ObjectiveChain(content_id=client_objectives.objectiveChainID, context=self.context, overrides=client_objectives.overrides)
            self.objective_chain.start()

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        self.focused = featureID == 'agent_mission' and missionID == self.agent_id or featureID == 'opportunities' and missionID == 'agent_missions:{}'.format(self.agent_id)
        if self.context:
            self.context.update_value('mission_focused', self.focused)
