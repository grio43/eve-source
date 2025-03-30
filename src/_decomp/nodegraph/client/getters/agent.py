#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\agent.py
from .base import GetterAtom
from characterdata.npccharacters import get_npc_character_name

class GetAgentMission(GetterAtom):
    atom_id = 392

    def __init__(self, agent_id = None, mission_id = None, division_id = None, level = None, faction_id = None, agent_type_id = None, career_path_id = None, accepted = None, offered = None, **kwargs):
        super(GetAgentMission, self).__init__(**kwargs)
        self.mission_id = self.get_atom_parameter_value('mission_id', mission_id)
        self.agent_id = self.get_atom_parameter_value('agent_id', agent_id)
        self.division_id = self.get_atom_parameter_value('division_id', division_id)
        self.faction_id = self.get_atom_parameter_value('faction_id', faction_id)
        self.level = self.get_atom_parameter_value('level', level)
        self.agent_type_id = self.get_atom_parameter_value('agent_type_id', agent_type_id)
        self.career_path_id = self.get_atom_parameter_value('career_path_id', career_path_id)
        self.accepted = self.get_atom_parameter_value('accepted', accepted)
        self.offered = self.get_atom_parameter_value('offered', offered)

    def get_values(self, **kwargs):
        from evemissions.client.mission_finder import find_mission
        mission = find_mission(self.offered, self.accepted, self.mission_id, self.agent_id, self.division_id, self.level, self.faction_id, self.agent_type_id, self.career_path_id)
        if mission:
            return {'mission_id': mission.mission_id,
             'agent_id': mission.agent_id,
             'division_id': mission.division_id,
             'faction_id': mission.faction_id,
             'agent_type_id': mission.agent_type_id,
             'level': mission.level,
             'career_path_id': mission.career_path_id}
        return {}


class GetClosestAgent(GetterAtom):
    atom_id = 477

    def __init__(self, agent_type_id = None, division_id = None, faction_id = None, career_path_id = None, only_incomplete = None, **kwargs):
        super(GetClosestAgent, self).__init__(**kwargs)
        self.agent_type_id = self.get_atom_parameter_value('agent_type_id', agent_type_id)
        self.division_id = self.get_atom_parameter_value('division_id', division_id)
        self.faction_id = self.get_atom_parameter_value('faction_id', faction_id)
        self.career_path_id = self.get_atom_parameter_value('career_path_id', career_path_id)
        self.only_incomplete = self.get_atom_parameter_value('only_incomplete', only_incomplete)

    def get_values(self, **kwargs):
        agent_id = sm.GetService('agents').GetClosestAgent(self.agent_type_id, self.division_id, self.faction_id, self.career_path_id, self.only_incomplete)
        return {'agent_id': agent_id}

    @classmethod
    def get_subtitle(cls, agent_id = None, **kwargs):
        return ''


class GetAgentInfo(GetterAtom):
    atom_id = 515

    def __init__(self, agent_id = None, **kwargs):
        super(GetAgentInfo, self).__init__(**kwargs)
        self.agent_id = self.get_atom_parameter_value('agent_id', agent_id)

    def get_values(self, **kwargs):
        agent_service = sm.GetService('agents')
        agent_info = agent_service.GetAgentByID(self.agent_id)
        if not agent_info:
            return {}
        return {'location_id': agent_service.GetAgentLocation(self.agent_id),
         'station_id': agent_info.stationID,
         'solar_system_id': agent_info.solarsystemID,
         'agent_type_id': agent_info.agentTypeID,
         'division_id': agent_info.divisionID,
         'level': agent_info.level,
         'corporation_id': agent_info.corporationID,
         'faction_id': agent_info.factionID}
