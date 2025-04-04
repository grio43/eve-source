#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\online.py
from dogma.effects import Effect
from dogma.items.locationDogmaItem import LocationDogmaItem

class OnlineEffect(Effect):
    __guid__ = 'dogmaXP.Online'
    __effectIDs__ = ['effectOnline']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogma = sm.GetService('dogma')
        dogma.SkillCheck(env, 'OnlineHasSkillPrerequisites', None)
        capacitorLevel = None
        if dogmaLM.locationGroup == const.groupSolarSystem:
            applyCapacitorCharge = True
            if self._ShouldAppleCapacitorCharge(shipID, env, dogmaLM):
                applyCapacitorCharge = False
            else:
                try:
                    if dogmaLM.CanFitItemInSpace(charID, shipID, itemID):
                        applyCapacitorCharge = False
                except UserError:
                    pass

            if applyCapacitorCharge:
                capacity = dogmaLM.GetAttributeValue(shipID, const.attributeCapacitorCapacity)
                ratio = dogmaLM.GetAttributeValue(shipID, const.attributeCharge) / capacity * 100
                if ratio < const.onlineCapacitorChargeRatio:
                    raise UserError('NotEnoughCapacitorForOnline', {'module': env.itemTypeID,
                     'have': ratio,
                     'need': const.onlineCapacitorChargeRatio})
                capacitorLevel = capacity * (const.onlineCapacitorRemainderRatio / 100.0)
        if not dogmaLM.IsItemLoading(shipID):
            GAV = dogmaLM.GetAttributeValue
            cpuRequired = GAV(itemID, const.attributeCpu)
            cpuOutput = GAV(shipID, const.attributeCpuOutput)
            cpuLoad = GAV(shipID, const.attributeCpuLoad)
            if cpuRequired != 0 and cpuLoad + cpuRequired > cpuOutput + 1e-06:
                dogma.UserError(env, 'NotEnoughCpu', None)
            powerRequired = GAV(itemID, const.attributePower)
            powerOutput = GAV(shipID, const.attributePowerOutput)
            powerLoad = GAV(shipID, const.attributePowerLoad)
            if powerRequired != 0 and powerLoad + powerRequired > powerOutput + 1e-06:
                dogma.UserError(env, 'NotEnoughPower', None)
            containerDogmaItem = dogmaLM.GetDogmaItem(shipID)
            if isinstance(containerDogmaItem, LocationDogmaItem):
                containerDogmaItem.CheckCanOnlineItem(itemID)
        dogmaLM.CheckSlotOnliningAndExistence(shipID, itemID)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 1)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        if capacitorLevel is not None:
            dogmaLM.SetAttributeValue(shipID, const.attributeCharge, capacitorLevel)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)

    def _ShouldAppleCapacitorCharge(self, shipID, env, dogmaLM):
        if dogmaLM.embarkingShips.has_key(shipID) or shipID in dogmaLM.loadingItems:
            return True
        if not charsession:
            return True
        if charsession.GetSessionVariable('SlashCommand', False):
            return True
        return hasattr(env, 'bypassChargeCost')
