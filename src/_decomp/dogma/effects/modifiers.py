#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\modifiers.py


class BaseModifier(object):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID):
        self.operator = operator
        self.domain = domain
        self.modifiedAttributeID = modifiedAttributeID
        self.modifyingAttributeID = modifyingAttributeID
        self.isShipModifier = domain == 'shipID'
        self.isCharModifier = domain == 'charID'
        self.isStuctureModifier = domain == 'structureID'
        self.isOtherModifier = domain == 'otherID'

    def _GetDomainID(self, env):
        if self.domain is None:
            return env.itemID
        return getattr(env, self.domain)

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self._GetStartFunc(dogmaLM)(*self._GetArgs(env, itemID))

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self._GetStopFunc(dogmaLM)(*self._GetArgs(env, itemID))

    def IsShipModifier(self):
        return self.isShipModifier

    def IsCharModifier(self):
        return self.isCharModifier

    def IsStructureModifier(self):
        return self.isStuctureModifier

    def IsOtherModifier(self):
        return self.isOtherModifier


class ItemModifier(BaseModifier):

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveModifier


def _GetItemModifier(modifier):
    return ItemModifier(modifier.operation, modifier.domain, modifier.modifiedAttributeID, modifier.modifyingAttributeID)


class LocationModifier(ItemModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationModifier


def _GetLocationModifier(modifier):
    return LocationModifier(modifier.operation, modifier.domain, modifier.modifiedAttributeID, modifier.modifyingAttributeID)


class RequiredSkillModifier(BaseModifier):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID, skillTypeID):
        super(RequiredSkillModifier, self).__init__(operator, domain, modifiedAttributeID, modifyingAttributeID)
        self.skillTypeID = skillTypeID

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.skillTypeID,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)


class LocationRequiredSkillModifier(RequiredSkillModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationRequiredSkillModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationRequiredSkillModifier


def _GetLocationRequiredSkillModifier(modifer):
    return LocationRequiredSkillModifier(modifer.operation, modifer.domain, modifer.modifiedAttributeID, modifer.modifyingAttributeID, modifer.skillTypeID)


class OwnerRequiredSkillModifier(RequiredSkillModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddOwnerRequiredSkillModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveOwnerRequiredSkillModifier

    def IsShipModifier(self):
        return True

    def IsCharModifier(self):
        return True


def _GetOwnerRequiredSkillModifier(modifier):
    return OwnerRequiredSkillModifier(modifier.operation, modifier.domain, modifier.modifiedAttributeID, modifier.modifyingAttributeID, modifier.skillTypeID)


class LocationGroupModifier(BaseModifier):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID, groupID):
        super(LocationGroupModifier, self).__init__(operator, domain, modifiedAttributeID, modifyingAttributeID)
        self.groupID = groupID

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.groupID,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationGroupModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationGroupModifier


def _GetLocationGroupModifier(modifier):
    return LocationGroupModifier(modifier.operation, modifier.domain, modifier.modifiedAttributeID, modifier.modifyingAttributeID, modifier.groupID)


class NoOpModifier(object):

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def IsShipModifier(self):
        return False

    def IsCharModifier(self):
        return False

    def IsStructureModifier(self):
        return False


def _GetNoOpModifier(effectDict):
    return NoOpModifier()


modifierGetterByType = {'ItemModifier': _GetItemModifier,
 'LocationRequiredSkillModifier': _GetLocationRequiredSkillModifier,
 'OwnerRequiredSkillModifier': _GetOwnerRequiredSkillModifier,
 'LocationModifier': _GetLocationModifier,
 'LocationGroupModifier': _GetLocationGroupModifier}

def GetModifierClassByTypeString(modifierType):
    return modifierGetterByType.get(modifierType)
