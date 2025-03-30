#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\player\suggestion.py
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eveui import dragdata
from eveui.constants import State
from eveui.autocomplete.suggestion import Suggestion
import localization

class OwnerIdentitySuggestion(Suggestion):
    __slots__ = ('owner_id',)
    key_attributes = __slots__

    def __init__(self, owner_id):
        self.owner_id = owner_id

    @property
    def name(self):
        return cfg.eveowners.Get(self.owner_id).ownerName

    @property
    def is_corporation(self):
        return idCheckers.IsCorporation(self.owner_id)

    @property
    def is_alliance(self):
        return idCheckers.IsAlliance(self.owner_id)

    @property
    def is_faction(self):
        return idCheckers.IsFaction(self.owner_id)

    @property
    def is_character(self):
        return idCheckers.IsCharacter(self.owner_id)

    @property
    def is_player_character(self):
        return idCheckers.IsEvePlayerCharacter(self.owner_id)

    @property
    def is_npc_character(self):
        return idCheckers.IsNPCCharacter(self.owner_id)

    @property
    def type_id(self):
        if self.is_character:
            return appConst.typeCharacter
        if self.is_corporation:
            return appConst.typeCorporation
        if self.is_alliance:
            return appConst.typeAlliance
        if self.is_faction:
            return appConst.typeFaction
        return appConst.typeCharacter

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        if self.is_player_character:
            return localization.GetByLabel('UI/Common/Capsuleer')
        if self.is_character:
            return localization.GetByLabel('UI/Common/Character')
        if self.is_corporation:
            return localization.GetByLabel('UI/Common/Corporation')
        if self.is_alliance:
            return localization.GetByLabel('UI/Common/Alliance')
        if self.is_faction:
            return localization.GetByLabel('UI/Common/Faction')
        return ''

    def render_icon(self, size):
        return OwnerIcon(state=State.disabled, ownerID=self.owner_id, size=size, width=size, height=size)

    def get_drag_data(self):
        return dragdata.Character(self.owner_id)

    def get_menu(self):
        return sm.GetService('menu').GetMenuForOwner(self.owner_id)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.type_id, itemID=self.owner_id)
