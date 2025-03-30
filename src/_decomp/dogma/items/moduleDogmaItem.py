#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\moduleDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
from utillib import KeyVal
import dogma.const as dgmconst

class ModuleDogmaItem(FittableDogmaItem):

    def GetCharacterID(self):
        return self.GetPilot()

    def IsOnline(self):
        return dgmconst.effectOnline in self.activeEffects

    def IsValidFittingLocation(self, location):
        return location.categoryID == const.categoryShip


class GhostModuleDogmaItem(ModuleDogmaItem):

    def GetPilot(self):
        return session.charid
