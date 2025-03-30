#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\ui\agents.py
from projectdiscovery.common.const import ACTIVE_PROJECT_ID, COVID_PROJECT_ID, EXOPLANETS_PROJECT_ID

class Agent(object):
    __slots__ = ('name', 'image')

    def __init__(self, name, image):
        self.name = name
        self.image = image


AGENTS_BY_PROJECT = {EXOPLANETS_PROJECT_ID: Agent(name='UI/ProjectDiscovery/exoplanets/AgentName', image='res:/UI/Texture/classes/ProjectDiscovery/DrMayor.png'),
 COVID_PROJECT_ID: Agent(name='UI/ProjectDiscovery/exoplanets/AgentName', image='res:/UI/Texture/classes/ProjectDiscovery/DrMayor.png')}

def get_agent():
    return AGENTS_BY_PROJECT.get(ACTIVE_PROJECT_ID, AGENTS_BY_PROJECT[EXOPLANETS_PROJECT_ID])
