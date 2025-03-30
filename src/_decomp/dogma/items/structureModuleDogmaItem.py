#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\structureModuleDogmaItem.py
from dogma.const import effectOnline
from fittableDogmaItem import FittableDogmaItem
from inventorycommon.const import categoryStructure

class StructureModuleDogmaItem(FittableDogmaItem):

    def IsOnline(self):
        if effectOnline in self.activeEffects:
            return (self.itemID, effectOnline) not in self.dogmaLocation.deactivatingEffects
        else:
            return (self.itemID, effectOnline) in self.dogmaLocation.activatingEffects

    def IsValidFittingLocation(self, location):
        return location.categoryID == categoryStructure

    def GetCharacterID(self):
        return self.GetPilot()

    def GetStructureID(self):
        if self.location:
            return self.location.itemID


class GhostStructureModuleDogmaItem(StructureModuleDogmaItem):

    def GetPilot(self):
        return session.charid
