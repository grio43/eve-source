#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveagent\data.py
from collections import defaultdict
from logging import getLogger
from characterdata.npccharacters import get_npc_character
from characterdata.npccharacters import iter_npc_characters
from eve.common.lib.appConst import agentTypeCONCORDAgent
from eve.common.lib.appConst import agentTypeEventMissionAgent
from eve.common.lib.appConst import agentTypeTutorialAgent
from eve.common.lib.appConst import factionCONCORDAssembly
from eve.common.lib.appConst import factionJoveEmpire
from eve.common.lib.appConst import factionSocietyOfConsciousThought
from fsdBuiltData.common.base import BuiltDataLoader
from npcs.npccorporations import get_corporation_faction_id
try:
    import agentsInSpaceLoader
except ImportError:
    agentsInSpaceLoader = None

try:
    import agentTypesLoader
except ImportError:
    agentTypesLoader = None

logger = getLogger(__name__)

class AgentsInSpace(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/agentsInSpace.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/agentsInSpace.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/agentsInSpace.fsdbinary'
    __loader__ = agentsInSpaceLoader


class AgentTypes(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/agentTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/agentTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/agentTypes.fsdbinary'
    __loader__ = agentTypesLoader


def get_agents_in_space():
    return AgentsInSpace.GetData()


def get_agent_in_space(agent_id):
    return get_agents_in_space().get(agent_id, None)


def get_agent(agent_id):
    character = get_npc_character(agent_id)
    if character and character.agent:
        return character.agent
    logger.error('Failed to load agent with id: %d, returning None.', agent_id)


def iter_agents():
    for character_id, character in iter_npc_characters():
        if character.agent:
            yield (character_id, character, character.agent)


def get_agent_type_id(character, agent):
    faction_id = get_corporation_faction_id(character.corporationID)
    if agent.agentType in (agentTypeTutorialAgent, agentTypeCONCORDAgent) or agent.agentLevel == 6 or faction_id in (factionCONCORDAssembly, factionJoveEmpire, factionSocietyOfConsciousThought):
        return agentTypeEventMissionAgent
    return agent.agentType


def get_agent_count_by_corporation(agent_type = None):
    agent_count = defaultdict(int)
    for _, character, agent in iter_agents():
        agent_type_id = get_agent_type_id(character, agent)
        if not agent_type or agent_type == agent_type_id:
            agent_count[character.corporationID] += 1

    return agent_count


def get_agents_by_corporation_id(corporation_id):
    return [ (agent_id, agent, get_agent_type_id(character, agent)) for agent_id, character, agent in iter_agents() if character.corporationID == corporation_id ]


def get_agent_ids_by_agent_type(agent_type):
    return [ character_id for character_id, _, agent in iter_agents() if agent.agentType == agent_type ]


def get_agent_config(agent_id):
    agent = get_agent(agent_id)
    if agent:
        return {'level': agent.agentLevel,
         'agent.LocateCharacterService.enabled': int(agent.agentLocateCharacter)}
    return {}


def iter_agents_in_stations():
    for agent_id, character, agent in iter_agents():
        if character.stationID:
            yield (agent_id, agent, character.stationID)


def get_agent_type_name(agent_type_id, default = None):
    return AgentTypes.GetData().get(agent_type_id, default)
