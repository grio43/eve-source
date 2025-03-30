#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterdata\npccharacters.py
from logging import getLogger
import localization
from eve.common.lib.appConst import auraAgentIDs
from eveprefs import boot
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import npcCharactersLoader
except ImportError:
    npcCharactersLoader = None

logger = getLogger(__name__)
OWNER_AURA_IDENTIFIER = 'UI/Agents/AuraAgentName'

class NpcCharactersLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/npcCharacters.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcCharacters.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcCharacters.fsdbinary'
    __loader__ = npcCharactersLoader


def _get_characters():
    return NpcCharactersLoader.GetData()


def iter_npc_characters():
    for character_id, character in _get_characters().iteritems():
        yield (character_id, character)


def get_npc_character(character_id, default = None):
    try:
        return _get_characters()[int(character_id)]
    except (KeyError, ValueError):
        logger.error('Failed to load NPC Character with id: %s, returning %s.', character_id, default)
        return default


def get_npc_character_corporation(character_id, default = None):
    character = get_npc_character(character_id)
    return getattr(character, 'corporationID', default)


def get_npc_character_name(character_id, character = None, language_id = None, important = False):
    if character_id in auraAgentIDs:
        if important:
            return localization.GetImportantByLabel(OWNER_AURA_IDENTIFIER)
        return localization.GetByLabel(OWNER_AURA_IDENTIFIER)
    if not character:
        character = get_npc_character(character_id)
    return _get_message(getattr(character, 'nameID', None), language_id, important)


def _get_message(message_id, language_id = None, important = False):
    if important and boot.role == 'client':
        return localization.GetImportantByMessageID(message_id)
    return localization.GetByMessageID(message_id, language_id)
