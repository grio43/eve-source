#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\ghostFittingUtil.py
import dogma.const as dogmaConst
import evetypes
ITEM_COUNTER = 0

class GhostFittingDataObject(object):

    def __init__(self, locationID, flagID, typeID, ownerID = None, number = None, originalItemID = None):
        global ITEM_COUNTER
        self.counter = ITEM_COUNTER
        ITEM_COUNTER += 1
        self.locationID = locationID
        self.flagID = flagID
        self.typeID = typeID
        self.originalItemID = originalItemID
        self.number = number
        self.itemID = self.GetItemKey()
        self.categoryID = evetypes.GetCategoryID(typeID)
        self.groupID = evetypes.GetGroupID(typeID)
        self.ownerID = session.charid

    def GetItemKey(self):
        return '%s_%s_%s_%s' % (self.flagID,
         self.typeID,
         self.counter,
         self.originalItemID)


class DBLessGhostFittingDataObject(GhostFittingDataObject):

    def GetItemKey(self):
        return (self.locationID, self.flagID, self.typeID)

    def SetQty(self, qty):
        self.attributes[dogmaConst.attributeQuantity].SetBaseValue(qty)


def GetOriganlItemIDFromItemKey(itemKey):
    parts = itemKey.split('_')
    itemIDString = parts[3]
    try:
        return int(itemIDString)
    except ValueError:
        return None
