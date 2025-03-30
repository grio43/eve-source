#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\emergencyHullEnergizer.py
import dogma.const as dogmaconst
from dogma.effects import Effect

class EmergencyHullEnergizer(Effect):
    __guid__ = 'dogmaXP.EmergencyHullEnergizer'
    __effectIDs__ = ['effectEmergencyHullEnergizer']
    MODIFIER_CHANGES = [(dogmaconst.dgmAssPostMul, dogmaconst.attributeEmDamageResonance, dogmaconst.attributeHullEmDamageResonance),
     (dogmaconst.dgmAssPostMul, dogmaconst.attributeThermalDamageResonance, dogmaconst.attributeHullThermalDamageResonance),
     (dogmaconst.dgmAssPostMul, dogmaconst.attributeKineticDamageResonance, dogmaconst.attributeHullKineticDamageResonance),
     (dogmaconst.dgmAssPostMul, dogmaconst.attributeExplosiveDamageResonance, dogmaconst.attributeHullExplosiveDamageResonance)]

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.SetAttributeValue(itemID, dogmaconst.attributeDamage, dogmaLM.GetAttributeValue(itemID, dogmaconst.attributeHp))
        self.AddModifiers(dogmaLM, shipID, itemID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)

    RestrictedStop = Stop
