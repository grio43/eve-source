#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\agent.py
from .base import Condition

class HasAgentMission(Condition):
    atom_id = 156

    def __init__(self, agent_id = None, mission_id = None, division_id = None, level = None, faction_id = None, agent_type_id = None, career_path_id = None, accepted = None, offered = None, **kwargs):
        super(HasAgentMission, self).__init__(**kwargs)
        self.agent_id = self.get_atom_parameter_value('agent_id', agent_id)
        self.mission_id = self.get_atom_parameter_value('mission_id', mission_id)
        self.division_id = self.get_atom_parameter_value('division_id', division_id)
        self.faction_id = self.get_atom_parameter_value('faction_id', faction_id)
        self.level = self.get_atom_parameter_value('level', level)
        self.agent_type_id = self.get_atom_parameter_value('agent_type_id', agent_type_id)
        self.career_path_id = self.get_atom_parameter_value('career_path_id', career_path_id)
        self.accepted = self.get_atom_parameter_value('accepted', accepted)
        self.offered = self.get_atom_parameter_value('offered', offered)

    def validate(self, **kwargs):
        from evemissions.client.mission_finder import find_mission
        return bool(find_mission(self.offered, self.accepted, self.mission_id, self.agent_id, self.division_id, self.level, self.faction_id, self.agent_type_id, self.career_path_id))

    @classmethod
    def get_subtitle(cls, agent_id = None, mission_id = None, accepted = None, offered = None, **kwargs):
        result = []
        if cls.get_atom_parameter_value('accepted', accepted):
            result.append('Accepted')
        if cls.get_atom_parameter_value('offered', offered):
            result.append('Offered')
        if agent_id:
            result.append('Agent:{}'.format(agent_id))
        if mission_id:
            from evemissions.client.data import get_mission_name_id
            from localization import GetByMessageID
            mission_name_id = get_mission_name_id(mission_id)
            mission_name = GetByMessageID(mission_name_id)
            result.append('"{}"'.format(mission_name))
        return ' '.join(result)


class IsAgentMissionWindowOpen(HasAgentMission):
    atom_id = 423

    def __init__(self, require_details_window = None, **kwargs):
        super(IsAgentMissionWindowOpen, self).__init__(**kwargs)
        self.require_details_window = self.get_atom_parameter_value('require_details_window', require_details_window)

    def validate(self, **kwargs):
        from evemissions.client.mission_finder import find_missions
        from evemissions.client.ui.utils import get_agent_conversation_window_id, get_mission_details_window_id
        from jobboard.client import get_agent_mission_job
        missions = find_missions(self.offered, self.accepted, self.mission_id, self.agent_id, self.division_id, self.level, self.faction_id, self.agent_type_id, self.career_path_id)
        if not missions:
            return False
        for mission in missions:
            agent_conversation_window_id = get_agent_conversation_window_id(mission.career_path_id, mission.agent_id)
            mission_details_window_id = get_mission_details_window_id(mission.career_path_id, mission.agent_id)
            if not self.require_details_window and get_window(agent_conversation_window_id):
                return True
            if get_window(mission_details_window_id):
                return True
            job = get_agent_mission_job(mission.agent_id, wait=False)
            if job and job.is_open:
                return True

        return False


def get_window(window_id):
    from carbonui.control.window import Window
    return Window.GetIfOpen(window_id) or Window.GetIfOpen((window_id, None))
