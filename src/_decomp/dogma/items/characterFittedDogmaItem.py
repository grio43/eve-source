#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\characterFittedDogmaItem.py
from dogma.items.fittableDogmaItem import FittableDogmaItem
from eve.common.lib import appConst as const

class CharacterFittedDogmaItem(FittableDogmaItem):

    def GetShipID(self):
        if self.location is None:
            self.dogmaLocation.LogWarn('CharacterFittedDogmaItem::GetShipID - item not fitted to location', self.itemID)
            return
        return self.location.GetShipID()

    def GetCharacterID(self):
        return self.GetPilot()

    def IsValidFittingLocation(self, location):
        return location.groupID == const.groupCharacter


class GhostCharacterFittedDogmaItem(CharacterFittedDogmaItem):
    __guid__ = 'GhostCharacterFittedDogmaItem'

    def GetShipID(self):
        return self.dogmaLocation.shipID
