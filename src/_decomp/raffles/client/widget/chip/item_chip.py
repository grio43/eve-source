#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\item_chip.py
import evetypes
import eveui
from raffles.client import texture
from raffles.client.widget.item_icon import ItemIcon
from .chip import Chip

class ItemTypeChip(Chip):
    default_name = 'ItemTypeChip'

    def __init__(self, type_id = None, **kwargs):
        super(ItemTypeChip, self).__init__(**kwargs)
        self.icon = ItemIcon(parent=self, state=eveui.State.disabled, align=eveui.Align.center_left, width=38, height=38, opacity=0.3, left=-4)
        self._type_id = None
        if type_id:
            self.type_id = type_id

    @property
    def type_id(self):
        return self._type_id

    @type_id.setter
    def type_id(self, type_id):
        if self._type_id == type_id:
            return
        self._type_id = type_id
        if type_id:
            self.icon.SetTypeID(type_id)
            self.text = evetypes.GetName(type_id)
        else:
            self.clear()

    def GetDragData(self):
        return [eveui.dragdata.ItemType(self.type_id)]

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=self.type_id, includeMarketDetails=True)


class ItemGroupChip(Chip):
    default_name = 'ItemGroupChip'

    def __init__(self, group_id = None, **kwargs):
        super(ItemGroupChip, self).__init__(**kwargs)
        eveui.Sprite(parent=self, align=eveui.Align.center_left, width=38, height=38, texturePath=texture.group_icon, opacity=0.3, left=-4)
        self._group_id = None
        if group_id:
            self.group_id = group_id

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        if self._group_id == group_id:
            return
        self._group_id = group_id
        if group_id:
            self.text = evetypes.GetGroupNameByGroup(group_id)
        else:
            self.clear()


class ItemCategoryChip(Chip):
    default_name = 'ItemCategoryChip'

    def __init__(self, category_id = None, **kwargs):
        super(ItemCategoryChip, self).__init__(**kwargs)
        self.icon = eveui.Sprite(parent=self, align=eveui.Align.center_left, width=38, height=38, texturePath=texture.group_icon, opacity=0.3, left=-4)
        self._category_id = None
        if category_id:
            self.category_id = category_id

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, category_id):
        if self._category_id == category_id:
            return
        self._category_id = category_id
        if category_id:
            self.text = evetypes.GetCategoryNameByCategory(category_id)
        else:
            self.clear()
