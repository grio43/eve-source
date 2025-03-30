#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\pythonEffects\warpDisruptSphere.py
from dogma import const as dogmaConst
from dogma.effects import Effect
from eve.common.lib import appConst as const

class BaseWarpDisruptSphere(Effect):
    __guid__ = 'dogmaXP.WarpDisruptSphere'
    __effectIDs__ = ['effectWarpDisruptSphere']
    __modifier_only__ = 0
    LOCATION_AND_GROUP_MODIFIER_CHANGES = [(dogmaConst.dgmAssPostPercent,
      const.groupPropulsionModule,
      const.attributeSpeedBoostFactor,
      const.attributeSpeedBoostFactorBonus), (dogmaConst.dgmAssPostPercent,
      const.groupPropulsionModule,
      const.attributeSpeedFactor,
      const.attributeSpeedFactorBonus)]
    MODIFIER_CHANGES = [(dogmaConst.dgmAssPostPercent, const.attributeMass, const.attributeMassBonusPercentage), (dogmaConst.dgmAssPostPercent, const.attributeMaxVelocity, const.attributeVelocityModifier), (dogmaConst.dgmAssPostPercent, const.attributeSignatureRadius, const.attributeSignatureRadiusBonus)]

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.AddModifiersOnStart(dogmaLM, itemID, shipID)
        self.ActivateWarpDisruption(dogmaLM, env, itemID, shipID)

    def ActivateWarpDisruption(self, dogmaLM, env, itemID, shipID):
        pass

    def AddModifiersOnStart(self, dogmaLM, itemID, shipID):
        self.AddLocationGroupModifiers(dogmaLM, shipID, itemID)
        self.AddModifiers(dogmaLM, shipID, itemID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        if not otherID:
            self.RemoveModifiersOnStop(dogmaLM, itemID, shipID)
            self.RemoveShipAsWarpDisruptor(dogmaLM, itemID, shipID)

    def RemoveShipAsWarpDisruptor(self, dogmaLM, itemID, shipID):
        pass

    def RemoveModifiersOnStop(self, dogmaLM, itemID, shipID):
        self.RemoveLocationGroupModifiers(dogmaLM, shipID, itemID)
        self.RemoveModifiers(dogmaLM, shipID, itemID)

    RestrictedStop = Stop
