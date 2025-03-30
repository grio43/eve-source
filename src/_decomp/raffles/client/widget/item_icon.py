#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\item_icon.py
import evelink.client
import evetypes
import eveui
from carbonui import TextColor
from eve.client.script.ui.shared.tooltip.dynamicItem import AddDynamicItemAttributes
from eve.client.script.ui.shared.tooltip.blueprints import AddBlueprintInfo
from eve.client.script.ui.control.itemIcon import ItemIcon as ItemIconBase
from eveui.audio import Sound
from menucheckers.itemCheckers import ItemChecker
from raffles.client.util import get_item_name

class ItemIcon(ItemIconBase):
    default_width = 64
    default_height = 64
    default_align = eveui.Align.center

    def __init__(self, item = None, item_id = None, type_id = None, is_copy = False, **kwargs):
        super(ItemIcon, self).__init__(**kwargs)
        self._item = None
        if item:
            self.item = item
        elif item_id:
            self.SetTypeIDandItemID(type_id, item_id, isCopy=is_copy)
        elif type_id:
            self.SetTypeID(type_id, isCopy=is_copy)

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item):
        self._item = item
        if item is None:
            self.SetTypeIDandItemID(None, None)
        else:
            self.SetTypeIDandItemID(item.typeID, item.itemID, isCopy=ItemChecker(item).IsBlueprintCopy())

    def OnMouseEnter(self, *args):
        Sound.button_hover.play()
        super(ItemIcon, self).OnMouseEnter(*args)

    def OnClick(self):
        if self.typeID is not None:
            super(ItemIcon, self).OnClick()

    def GetDragData(self):
        return [ItemIconDragData(self)]

    def LoadTooltipPanel(self, tooltip_panel, *args):
        if not self.typeID:
            return
        tooltip_panel.LoadGeneric2ColumnTemplate()
        tooltip_panel.margin = (12, 8, 12, 8)
        tooltip_panel.AddLabelSmall(text=evetypes.GetGroupName(self.typeID), colSpan=2, wrapWidth=200, color=TextColor.SECONDARY)
        tooltip_panel.AddLabelMedium(text=get_item_name(self.typeID, item_id=self.itemID), colSpan=2, bold=True, wrapWidth=200)
        AddBlueprintInfo(tooltip_panel, self.itemID, self.typeID, spacerHeight=6)
        AddDynamicItemAttributes(tooltip_panel, self.itemID, self.typeID, spacerHeight=6)


class ItemIconDragData(object):

    def __init__(self, item_icon):
        self.item = item_icon.item
        self.typeID = item_icon.typeID
        self.itemID = item_icon.itemID
        self.isCopy = item_icon.IsBlueprintCopy()

    def get_link(self):
        if self.item:
            return evelink.item_link(self.item)
        else:
            return evelink.type_link(self.typeID, self.itemID)

    def LoadIcon(self, icon, dad, *args):
        icon.LoadIconByTypeID(typeID=self.typeID, itemID=self.itemID, isCopy=self.isCopy)
