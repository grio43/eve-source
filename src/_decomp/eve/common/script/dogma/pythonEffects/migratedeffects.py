#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\migratedeffects.py
from dogma.effects import Effect
from dogma.const import *

class MissileEMDmgBonus(Effect):
    __guid__ = 'dogmaXP.MissileEMDmgBonus'
    __effectIDs__ = [660]
    isPythonEffect = True
    __modifies_character__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeDamageMultiplierBonus
    modifiedAttributeID = attributeEmDamage
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class MissileExplosiveDmgBonus(Effect):
    __guid__ = 'dogmaXP.MissileExplosiveDmgBonus'
    __effectIDs__ = [661]
    isPythonEffect = True
    __modifies_character__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeDamageMultiplierBonus
    modifiedAttributeID = attributeExplosiveDamage
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class MissileThermalDmgBonus(Effect):
    __guid__ = 'dogmaXP.MissileThermalDmgBonus'
    __effectIDs__ = [662]
    isPythonEffect = True
    __modifies_character__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeDamageMultiplierBonus
    modifiedAttributeID = attributeThermalDamage
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class MissileKineticDmgBonus2(Effect):
    __guid__ = 'dogmaXP.MissileKineticDmgBonus2'
    __effectIDs__ = [668]
    isPythonEffect = True
    __modifies_character__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeDamageMultiplierBonus
    modifiedAttributeID = attributeKineticDamage
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class CloakingTargetingDelayBonusPostPercentCloakingTargetingDelayBonusForShipModulesRequiringCloaking(Effect):
    __guid__ = 'dogmaXP.CloakingTargetingDelayBonusPostPercentCloakingTargetingDelayBonusForShipModulesRequiringCloaking'
    __effectIDs__ = [848]
    isPythonEffect = True
    __modifier_only__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeCloakingTargetingDelayBonus
    modifiedAttributeID = attributeCloakingTargetingDelay
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class DroneDmgBonus(Effect):
    __guid__ = 'dogmaXP.DroneDmgBonus'
    __effectIDs__ = [1730]
    isPythonEffect = True
    __modifies_character__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeDamageMultiplierBonus
    modifiedAttributeID = attributeDamageMultiplier
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveOwnerRequiredSkillModifier(self.operation, charID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class SelfRof(Effect):
    __guid__ = 'dogmaXP.SelfRof'
    __effectIDs__ = [1851]
    isPythonEffect = True
    __modifier_only__ = True
    __modifies_ship__ = True
    modifyingAttributeID = attributeRofBonus
    modifiedAttributeID = attributeRateOfFire
    operation = dgmAssPostPercent

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.AddLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        affectedSkillID = env.itemTypeID
        affectingModuleID = env.itemID
        env.dogmaLM.RemoveLocationRequiredSkillModifier(self.operation, shipID, affectedSkillID, self.modifiedAttributeID, affectingModuleID, self.modifyingAttributeID)


class TargetPassively(Effect):
    __guid__ = 'dogmaXP.TargetPassively'
    __effectIDs__ = [54]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddTargetEx(shipID, targetID, silent=1, tasklet=1)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class ArmorRepairForEntities(Effect):
    __guid__ = 'dogmaXP.ArmorRepairForEntities'
    __effectIDs__ = [878]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.DecreaseItemAttribute(itemID, attributeArmorDamage, itemID, attributeEntityArmorRepairAmount)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class ShieldBoostingEffect(Effect):
    __guid__ = 'dogmaXP.EntityShieldBoosting'
    __effectIDs__ = [876,
     2192,
     2193,
     2194]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.IncreaseItemAttribute(itemID, attributeShieldCharge, itemID, attributeEntityShieldBoostAmount)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class ArmorRepairingEffect(Effect):
    __guid__ = 'dogmaXP.EntityArmorRepairing'
    __effectIDs__ = [2195, 2196, 2197]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.DecreaseItemAttribute(itemID, attributeArmorDamage, itemID, attributeEntityArmorRepairAmount)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1
