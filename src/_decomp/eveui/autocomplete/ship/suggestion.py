#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\ship\suggestion.py
import evetypes
from eveui.autocomplete import Suggestion
from shipgroup import get_ship_class_id, get_ship_group_name, get_ship_tree_group_name, get_ship_tree_group_icon, get_ship_tree_group_icon_small
from eveui import dragdata
from eveui.constants import State
from eveui.primitive.sprite import Sprite
from eve.client.script.ui.control.itemIcon import ItemIcon
from carbonui import TextColor
import localization

class ShipTypeSuggestion(Suggestion):
    __slots__ = ('type_id',)
    key_attributes = __slots__

    def __init__(self, type_id):
        self.type_id = type_id

    @property
    def name(self):
        return evetypes.GetName(self.type_id, important=False)

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        return get_ship_group_name(self.type_id)

    def render_icon(self, size):
        return ItemIcon(state=State.disabled, width=size, height=size, typeID=self.type_id, showOmegaOverlay=False)

    def get_drag_data(self):
        return dragdata.ItemType(type_id=self.type_id)

    def get_menu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.type_id, includeMarketDetails=True)

    def has_show_info(self):
        return True

    def show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.type_id)


class ShipClassSuggestion(Suggestion):
    __slots__ = ('ship_class_id',)
    key_attributes = __slots__

    def __init__(self, ship_class_id):
        self.ship_class_id = ship_class_id

    @property
    def name(self):
        return get_ship_tree_group_name(self.ship_class_id)

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        return localization.GetByLabel('UI/Common/ShipClass')

    def render_icon(self, size):
        if size > 32:
            size = max(32, size * 0.8)
            texture_path = get_ship_tree_group_icon(self.ship_class_id)
        else:
            texture_path = get_ship_tree_group_icon_small(self.ship_class_id)
        return Sprite(width=size, height=size, texturePath=texture_path, color=TextColor.SECONDARY)
