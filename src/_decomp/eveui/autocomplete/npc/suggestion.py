#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\npc\suggestion.py
from eve.common.lib import appConst
from npcs.npccorporations import get_npc_corporation_name, get_corporation_faction_id
from characterdata.factions import get_faction_name
from characterdata.npccharacters import get_npc_character_name, get_npc_character
import localization
from eveui import dragdata
from eveui.constants import State
from eveui.icon.agent_portrait import AgentPortrait
from eve.client.script.ui.control.eveIcon import OwnerIcon
import eveformat.client
from eveui.autocomplete.suggestion import Suggestion

class FactionSuggestion(Suggestion):
    __slots__ = ('faction_id',)
    key_attributes = __slots__

    def __init__(self, faction_id):
        self.faction_id = faction_id

    @property
    def type_id(self):
        return appConst.typeFaction

    @property
    def text(self):
        return get_faction_name(self.faction_id, important=False)

    @property
    def subtext(self):
        return localization.GetByLabel('UI/Common/Faction')

    def render_icon(self, size):
        return OwnerIcon(state=State.disabled, ownerID=self.faction_id, size=size, width=size, height=size)

    def get_drag_data(self):
        return dragdata.Character(self.faction_id)

    def get_menu(self):
        return sm.GetService('menu').GetMenuForOwner(self.faction_id)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.type_id, itemID=self.faction_id)


class NpcCorporationSuggestion(Suggestion):
    __slots__ = ('corporation_id',)
    key_attributes = __slots__

    def __init__(self, corporation_id):
        self.corporation_id = corporation_id

    @property
    def type_id(self):
        return appConst.typeCorporation

    @property
    def text(self):
        return get_npc_corporation_name(self.corporation_id, important=False)

    @property
    def subtext(self):
        faction_id = get_corporation_faction_id(self.corporation_id)
        if faction_id:
            return get_faction_name(faction_id, important=False)
        return ''

    def render_icon(self, size):
        return OwnerIcon(state=State.disabled, ownerID=self.corporation_id, size=size, width=size, height=size)

    def get_drag_data(self):
        return dragdata.Character(self.corporation_id)

    def get_menu(self):
        return sm.GetService('menu').GetMenuForOwner(self.corporation_id)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.type_id, itemID=self.corporation_id)


class AgentSuggestion(Suggestion):
    __slots__ = ('agent_id',)
    key_attributes = __slots__

    def __init__(self, agent_id):
        self.agent_id = agent_id

    @property
    def type_id(self):
        character_info = cfg.eveowners.Get(self.agent_id)
        return character_info.typeID

    @property
    def text(self):
        return get_npc_character_name(self.agent_id, important=False)

    @property
    def subtext(self):
        character_info = get_npc_character(self.agent_id)
        station = cfg.stations.Get(character_info.stationID)
        return eveformat.solar_system_with_security_and_jumps(station.solarSystemID)

    def render_icon(self, size):
        return AgentPortrait(state=State.disabled, agent_id=self.agent_id, size=size)

    def get_drag_data(self):
        return dragdata.Character(self.agent_id)

    def get_menu(self):
        return sm.GetService('menu').GetMenuForOwner(self.agent_id)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.type_id, itemID=self.agent_id)
