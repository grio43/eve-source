#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective\agent.py
from objectives.client.objective.base import Objective

class CompleteAgentMissionObjective(Objective):
    objective_content_id = 2

    def _on_start(self):
        agent_id = self.get_value('agent_id')
        if not self.get_value('location_id'):
            location_id = sm.GetService('agents').GetAgentLocation(agent_id)
            self.update_value('location_id', location_id)
        mission = sm.GetService('missionObjectivesTracker').agentMissions.get(agent_id)
        if mission and mission.remote_completable:
            self.start_task('talk_to_agent')
        else:
            self.start_task('travel_to_agent')
