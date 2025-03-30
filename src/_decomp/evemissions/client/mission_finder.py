#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\mission_finder.py
from evemissions.client.mission import Mission

def find_mission(*args, **kwargs):
    kwargs['return_all'] = False
    missions = _find_missions(*args, **kwargs)
    if missions:
        return missions[0]


def find_missions(*args, **kwargs):
    kwargs['return_all'] = True
    missions = _find_missions(*args, **kwargs)
    return missions


def _find_missions(offered = True, accepted = True, mission_id = None, agent_id = None, division_id = None, level = None, faction_id = None, agent_type_id = None, career_path_id = None, return_all = False):
    ret = []
    for each_mission in sm.GetService('journal').GetAgentMissions():
        each_mission_state, _, _, _, each_agent_id, _, _, _, _, each_mission_id = each_mission
        each_mission = Mission(each_mission_id, each_agent_id, each_mission_state)
        if mission_id and mission_id != each_mission.mission_id:
            continue
        if agent_id and agent_id != each_mission.agent_id:
            continue
        if division_id or level or faction_id or agent_type_id:
            if division_id and division_id != each_mission.division_id:
                continue
            if level and level != each_mission.level:
                continue
            if faction_id and faction_id != each_mission.faction_id:
                continue
            if agent_type_id and agent_type_id != each_mission.agent_type_id:
                continue
            if career_path_id and career_path_id != each_mission.career_path_id:
                continue
        if accepted and each_mission.is_accepted() or offered and each_mission.is_offered():
            ret.append(each_mission)
            if not return_all:
                return ret

    return ret
