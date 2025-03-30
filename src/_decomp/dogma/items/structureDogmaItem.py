#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\structureDogmaItem.py
import weakref
from inventorycommon.util import IsStructureFittingFlag, IsFighterTubeFlag
from locationDogmaItem import LocationDogmaItem
import dogma.const

class StructureDogmaItem(LocationDogmaItem):

    def __init__(self, *args, **kwargs):
        self.drones = {}
        LocationDogmaItem.__init__(self, *args, **kwargs)

    def OnItemLoaded(self):
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        LocationDogmaItem.OnItemLoaded(self)

    def PostLoadAction(self):
        super(StructureDogmaItem, self).PostLoadAction()
        self.dogmaLocation.UpdateStructureServices(self.itemID)

    def ValidFittingFlag(self, flagID):
        return IsStructureFittingFlag(flagID) or IsFighterTubeFlag(flagID)

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.categoryID in (const.categoryStructureModule, const.categoryCharge) and self.ValidFittingFlag(flagID):
            return True
        elif dogmaItem.groupID == const.groupCharacter and flagID == const.flagPilot:
            return True
        elif dogmaItem.itemID == self.itemID:
            return True
        else:
            return False

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationID != self.itemID:
            raise RuntimeError('ShipDogmaItem.SetLocation::locationID is not ship (%s, %s)' % (locationID, self.itemID))
        self.fittedItems[locationID] = weakref.proxy(self)
        self.flagID = flagID

    def IsOnline(self):
        return True

    def IsActive(self):
        return False

    def RegisterPilot(self, item):
        self.fittedItems[item.itemID] = weakref.proxy(item)

    def UnregisterPilot(self, item):
        self.fittedItems.pop(item.itemID, None)

    def GetCharacterID(self):
        return None

    def GetPilot(self):
        return self.dogmaLocation.pilotsByShipID.get(self.itemID, None)

    def GetHeatStates(self):
        return {attribute:self.attributes[attribute].GetHeatMessage() for attribute in dogma.heatAttributes}

    def GetHeatValues(self):
        return {attribute:0 for attribute in dogma.heatAttributes}

    def GetDrones(self):
        return {}

    def GetDronesInBay(self):
        return {}

    def GetDronesInSpace(self):
        return {}

    def IsItemIDInDrones(self, itemID):
        return itemID in self.drones

    @property
    def overloadedModules(self):
        return set()

    def GetStructureID(self):
        return self.itemID


FAKE_FLAGID = -1

class GhostStructureDogmaItem(StructureDogmaItem):
    __guid__ = 'GhostStructureDogmaItem'

    def RegisterFittedItem(self, dogmaItem, flagID):
        if flagID in (FAKE_FLAGID, None):
            return
        StructureDogmaItem.RegisterFittedItem(self, dogmaItem, flagID)

    def UnregisterFittedItem(self, dogmaItem):
        if dogmaItem.flagID in (FAKE_FLAGID, None):
            return
        StructureDogmaItem.UnregisterFittedItem(self, dogmaItem)

    def GetPilot(self):
        return session.charid
