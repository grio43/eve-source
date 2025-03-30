#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\propulsionModules.py
import dogma.const as dogmaconst
from dogma.effects import Effect
from dogma.attributes import LiteralAttribute
SPEED_BOOST_FACTOR_CALC = 0.01

class Afterburner(Effect):
    __guid__ = 'dogmaXP.Afterburner'
    __effectIDs__ = ['effectModuleBonusAfterburner']
    MODIFIER_CHANGES = [(dogmaconst.dgmAssModAdd, dogmaconst.attributeMass, dogmaconst.attributeMassAddition)]
    speedFactorAttribute = dogmaconst.attributeSpeedFactor
    speedBoostFactorAttribute = dogmaconst.attributeSpeedBoostFactor

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.AddModifiers(dogmaLM, shipID, itemID)
        self._AddSpeedMultiplierModifier(env, dogmaLM, itemID, shipID)

    def _AddSpeedMultiplierModifier(self, env, dogmaLM, itemID, shipID):
        speedFactor = dogmaLM.GetAttributeValue(itemID, self.speedFactorAttribute)
        speedBoostFactor = dogmaLM.GetAttributeValue(itemID, self.speedBoostFactorAttribute)
        shipMass = dogmaLM.GetAttributeValue(shipID, dogmaconst.attributeMass)
        speedMultiplier = 1 + SPEED_BOOST_FACTOR_CALC * speedFactor * speedBoostFactor / shipMass
        env.afterburner_speedMultiplierAttribute = LiteralAttribute(speedMultiplier)
        dogmaLM.AddModifierWithSource(dogmaconst.dgmAssPostMul, shipID, dogmaconst.attributeMaxVelocity, env.afterburner_speedMultiplierAttribute)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)
        self._RemoveSpeedMultiplierModifier(env, dogmaLM, shipID)

    def _RemoveSpeedMultiplierModifier(self, env, dogmaLM, shipID):
        dogmaLM.RemoveModifierWithSource(dogmaconst.dgmAssPostMul, shipID, dogmaconst.attributeMaxVelocity, env.afterburner_speedMultiplierAttribute)

    def RefreshEffect(self, dogmaLM, env, itemID, shipID):
        isThere = dogmaLM.IsAttributeInIcomingModifiers(shipID, dogmaconst.attributeMaxVelocity, env.afterburner_speedMultiplierAttribute, dogmaconst.dgmAssPostMul)
        if not isThere:
            return
        self._RemoveSpeedMultiplierModifier(env, dogmaLM, shipID)
        self._AddSpeedMultiplierModifier(env, dogmaLM, itemID, shipID)

    RestrictedStop = Stop


class Microwarpdrive(Afterburner):
    __guid__ = 'dogmaXP.Microwarpdrive'
    __effectIDs__ = ['effectModuleBonusMicrowarpdrive']
    MODIFIER_CHANGES = Afterburner.MODIFIER_CHANGES + [(dogmaconst.dgmAssPostPercent, dogmaconst.attributeSignatureRadius, dogmaconst.attributeSignatureRadiusBonus)]
