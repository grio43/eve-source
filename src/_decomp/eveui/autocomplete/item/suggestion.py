#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\item\suggestion.py
import evetypes
import eveicon
from carbonui import TextColor
from eveui.autocomplete.suggestion import Suggestion
from eveui import dragdata
from eveui.constants import State
from eveui.primitive.sprite import Sprite
from eve.client.script.ui.control.itemIcon import ItemIcon
import localization

class ItemTypeSuggestion(Suggestion):
    __slots__ = ('type_id',)
    key_attributes = __slots__

    def __init__(self, type_id):
        self.type_id = type_id

    @property
    def name(self):
        return evetypes.GetName(self.type_id, important=False)

    @property
    def group_id(self):
        return evetypes.GetGroupID(self.type_id)

    @property
    def group_name(self):
        return evetypes.GetGroupName(self.type_id)

    @property
    def category_id(self):
        return evetypes.GetCategoryID(self.type_id)

    @property
    def category_name(self):
        return evetypes.GetCategoryName(self.type_id)

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        return self.group_name

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


class ItemGroupSuggestion(Suggestion):
    __slots__ = ('group_id',)
    key_attributes = __slots__

    def __init__(self, group_id):
        self.group_id = group_id

    @property
    def name(self):
        return evetypes.GetGroupNameByGroup(self.group_id, important=False)

    @property
    def category_id(self):
        return evetypes.GetCategoryIDByGroup(self.group_id)

    @property
    def category_name(self):
        return evetypes.GetCategoryNameByGroup(self.group_id)

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        return localization.GetByLabel('UI/Common/Group')

    def render_icon(self, size):
        if size > 32:
            size = max(32, size * 0.8)
        return Sprite(width=size, height=size, texturePath=eveicon.folder, color=TextColor.SECONDARY)


class ItemCategorySuggestion(Suggestion):
    __slots__ = ('category_id',)
    key_attributes = __slots__

    def __init__(self, category_id):
        self.category_id = category_id

    @property
    def name(self):
        return evetypes.GetCategoryNameByCategory(self.category_id, important=False)

    @property
    def text(self):
        return self.name

    @property
    def subtext(self):
        return localization.GetByLabel('UI/Common/Category')

    def render_icon(self, size):
        if size > 32:
            size = max(32, size * 0.8)
        return Sprite(width=size, height=size, texturePath=eveicon.folder, color=TextColor.SECONDARY)
