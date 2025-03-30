#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\npc\provider.py
import threadutils
from eve.common.lib import appConst
from npcs.npccorporations import get_npc_corporations, get_npc_corporation_name
from characterdata.factions import get_factions, get_faction_name
from characterdata.npccharacters import iter_npc_characters, get_npc_character_name
from eveui.autocomplete.provider import NameCache, NameCacheProvider
from eveui.autocomplete.npc.suggestion import FactionSuggestion, NpcCorporationSuggestion, AgentSuggestion

class FactionProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(FactionProvider, self).__init__(cache=FactionNameCache.instance(), suggestion_type=FactionSuggestion, filter=filter)


class FactionNameCache(NameCache):

    def prime(self):
        cache = {}
        for faction_id in get_factions():
            cache[faction_id] = get_faction_name(faction_id, important=False)
            threadutils.BeNice(5)

        return cache


class NpcCorporationProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(NpcCorporationProvider, self).__init__(cache=NpcCorporationNameCache.instance(), suggestion_type=NpcCorporationSuggestion, filter=filter)


class NpcCorporationNameCache(NameCache):

    def prime(self):
        cache = {}
        for corporation_id in get_npc_corporations():
            cache[corporation_id] = get_npc_corporation_name(corporation_id, important=False)
            threadutils.BeNice(5)

        return cache


class AgentProvider(NameCacheProvider):

    def __init__(self, filter = None):
        super(AgentProvider, self).__init__(cache=AgentNameCache.instance(), suggestion_type=AgentSuggestion, filter=filter)


class AgentNameCache(NameCache):

    def prime(self):
        cache = {}
        for character_id, character in iter_npc_characters():
            if character.agent and character.agent.agentType != appConst.agentTypeAura:
                cache[character_id] = get_npc_character_name(character_id, character=character, important=False)
            threadutils.BeNice(5)

        return cache
