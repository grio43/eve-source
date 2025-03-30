#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\pythonEffects.py
import dbuff.common.industrialInvulnConst as invulnConst
import dogma.data as dogma_data
from eve.common.lib import appConst as const
from eve.common.lib.appConst import MSEC
from dbuff.common import baseBurstEffect
from dogma import const as dogmaConst
from dogma.effects import Effect
from dogma.items.locationDogmaItem import LocationDogmaItem
from eve.common.script.dogma.pythonEffects.emergencyHullEnergizer import EmergencyHullEnergizer
from eve.common.script.dogma.pythonEffects.remoteTargetPaintFalloff import BaseRemoteTargetPaintFalloff
from eve.common.script.dogma.pythonEffects.remoteTrackingComputer import BaseRemoteTrackingComputer
from eve.common.script.dogma.pythonEffects.remoteWebifierFalloff import BaseRemoteWebifierFalloff
from eve.common.script.dogma.pythonEffects.sensorFalloff import BaseSensorFalloffEffect
from eve.common.script.dogma.pythonEffects.weaponDisruptionUtil import GetGuidanceDisruptionAttributes, GetTrackingDisruptionAttributes, GetWeaponDisruptionAttributes
import inventorycommon.const as invConst
from eveexceptions import UserError

class Attack(Effect):
    __guid__ = 'testAttack'
    __effectIDs__ = ['effectTargetAttack',
     'effectTargetAttackForStructures',
     'effectProjectileFired',
     'effectProjectileFiredForEntities']

    def __init__(self, *args):
        pass


class OnlineEffect(Effect):
    __guid__ = 'OnlineEffect'
    __effectIDs__ = ['effectOnline']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        containerDogmaItem = dogmaLM.GetDogmaItem(shipID)
        if isinstance(containerDogmaItem, LocationDogmaItem):
            containerDogmaItem.CheckCanOnlineItem(itemID)
        dogma = sm.GetService('dogma')
        cpuOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuOutput)
        cpuLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuLoad)
        cpu = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeCpu)
        if self.HasEnoughCpuLeft(cpu, cpuLoad, cpuOutput):
            powerOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerOutput)
            powerLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerLoad)
            power = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributePower)
            if self.HasEnoughPowerLeft(power, powerLoad, powerOutput):
                dogmaLM.SetAttributeValue(itemID, dogmaConst.attributeIsOnline, 1)
                dogmaLM.AddModifier(dogmaConst.dgmAssModAdd, shipID, dogmaConst.attributeCpuLoad, itemID, dogmaConst.attributeCpu)
                dogmaLM.AddModifier(dogmaConst.dgmAssModAdd, shipID, dogmaConst.attributePowerLoad, itemID, dogmaConst.attributePower)
            else:
                dogma.UserError(env, 'NotEnoughPower', None)
        else:
            dogma.UserError(env, 'NotEnoughCpu', None)

    def HasEnoughCpuLeft(self, cpu, cpuLoad, cpuOutput):
        if self.ShouldIgnoreCpuPowerRestrictions():
            return True
        hasEnoughPowerLeft = cpuOutput >= cpuLoad + cpu
        return hasEnoughPowerLeft

    def HasEnoughPowerLeft(self, power, powerLoad, powerOutput):
        if self.ShouldIgnoreCpuPowerRestrictions():
            return True
        if power == 0:
            return True
        return powerOutput >= powerLoad + power

    def ShouldIgnoreCpuPowerRestrictions(self):
        return True

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(dogmaConst.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)


class Powerboost(Effect):
    __guid__ = 'dogmaXP.Effect_48'
    __effectIDs__ = [48]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        weaponID = env.itemID
        shipID = env.shipID
        item = dogmaLM.dogmaItems[weaponID]
        chargeKey = dogmaLM.GetSubLocation(shipID, item.flagID)
        if chargeKey is None:
            return 1
        chargeQuantity = dogmaLM.GetAttributeValue(chargeKey, const.attributeQuantity)
        if chargeQuantity is None or chargeQuantity < 1:
            return 1
        capacitorBonus = dogmaLM.GetAttributeValue(chargeKey, const.attributeCapacitorBonus)
        if capacitorBonus != 0:
            new, old = dogmaLM.IncreaseItemAttributeEx(env.shipID, const.attributeCharge, capacitorBonus, alsoReturnOldValue=True)
        return 1

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class Mine(Effect):
    __guid__ = 'dogmaXP.Mining'
    __effectIDs__ = ['effectMining', 'effectMiningLaser', 'effectMiningClouds']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, asteroidID):
        durationAttributeID = dogma_data.get_effect(env.effectID).durationAttributeID
        duration = dogmaLM.GetAttributeValue(itemID, durationAttributeID)
        env.miningDuration = duration
        import blue
        env.startedEffect = blue.os.GetSimTime()

    def GetClamp(self, env, preferredDuration):
        import blue
        timePassed = blue.os.GetSimTime() - env.startedEffect
        millisecondsPassed = timePassed / 10000L
        return float(millisecondsPassed) / preferredDuration


