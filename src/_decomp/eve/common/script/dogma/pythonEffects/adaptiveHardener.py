#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\adaptiveHardener.py
from dogma.effects import Effect
import dogma.const as dConst

class BaseAdaptiveHardener(Effect):
    __guid__ = 'dogmaXP.AdaptiveHardener'
    __effectIDs__ = ['effectAdaptiveArmorHardener']
    MODIFIER_CHANGES = [(dConst.dgmAssPreMul, dConst.attributeArmorEmDamageResonance, dConst.attributeArmorEmDamageResonance),
     (dConst.dgmAssPreMul, dConst.attributeArmorExplosiveDamageResonance, dConst.attributeArmorExplosiveDamageResonance),
     (dConst.dgmAssPreMul, dConst.attributeArmorKineticDamageResonance, dConst.attributeArmorKineticDamageResonance),
     (dConst.dgmAssPreMul, dConst.attributeArmorThermalDamageResonance, dConst.attributeArmorThermalDamageResonance)]

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self._SetDamageStats(env, dogmaLM, shipID)
        try:
            attributeValuesToUpdate = self._GetAttributeValuesToUpdate(env)
        except AttributeError:
            pass
        else:
            for attributeID, value in attributeValuesToUpdate.iteritems():
                dogmaLM.SetAttributeValue(itemID, attributeID, value, dirty=False)

        self.AddModifiers(dogmaLM, shipID, itemID)

    def _SetDamageStats(self, env, dogmaLM, shipID):
        pass

    def _GetAttributeValuesToUpdate(self, env):
        return {}

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)
        self.ProcessStop(env, dogmaLM, itemID, shipID)

    def ProcessStop(self, env, dogmaLM, itemID, shipID):
        pass

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)
        self.ProcessRestrictStop(env, dogmaLM, itemID)

    def ProcessRestrictStop(self, env, dogmaLM, itemID):
        pass
