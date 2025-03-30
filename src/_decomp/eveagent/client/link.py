#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveagent\client\link.py
from evelink import Link
import localization
from evemissions.client.data import get_mission_name_id
SCHEME_OPEN_CAREER_AGENTS = 'openCareerAgents'
SCHEME_FLEET_MISSION = 'fleetmission'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_FLEET_MISSION, handler=handle_fleet_mission_link, hint='UI/Opportunities/ChatLinkHint')


def handle_fleet_mission_link(url):
    agent_id, char_id = parse_fleet_mission_url(url)
    sm.GetService('agents').PopupMission(agent_id, char_id)


def parse_fleet_mission_url(url):
    agent_id, char_id = url.split(':')[1].split('//')
    return (int(agent_id), int(char_id))


def format_fleet_mission_url(agent_id, char_id):
    return u'{}:{}//{}'.format(SCHEME_FLEET_MISSION, agent_id, char_id)


def open_career_agents_link(text):
    return Link(url=format_open_career_agents_url(), text=text)


def format_open_career_agents_url():
    return u'{}:'.format(SCHEME_OPEN_CAREER_AGENTS)


class AgentMissionLinkDragData(object):

    def __init__(self, agent_id, character_id, content_id):
        self._agent_id = agent_id
        self._character_id = character_id
        self._content_id = content_id

    def get_link(self):
        mission_name = localization.GetByMessageID(get_mission_name_id(self._content_id))
        agent_name = cfg.eveowners.Get(self._agent_id).name
        return Link(url=format_fleet_mission_url(self._agent_id, self._character_id), text=localization.GetByLabel('UI/Opportunities/ChatLinkLabel', title=u'{} - {}'.format(agent_name, mission_name)))

    def LoadIcon(self, icon, dad, iconSize):
        icon.LoadIcon('res:/ui/Texture/WindowIcons/opportunities.png')
