#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragdata\typedragdata.py
import logging
import evelink.client
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from evetypes import TypeNotFoundException
from inventorycommon.typeHelpers import GetIconFile
logger = logging.getLogger(__name__)

class TypeDragData(BaseDragData):

    def __init__(self, typeID):
        super(TypeDragData, self).__init__()
        self.typeID = typeID

    def GetIconTexturePath(self):
        try:
            return GetIconFile(self.typeID) or super(TypeDragData, self).GetIconTexturePath()
        except TypeNotFoundException as e:
            logger.error(e)
            return None

    def get_link(self):
        return evelink.type_link(self.typeID)

    def GetTypeID(self):
        return self.typeID


class ItemDragData(BaseDragData):

    def __init__(self, item = None, itemID = None, typeID = None, isBlueprintCopy = False):
        self.item = item
        self.itemID = itemID
        self.typeID = typeID
        self.isBlueprintCopy = isBlueprintCopy

    def get_link(self):
        if self.item:
            return evelink.item_link(self.item)
        else:
            return evelink.type_link(self.typeID, self.itemID)

    def GetIconTexturePath(self):
        try:
            return GetIconFile(self.typeID) or super(TypeDragData, self).GetIconTexturePath()
        except TypeNotFoundException as e:
            logger.error(e)
            return None

    def GetTypeID(self):
        return self.typeID


class ItemIconDragData(ItemDragData):

    def __init__(self, itemIcon = None):
        super(ItemIconDragData, self).__init__(item=itemIcon.item, itemID=itemIcon.itemID, typeID=itemIcon.typeID, isBlueprintCopy=itemIcon.IsBlueprintCopy())


class ShipDragData(BaseDragData):

    def __init__(self, typeID, itemID = None, ownerID = None, itemName = None):
        super(ShipDragData, self).__init__()
        self.typeID = typeID
        self.itemID = itemID
        self.ownerID = ownerID
        self.itemName = itemName

    def GetIconTexturePath(self):
        try:
            return GetIconFile(self.typeID) or super(TypeDragData, self).GetIconTexturePath()
        except TypeNotFoundException as e:
            logger.error(e)
            return None

    def GetTypeID(self):
        return self.typeID

    def get_link(self):
        return evelink.ship_link(self.typeID, self.itemID, self.ownerID, self.itemName)
