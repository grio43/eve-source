#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\controlTowerDogmaItem.py
import inventorycommon.const as invconst
from dogma.items.locationDogmaItem import LocationDogmaItem

class ControlTowerDogmaItem(LocationDogmaItem):

    def OnItemLoaded(self):
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        LocationDogmaItem.OnItemLoaded(self)

    def GetCharacterID(self):
        return None

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.itemID == self.itemID:
            return True
        if dogmaItem.categoryID == invconst.categoryStarbase and dogmaItem.groupID != invconst.groupControlTower:
            return True
        return False

    def GetShip(self):
        return self.itemID