class FakeCloaking(Effect):
    __guid__ = 'dogmaXP.Cloaking'
    __effectIDs__ = ['effectCloaking', 'effectCloakingWarpSafe', 'effectCloakingPrototype']
    effectIDList = None

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID, internal = False):
        if dogmaLM.IsShipCloaked():
            raise UserError('CantCloakTooManyDevices')
        if not dogmaLM.GetAttributeValue(shipID, const.attributeCanCloak):
            raise UserError('CantCloakTooShipUnsuitable')
        for effectID, itemID, activationInfo, typeID in dogmaLM.GetActivatedEffectsOnShip():
            if dogmaLM.dogmaStaticMgr.GetTypeAttribute2(typeID, const.attributeDisallowEarlyDeactivation):
                raise UserError('CantCloakModuleActive', {'module': (const.UE_TYPEID, typeID)})

        if dogmaLM.GetAttributeValue(shipID, const.attributeDisallowCloaking):
            raise UserError('CantCloak')

    def EnforceActivationConditions(self, dogmaLM, shipID, itemID, effectID):
        dogmaLM.DeactivateActivatedEffectsOfShip(excludeEffectKey=(effectID, itemID))

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        env.cloaked = 0
        self.EnforceActivationConditions(dogmaLM, shipID, itemID, env.effectID)
        dogmaLM.AddModifier(4, shipID, const.attributeMaxVelocity, itemID, const.attributeMaxVelocityBonus)
        self._Start_Effect(dogmaLM, env, shipID, itemID)

    def _Start_Effect(self, dogmaLM, env, shipID, itemID):
        try:
            self.PreStartChecks(env, dogmaLM, itemID, shipID, env.charID, env.otherID, env.targetID, internal=True)
        except UserError as e:
            dogmaLM.StopEffect(env.effectID, itemID, 1, forced=1)
            return

        self.EnforceActivationConditions(dogmaLM, shipID, itemID, env.effectID)
        env.cloaked = 1

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RestrictedStop(env, dogmaLM, itemID, shipID, charID, otherID, targetID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        env.cloaked = -1
        dogmaLM.RemoveModifier(4, shipID, const.attributeMaxVelocity, itemID, const.attributeMaxVelocityBonus)


class FakeBaseCommandBurstEffect(Effect):
    sourceVFXEffect = None
    targetVFXEffect = None

    def PreStartChecks(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID = None, targetID = None):
        buffValues, effectDurationMillis = baseBurstEffect.GetBuffValuesAndDurationMillis(dogmaLM, itemID)
        buffDuration = effectDurationMillis * MSEC
        baseBurstEffect.ApplyBuffToSourceShip(dogmaLM, charID, shipID, buffDuration, buffValues)


@baseBurstEffect.BurstEffectDecorator(baseBurstEffect.GetArmorEffectClassVariables())

class CommandBurstArmorEffect(FakeBaseCommandBurstEffect):
    pass


@baseBurstEffect.BurstEffectDecorator(baseBurstEffect.GetInfoEffectClassVariables())

class CommandBurstInfoEffect(FakeBaseCommandBurstEffect):
    pass


@baseBurstEffect.BurstEffectDecorator(baseBurstEffect.GetMiningEffectClassVariables())

class CommandBurstMiningEffect(FakeBaseCommandBurstEffect):
    pass


@baseBurstEffect.BurstEffectDecorator(baseBurstEffect.GetShieldEffectClassVariables())

class CommandBurstShieldEffect(FakeBaseCommandBurstEffect):
    pass


@baseBurstEffect.BurstEffectDecorator(baseBurstEffect.GetSkirmishEffectClassVariables())

class CommandBurstSkirmishEffect(FakeBaseCommandBurstEffect):
    pass


class FakeTitanBurstEffect(Effect):
    __guid__ = 'dogmaXP.TitanBurstEffect'
    __effectIDs__ = ['effectModuleTitanBurst']

    def Start(self, env, dogmaLM, itemID, shipID, charID, *args):
        effectDuration = 10000000
        buffValues, effectDurationMillis = baseBurstEffect.GetBuffValuesAndDurationMillis(dogmaLM, itemID)
        buffDuration = effectDurationMillis * MSEC
        baseBurstEffect.ApplyBuffToSourceShip(dogmaLM, charID, shipID, buffDuration, buffValues)


class FakeIndustrialInvulnerability(Effect):
    __guid__ = 'dogmaXP.IndustrialInvulnerability'
    __effectIDs__ = ['effectModuleBonusIndustrialInvulnerability']
    DBUFF_VALUES = invulnConst.DBUFF_VALUES

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        effectDuration = 10000000
        baseBurstEffect.ApplyBuffToSourceShip(dogmaLM, charID, shipID, effectDuration, self.DBUFF_VALUES)
        dogmaLM.DeactivateBlockedActivatedEffectsOfShip()


class FakeCargoScan(Effect):
    __guid__ = 'dogmaXP.Effect_47'
    __effectIDs__ = [47]
    isPythonEffect = True


class FakeShipScan(Effect):
    __guid__ = 'dogmaXP.Effect_46'
    __effectIDs__ = [46]
    isPythonEffect = True


class FakePointDefense(Effect):
    __guid__ = 'dogmaXP.Effect_6443'
    __effectIDs__ = [6443]
    isPythonEffect = False


class FakeTargetHostile(Effect):
    __guid__ = 'dogmaXP.Effect_55'
    __effectIDs__ = [55]
    isPythonEffect = True


class FakeEmpWave(Effect):
    __guid__ = 'dogmaXP.Effect_38'
    __effectIDs__ = [38]
    isPythonEffect = True


class FakeSurveyScan(Effect):
    __guid__ = 'dogmaXP.Effect_81'
    __effectIDs__ = [81]
    isPythonEffect = True


class FakeTargetABCAttack(Effect):
    __guid__ = 'dogmaXP.Effect_6995'
    __effectIDs__ = [6995]
    isPythonEffect = False


class FakeEntosisLinkEffect(Effect):
    __guid__ = 'dogmaXP.Effect_6063'
    __effectIDs__ = [6063]
    isPythonEffect = False
    MODIFIER_CHANGES = [(dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanRadarStrength, dogmaConst.attributeScanRadarStrengthPercent),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanMagnetometricStrength, dogmaConst.attributeScanMagnetometricStrengthPercent),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanGravimetricStrength, dogmaConst.attributeScanGravimetricStrengthPercent),
     (dogmaConst.dgmAssPostPercent, dogmaConst.attributeScanLadarStrength, dogmaConst.attributeScanLadarStrengthPercent)]

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.AddModifiers(dogmaLM, shipID, itemID)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.RemoveModifiers(dogmaLM, shipID, itemID)


