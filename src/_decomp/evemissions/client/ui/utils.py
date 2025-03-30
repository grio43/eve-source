#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\ui\utils.py


def get_agent_conversation_window_id(career_path_id, agent_id):
    window_id = 'AgentConversation'
    if career_path_id:
        from characterdata.careerpath import get_career_path_internal_name
        window_id += '_{career_path_name}'.format(career_path_name=get_career_path_internal_name(career_path_id))
    if agent_id:
        window_id += '_{agent_id}'.format(agent_id=agent_id)
    return window_id


def get_mission_details_window_id(career_path_id, agent_id):
    window_id = 'MissionDetails'
    if career_path_id:
        from characterdata.careerpath import get_career_path_internal_name
        window_id += '_{career_path_name}'.format(career_path_name=get_career_path_internal_name(career_path_id))
    if agent_id:
        window_id += '_{agent_id}'.format(agent_id=agent_id)
    return window_id
