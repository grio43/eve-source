#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\items\fighterDogmaItem.py
from dogma.items.baseDogmaItem import BaseDogmaItem
from eve.common.script.sys.idCheckers import IsSolarSystem

class FighterDogmaItem(BaseDogmaItem):

    def GetShipItem(self):
        return self.dogmaLocation.GetShipItemForFighter(self.itemID)

    def IsOwnerModifiable(self, locationID = None):
        if not locationID:
            locationID = self.locationID
        if not self.dogmaLocation.IsFighterOwnerModifiablesAtLocation(locationID):
            return False
        if not self.ownerID:
            return False
        pilotShip = self.GetShipItem()
        if not pilotShip:
            return False
        return True

    def GetLocation(self):
        return None

    def AddFighterControllerOwnerModifiers(self):
        for toAttrib, modSet in self._IterOwnerReqSkillModifiers():
            self._ApplyModsToAttrib(modSet, toAttrib, callOnAttributeChanged=True, debugContext='AddFighterControllerOwnerModifiers')

    def RemoveFighterControllerOwnerModifiers(self):
        for toAttrib, modSet in self._IterOwnerReqSkillModifiers():
            for operation, fromAttrib in modSet:
                fromAttrib.RemoveOutgoingModifier(operation, toAttrib)
                toAttrib.RemoveIncomingModifier(operation, fromAttrib)

    def _IterOwnerReqSkillModifiers(self):
        owner = self.dogmaLocation.dogmaItems.get(self.ownerID, None)
        if not owner:
            self.dogmaLocation.broker.LogWarn('_IterOwnerReqSkills could not find its owner?', self.itemID, self.ownerID)
            return
        for skillID in self.reqSkills:
            ownerMods = owner.ownerReqSkillMods.get(skillID, {})
            for attribID, modSet in ownerMods.iteritems():
                if attribID in self.attributes:
                    toAttrib = self.attributes[attribID]
                    yield (toAttrib, modSet)

    def GetCharacterID(self):
        return self.GetPilot()

    def UnsetLocation(self, locationDogmaItem):
        self.flagID = None


class GhostFighterDogmaItem(FighterDogmaItem):

    @apply
    def squadronSize():

        def fget(self):
            return getattr(self, 'stacksize', 0)

        return property(**locals())