class FakeEmergencyHullEnergizer(EmergencyHullEnergizer):

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self.AddModifiers(dogmaLM, shipID, itemID)


class FakeSensorFalloffEffect(BaseSensorFalloffEffect):
    __guid__ = 'dogmaXP.RemoteSensorBooster'
    __effectIDs__ = [dogmaConst.effectRemoteSensorBoostFalloff, dogmaConst.effectRemoteSensorDampFalloff, dogmaConst.effectStructureModuleEffectRemoteSensorDampener]


class FakeRemoteTrackingComputer(BaseRemoteTrackingComputer):
    __guid__ = 'dogmaXP.RemoteTrackingComputer'
    __effectIDs__ = [dogmaConst.effectShipModuleRemoteTrackingComputer]


class FakeWeaponDisruption(Effect):
    __guid__ = 'dogmaXP.WeaponDisruption'
    __effectIDs__ = [dogmaConst.effectStructureModuleEffectWeaponDisruption]
    WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY = GetWeaponDisruptionAttributes()
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = [ (dogmaConst.dgmAssPostPercent,
     skillTypeID,
     affectedAttributeID,
     affectingAttributeID) for skillTypeID, affectingAttributeID, affectedAttributeID in WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY.get(invConst.categoryShip, []) ]


class FakeTrackingDisruption(Effect):
    __guid__ = 'dogmaXP.TrackingDisruption'
    __effectIDs__ = [dogmaConst.effectShipModuleTrackingDisruptor]
    WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY = GetTrackingDisruptionAttributes()
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = [ (dogmaConst.dgmAssPostPercent,
     skillTypeID,
     affectedAttributeID,
     affectingAttributeID) for skillTypeID, affectingAttributeID, affectedAttributeID in WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY.get(invConst.categoryShip, []) ]


class FakeGuidanceDisruption(Effect):
    __guid__ = 'dogmaXP.GuidanceDisruption'
    __effectIDs__ = [dogmaConst.effectShipModuleGuidanceDisruptor]
    WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY = GetGuidanceDisruptionAttributes()
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = [ (dogmaConst.dgmAssPostPercent,
     skillTypeID,
     affectedAttributeID,
     affectingAttributeID) for skillTypeID, affectingAttributeID, affectedAttributeID in WEAPON_DISRUPTION_ATTRIBUTES_BY_CATEGORY.get(invConst.categoryShip, []) ]


class FakeRemoteTargetPaintFalloff(BaseRemoteTargetPaintFalloff):
    __guid__ = 'dogmaXP.RemoteTargetPaintFalloff'
    __effectIDs__ = [dogmaConst.effectRemoteTargetPaintFalloff, dogmaConst.effectStructureModuleEffectTargetPainter]


class FakeRemoteWebifierFalloff(BaseRemoteWebifierFalloff):
    __guid__ = 'dogmaXP.RemoteWebifierFalloff'
    __effectIDs__ = [dogmaConst.effectRemoteWebifierFalloff, dogmaConst.effectStructureModuleEffectStasisWebifier]
