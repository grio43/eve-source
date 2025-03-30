#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\fittingDogmaLocationUtil.py
import math
from collections import defaultdict
from math import sqrt, log, exp
import evetypes
from inventorycommon.const import groupMissileLauncherDot
from itertoolsext import Bundle
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_2, GetAbilityIDForSlot
from fighters.abilityAttributes import GetDogmaAttributeIDsForAbilityID, FIGHTER_DAMAGE_ATTRIBUTES, GetDamageMultiplierAttributeFromAbilityID, GetAbilityDurationAttributeID, GetAbilityRangeAndFalloffAttributeIDs
from fighters import GetMaxSquadronSize
from utillib import KeyVal
CAP_STABLE_TIME = const.HOUR
DAMAGE_ATTRIBUTES = (const.attributeEmDamage,
 const.attributeExplosiveDamage,
 const.attributeKineticDamage,
 const.attributeThermalDamage)
DURATION_ATTRIBUTES = [const.attributeFighterAbilityAttackMissileDuration, const.attributeFighterAbilityMissilesDuration, const.attributeFighterAbilityAttackTurretDuration]

def GetFittingItemDragData(itemID, dogmaLocation):
    dogmaItem = dogmaLocation.dogmaItems[itemID]
    data = Bundle()
    data.__guid__ = 'listentry.Item'
    data.item = KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeQuantity) or getattr(dogmaItem, 'stacksize', 1), singleton=False)
    data.flagID = dogmaItem.flagID
    data.isFitted = True
    data.rec = data.item
    data.typeID = dogmaItem.typeID
    data.itemID = itemID
    data.viewMode = 'icons'
    return [data]


def GetFittedItemsByFlag(dogmaLocation):
    typeHasEffectFunc = dogmaLocation.dogmaStaticMgr.TypeHasEffect
    chargesByFlag = {}
    turretsByFlag = {}
    launchersByFlag = {}
    aoeWeaponsByFlag = {}
    dotLaunchersByFlag = {}
    IsTurret = lambda typeID: typeHasEffectFunc(typeID, const.effectTurretFitted)
    IsLauncher = lambda typeID: typeHasEffectFunc(typeID, const.effectLauncherFitted) or typeHasEffectFunc(typeID, const.effectUseMissiles)
    IsAOE = lambda itemID: dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeEmpFieldRange)
    for module in dogmaLocation.GetFittedItemsToShip().itervalues():
        if IsTurret(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            turretsByFlag[module.flagID] = module.itemID
        elif IsLauncher(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            if module.groupID == groupMissileLauncherDot:
                dotLaunchersByFlag[module.flagID] = module.itemID
            else:
                launchersByFlag[module.flagID] = module.itemID
        elif module.categoryID == const.categoryCharge:
            chargesByFlag[module.flagID] = module.itemID
        elif IsAOE(module.itemID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            aoeWeaponsByFlag[module.flagID] = module.itemID

    return (chargesByFlag,
     launchersByFlag,
     turretsByFlag,
     aoeWeaponsByFlag,
     dotLaunchersByFlag)


def GetAlphaStrike(dogmaLocation):
    chargesByFlag, launchersByFlag, turretsByFlag, aoeWeaponsByFlag, dotLaunchersByFlag = GetFittedItemsByFlag(dogmaLocation)
    GAV = dogmaLocation.GetAccurateAttributeValue
    alpha = 0.0
    ownerID = session.charid
    for flagID, itemID in launchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        damagePerShot = _GetLauncherDamagePerShot(dogmaLocation, chargeKey, itemID, ownerID, GAV)
        alpha += damagePerShot

    for flagID, itemID in turretsByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        damagePerShot = _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV)
        alpha += damagePerShot

    for flagID, itemID in dotLaunchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        damagePerHit = GetDotDps(chargeKey, itemID, GAV)
        alpha += damagePerHit

    for flagID, itemID in aoeWeaponsByFlag.iteritems():
        damagePerHit = GetDamageFromItem(dogmaLocation, itemID)
        alpha += damagePerHit

    return alpha


def _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag):
    turretDps = 0.0
    turretDpsWithReload = 0.0
    for flagID, itemID in turretsByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        thisTurretDps, thisTurretDpsWithReload = GetTurretDps(dogmaLocation, chargeKey, itemID, GAV)
        turretDps += thisTurretDps
        turretDpsWithReload += thisTurretDpsWithReload

    return (turretDps, turretDpsWithReload)


def _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem):
    missileDps = 0.0
    missilDpsWithReload = 0.0
    for flagID, itemID in launchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        if chargeKey is None:
            continue
        ownerID = session.charid
        thisLauncherDps, thisLauncherDpsWithReload = GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV)
        missileDps += thisLauncherDps
        missilDpsWithReload += thisLauncherDpsWithReload

    return (missileDps, missilDpsWithReload)


def _GetDotDps(GAV, chargesByFlag, dotLaunchersByFlagID):
    dotDps = 0.0
    for flagID, itemID in dotLaunchersByFlagID.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        if chargeKey is None:
            continue
        dotDps += GetDotDps(chargeKey, itemID, GAV)

    return dotDps


def _GetAoeDps(GAV, aoeWeaponsByFlag, dogmaLocation):
    dps = 0.0
    for flagID, itemID in aoeWeaponsByFlag.iteritems():
        damage = GetDamageFromItem(dogmaLocation, itemID)
        duration = GAV(itemID, const.attributeDuration)
        if not duration:
            continue
        missileDps = damage / duration
        dps += missileDps

    return dps * 1000


def GetAllDpsInfo(shipID, dogmaLocation):
    dpsInfo = GetTurretMissileAndAoeDps(shipID, dogmaLocation)
    from shipfitting.droneUtil import GetDroneDps
    droneDps, _ = GetDroneDps(shipID, dogmaLocation)
    dpsInfo.droneDps = droneDps
    fighterDamage, dpsByTubeID, dpsByPrimaryAbilityID, dpsBySecondaryAbilityID = GetFighterDamage(dogmaLocation)
    totalFighterDps = sum(dpsByTubeID.values())
    dpsInfo.fighterDps = totalFighterDps
    dpsInfo.dpsByPrimaryAbilityID = dpsByPrimaryAbilityID
    dpsInfo.dpsBySecondaryAbilityID = dpsBySecondaryAbilityID
    dpsInfo.totalDps += droneDps + totalFighterDps
    dpsInfo.totalDpsWithReload += droneDps + totalFighterDps
    return dpsInfo


def GetTotalFighterDps(dogmaLocation):
    fighterDamage, dpsByTubeID, dpsByPrimaryAbilityID, dpsBySecondaryAbilityID = GetFighterDamage(dogmaLocation)
    totalFighterDps = sum(dpsByTubeID.values())
    return totalFighterDps


def GetTurretMissileAndAoeDps(shipID, dogmaLocation):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    GAV = dogmaLocation.GetAttributeValue
    if getattr(dogmaLocation, 'godma', False):
        godmaShipItem = dogmaLocation.godma.GetItem(shipID)
        if godmaShipItem is not None:
            GAV = dogmaLocation.GetGodmaAttributeValue
    chargesByFlag, launchersByFlag, turretsByFlag, aoeWeaponsByFlag, dotLaunchersByFlag = GetFittedItemsByFlag(dogmaLocation)
    turretDps, turretDpsWithReload = _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag)
    missileDps, missileDpsWithReload = _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem)
    dotDps = _GetDotDps(GAV, chargesByFlag, dotLaunchersByFlag)
    aoeDps = _GetAoeDps(GAV, aoeWeaponsByFlag, dogmaLocation)
    totalDps = turretDps + missileDps + aoeDps + dotDps
    totalDpsWithReload = turretDpsWithReload + missileDpsWithReload + aoeDps + dotDps
    dpsInfo = KeyVal(turretDps=turretDps, turretDpsWithReload=turretDpsWithReload, missileDps=missileDps, missileDpsWithReload=missileDpsWithReload, aoeDps=aoeDps, totalDps=totalDps, totalDpsWithReload=totalDpsWithReload, dotDps=dotDps)
    return dpsInfo


def GetChanceToHit(shipID, dogmaLocation):
    chargesByFlag, launchersByFlag, turretsByFlag, aoeWeaponsByFlag, dotLaunchersByFlag = GetFittedItemsByFlag(dogmaLocation)
    trackingSpeed = falloff = maxRange = optimalSig = 0
    numTurrets = len(turretsByFlag)
    for turret in turretsByFlag.itervalues():
        trackingSpeed += dogmaLocation.GetAttributeValue(turret, const.attributeTrackingSpeed)
        falloff += dogmaLocation.GetAttributeValue(turret, const.attributeFalloff)
        maxRange += dogmaLocation.GetAttributeValue(turret, const.attributeMaxRange)
        optimalSig += dogmaLocation.GetAttributeValue(turret, const.attributeOptimalSigRadius)

    trackingSpeed /= numTurrets
    falloff /= numTurrets
    maxRange /= numTurrets
    optimalSig /= numTurrets
    return (trackingSpeed,
     falloff,
     maxRange,
     optimalSig)


def GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV):
    damagePerShot = _GetLauncherDamagePerShot(dogmaLocation, chargeKey, itemID, ownerID, GAV)
    duration = GAV(itemID, const.attributeRateOfFire)
    missileDps = damagePerShot / duration
    missileDpsWithReload = _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration)
    return (missileDps * 1000, missileDpsWithReload * 1000)


def _GetLauncherDamagePerShot(dogmaLocation, chargeKey, moduleID, ownerID, GAV):
    if chargeKey is None:
        return 0
    damageMultiplier = GetMissleDamageMultiplier(dogmaLocation, moduleID, ownerID, GAV)
    damage = GetDamageFromItem(dogmaLocation, chargeKey)
    damagePerShot = damage * damageMultiplier
    return damagePerShot


def GetMissleDamageMultiplier(dogmaLocation, moduleID, ownerID, GAV):
    dogmaItem = dogmaLocation.SafeGetDogmaItem(moduleID)
    if dogmaItem and dogmaItem.groupID == const.groupMissileLauncherBomb:
        damageMultiplier = 1
    else:
        damageMultiplier = GAV(ownerID, const.attributeMissileDamageMultiplier)
    return damageMultiplier


def GetTurretDps(dogmaLocation, chargeKey, itemID, GAV, *args):
    turretDps = 0.0
    turretDpsWithReload = 0.0
    damagePerShot = _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV)
    if abs(damagePerShot) > 0:
        duration = GAV(itemID, const.attributeRateOfFire)
        if abs(duration) > 0:
            turretDps = damagePerShot / duration
            turretDpsWithReload = _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration)
    return (turretDps * 1000, turretDpsWithReload * 1000)


def _GetTurretDamagePerShot(dogmaLocation, chargeKey, itemID, GAV):
    if chargeKey is not None:
        damage = GetDamageFromItem(dogmaLocation, chargeKey)
    else:
        damage = GetDamageFromItem(dogmaLocation, itemID)
    if damage > 0:
        damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
        damage *= damageMultiplier
    return damage


def _GetDpsWithReload(chargeKey, itemID, GAV, damagePerShot, duration):
    if chargeKey is None:
        return damagePerShot / duration
    reloadTime = GAV(itemID, const.attributeReloadTime)
    reactivationDelay = GAV(itemID, const.attributeModuleReactivationDelay)
    numShotBeforeReload = GetNumChargesFullyLoaded(chargeKey, itemID, GAV)
    if reactivationDelay > reloadTime:
        missileDpsWithReload = damagePerShot / (reactivationDelay + duration)
        return missileDpsWithReload
    if numShotBeforeReload:
        missileDpsWithReload = numShotBeforeReload * damagePerShot / (numShotBeforeReload * duration + reloadTime)
        return missileDpsWithReload
    return 0


def GetDotDps(chargeKey, itemID, GAV, *args):
    if chargeKey is None:
        return 0
    dotMaxDamagePerTick = GAV(chargeKey, const.attributeDotMaxDamagePerTick)
    damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
    return dotMaxDamagePerTick * damageMultiplier


def GetNumChargesFullyLoaded(chargeKey, itemID, GAV):
    launcherCapacity = GAV(itemID, const.attributeCapacity)
    chargeVolume = GAV(chargeKey, const.attributeVolume)
    if chargeVolume:
        numShotBeforeReload = int(launcherCapacity / float(chargeVolume))
        return numShotBeforeReload
    else:
        return 0


def GetDamageFromItem(dogmaLocation, itemID):
    accDamage = 0
    for attributeID in DAMAGE_ATTRIBUTES:
        d = dogmaLocation.GetAccurateAttributeValue(itemID, attributeID)
        accDamage += d

    return accDamage


def CapacitorSimulator(dogmaLocation, shipID):
    dogmaItem = dogmaLocation.dogmaItems[shipID]
    capacitorCapacity = dogmaLocation.GetAccurateAttributeValue(shipID, const.attributeCapacitorCapacity)
    rechargeTime = dogmaLocation.GetAccurateAttributeValue(shipID, const.attributeRechargeRate)
    modules = []
    totalCapNeed = 0
    modulesByFlag = {}
    chargesByFlag = {}
    for moduleID, module in dogmaItem.GetFittedItems().iteritems():
        if module.categoryID == const.categoryCharge:
            chargesByFlag[module.flagID] = module
        else:
            modulesByFlag[module.flagID] = module

    for flagID, module in modulesByFlag.iteritems():
        moduleID = module.itemID
        if not dogmaLocation.IsModuleIncludedInCalculation(module):
            continue
        try:
            defaultEffectID = dogmaLocation.dogmaStaticMgr.GetDefaultEffect(module.typeID)
        except KeyError:
            defaultEffectID = None

        if defaultEffectID is None:
            continue
        defaultEffect = dogmaLocation.dogmaStaticMgr.effects[defaultEffectID]
        durationAttributeID = defaultEffect.durationAttributeID
        dischargeAttributeID = defaultEffect.dischargeAttributeID
        if durationAttributeID is None:
            continue
        duration = dogmaLocation.GetAccurateAttributeValue(moduleID, durationAttributeID)
        reactivationDelay = dogmaLocation.GetAccurateAttributeValue(moduleID, const.attributeModuleReactivationDelay)
        reloadInfo = None
        moduleGroupID = evetypes.GetGroupID(module.typeID)
        if moduleGroupID == const.groupCapacitorBooster:
            charges = chargesByFlag.get(flagID, None)
            if not charges:
                continue
            avgCapInjectedEachCycle, capInjectedPerCycle, reloadInfo = _GetAvgInjectedEachCycle(dogmaLocation, moduleID, charges, duration)
            avgCapNeed = -avgCapInjectedEachCycle
            capNeed = -capInjectedPerCycle
        elif moduleGroupID == const.groupEnergyVampire:
            capInjectedPerCycle = dogmaLocation.GetAccurateAttributeValue(moduleID, const.attributePowerTransferAmount)
            capNeed = -capInjectedPerCycle
            avgCapNeed = -capInjectedPerCycle
        elif dischargeAttributeID is None:
            continue
        else:
            avgCapNeed = capNeed = dogmaLocation.GetAccurateAttributeValue(moduleID, dischargeAttributeID)
        k = KeyVal(capNeeded=capNeed, durationValue=long(duration * const.dgmTauConstant), nextRun=0, cyclesSinceReload=0, reloadInfo=reloadInfo, reactivationDelay=reactivationDelay)
        modules.append(k)
        totalCapNeed += avgCapNeed / (duration + reactivationDelay)

    rechargeRateAverage = capacitorCapacity / rechargeTime
    peakRechargeRate = 2.5 * rechargeRateAverage
    tau = rechargeTime / 5
    totalPositiveCapNeeded = max(0, totalCapNeed)
    TTL = None
    runSimulation = totalCapNeed > peakRechargeRate
    if runSimulation or totalCapNeed / peakRechargeRate > 0.95:
        TTL = RunSimulation(capacitorCapacity, rechargeTime, modules)
        if TTL >= CAP_STABLE_TIME:
            TTL = None
    if TTL is not None:
        loadBalance = 0
    else:
        c = 2 * capacitorCapacity / tau
        k = totalPositiveCapNeeded / c
        fourK = min(1, 4 * k)
        exponent = (1 - sqrt(1 - fourK)) / 2
        if exponent == 0:
            loadBalance = 1
        else:
            t = -log(exponent) * tau
            loadBalance = (1 - exp(-t / tau)) ** 2
    return (peakRechargeRate,
     totalCapNeed,
     loadBalance,
     TTL)


def _GetReloadInfo(dogmaLocation, moduleID, charges):
    GAV = dogmaLocation.GetAccurateAttributeValue
    reloadTime = GAV(moduleID, const.attributeReloadTime)
    moduleCapacity = GAV(moduleID, const.attributeCapacity)
    chargeVolume = GAV(charges.itemID, const.attributeVolume)
    maxChargesInModule = int(moduleCapacity / float(chargeVolume))
    moduleRechargeInfo = KeyVal(reloadTime=reloadTime, maxChargesInModule=maxChargesInModule)
    return moduleRechargeInfo


def _GetAvgInjectedEachCycle(dogmaLocation, moduleID, charges, duration):
    moduleRechargeInfo = _GetReloadInfo(dogmaLocation, moduleID, charges)
    capInjectedPerCycle = dogmaLocation.GetAccurateAttributeValue(charges.itemID, const.attributeCapacitorBonus)
    injectedInOneLoad = moduleRechargeInfo.maxChargesInModule * capInjectedPerCycle
    durationOfFullLoad = moduleRechargeInfo.maxChargesInModule * duration
    avgCapInjectedEachCycle = injectedInOneLoad / (durationOfFullLoad + moduleRechargeInfo.reloadTime) * duration
    return (avgCapInjectedEachCycle, capInjectedPerCycle, moduleRechargeInfo)


def RunSimulation(capacitorCapacity, rechargeRate, modules):
    capacitor = capacitorCapacity
    tauThingy = float(const.dgmTauConstant) * (rechargeRate / 5.0)
    currentTime = nextTime = 0L
    while capacitor > 0.0 and nextTime < CAP_STABLE_TIME:
        capacitor = (1.0 + (math.sqrt(capacitor / capacitorCapacity) - 1.0) * math.exp((currentTime - nextTime) / tauThingy)) ** 2 * capacitorCapacity
        currentTime = nextTime
        nextTime = CAP_STABLE_TIME
        for data in modules:
            if data.nextRun == currentTime:
                capacitor -= data.capNeeded
                data.cyclesSinceReload += 1
                if data.reloadInfo:
                    if data.cyclesSinceReload >= data.reloadInfo.maxChargesInModule:
                        data.nextRun += data.reloadInfo.reloadTime * const.SEC
                        data.cyclesSinceReload = 0
                if data.reactivationDelay:
                    data.nextRun += data.reactivationDelay * const.SEC
                data.nextRun += data.durationValue
            nextTime = min(nextTime, data.nextRun)

    if capacitor > 0.0:
        return CAP_STABLE_TIME
    return currentTime


LN_025 = math.log(0.25)

def GetAlignTime(dogmaLocation):
    shipID = dogmaLocation.GetCurrentShipID()
    agility = dogmaLocation.GetAttributeValue(shipID, const.attributeAgility)
    mass = dogmaLocation.GetAttributeValue(shipID, const.attributeMass)
    return GetAlignTimeFromAgilityAndMass(agility, mass)


def GetAlignTimeFromAgilityAndMass(agility, mass):
    alignTime = -LN_025 * agility * mass / 1000000
    return alignTime


def GetFuelUsage(dogmaLocation):
    totalFuelPerHour = GetFuelUsagePerHour(dogmaLocation)
    return totalFuelPerHour * 24


def GetFuelUsagePerHour(dogmaLocation):
    ship = dogmaLocation.GetShip()
    totalFuelPerHour = 0
    for itemID, dogmaItem in ship.GetFittedItems().iteritems():
        fuelPerHour = dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeServiceModuleFuelAmount)
        if fuelPerHour and dogmaItem.IsOnline():
            totalFuelPerHour += fuelPerHour

    return totalFuelPerHour


def GetFighterDamage(dogmaLocation):
    totalDmgFromFighters = 0
    dpsByPrimaryAbilityID = defaultdict(int)
    dpsBySecondaryAbilityID = defaultdict(int)
    dpsByTubeID = defaultdict(int)
    for eachTubeFlagID in const.fighterTubeFlags:
        fighterBelongingToTube = dogmaLocation.GetFightersForTube(eachTubeFlagID)
        if fighterBelongingToTube is None:
            continue
        fighterID = fighterBelongingToTube.itemID
        qty = fighterBelongingToTube.squadronSize
        primaryDmg, primaryDps, primaryAbilityID = GetPrimaryDamageForSquadron(dogmaLocation, fighterID, fighterBelongingToTube.typeID, qty)
        secondaryDmg, secondaryDps, secondaryAbilityID = GetSecondaryForSquadron(dogmaLocation, fighterID, fighterBelongingToTube.typeID, qty)
        totalDmgFromFighters += primaryDmg + secondaryDmg
        dpsByPrimaryAbilityID[primaryAbilityID] += primaryDps
        if secondaryDps and secondaryAbilityID is not None:
            dpsBySecondaryAbilityID[secondaryAbilityID] += secondaryDps
        dpsByTubeID[eachTubeFlagID] += primaryDps + secondaryDps

    return (totalDmgFromFighters,
     dpsByTubeID,
     dpsByPrimaryAbilityID,
     dpsBySecondaryAbilityID)


def GetPrimaryDamageForSquadron(dogmaLocation, fighterID, typeID, qty):
    dps, squadronDmg, abilityID = GetDamageForAbilitySlot(dogmaLocation, fighterID, typeID, qty, abilitySlotID=ABILITY_SLOT_0)
    return (squadronDmg, dps, abilityID)


def GetSecondaryForSquadron(dogmaLocation, fighterID, typeID, qty):
    dps, squadronDmg, abilityID = GetDamageForAbilitySlot(dogmaLocation, fighterID, typeID, qty, abilitySlotID=ABILITY_SLOT_2)
    return (squadronDmg, dps, abilityID)


def GetDamageForAbilitySlot(dogmaLocation, fighterID, typeID, qty, abilitySlotID):
    squadronDmg = 0
    dps = 0
    abilityID = GetAbilityIDForSlot(typeID, abilitySlotID)
    if abilityID:
        squadronDmg, dps = GetDamageForSquadron(dogmaLocation, fighterID, qty, abilityID)
    return (dps, squadronDmg, abilityID)


def GetDamageForSquadron(dogmaLocation, fighterID, qty, abilityID):
    dItem = dogmaLocation.SafeGetDogmaItem(fighterID)
    if dItem is None:
        return (0, 0)
    dmg, dps = GetDamageFromFighter(dogmaLocation, dItem.itemID, abilityID)
    totalDmg = qty * dmg
    totalDps = qty * dps
    return (totalDmg, totalDps)


def GetDamageFromFighter(dogmaLocation, itemID, abilityID):
    damageMultiplierAttributeID = GetDamageMultiplierAttributeFromAbilityID(abilityID)
    if damageMultiplierAttributeID is None:
        return (0, 0)
    multiplier = dogmaLocation.GetAccurateAttributeValue(itemID, damageMultiplierAttributeID)
    accDamage = 0
    abilityAttributeIDs = GetDogmaAttributeIDsForAbilityID(abilityID)
    durationAttributeID = GetAbilityDurationAttributeID(dogmaLocation.dogmaStaticMgr, abilityID)
    for attributeID in abilityAttributeIDs:
        if attributeID not in FIGHTER_DAMAGE_ATTRIBUTES:
            if attributeID in DURATION_ATTRIBUTES:
                durationAttributeID = attributeID
            continue
        d = dogmaLocation.GetAccurateAttributeValue(itemID, attributeID)
        accDamage += d * multiplier

    dps = 0
    if durationAttributeID:
        duration = dogmaLocation.GetAccurateAttributeValue(itemID, durationAttributeID)
        if duration:
            dps = accDamage / duration
    return (accDamage, dps * 1000)


def GetRangesForAbilitySlot(dogmaLocation, fighterID, typeID, abilitySlotID):
    maxRange = None
    falloffDist = None
    abilityID = GetAbilityIDForSlot(typeID, abilitySlotID)
    if abilityID:
        rangeAttributeID, falloffAttributeID = GetAbilityRangeAndFalloffAttributeIDs(dogmaLocation.dogmaStaticMgr, abilityID)
        if rangeAttributeID:
            maxRange = dogmaLocation.GetAccurateAttributeValue(fighterID, rangeAttributeID)
        if falloffAttributeID:
            falloffDist = dogmaLocation.GetAccurateAttributeValue(fighterID, falloffAttributeID)
    return (maxRange, falloffDist, abilityID)


def AddDogmaOwnerModifiers(fittingDogmaLocation, fighterID):
    fighterDogmaItem = fittingDogmaLocation.SafeGetDogmaItem(fighterID)
    if fighterDogmaItem is not None:
        fighterDogmaItem.AddFighterControllerOwnerModifiers()


def GetFullAndPartialSquadrons(dogmaLocation):
    full = 0
    partial = 0
    for flagID in const.fighterTubeFlags:
        dogmaItem = dogmaLocation.GetFightersForTube(flagID)
        if dogmaItem:
            squadronSize = dogmaItem.squadronSize
            if not squadronSize:
                continue
            maxInSquadron = GetMaxSquadronSize(dogmaItem.typeID)
            if squadronSize < maxInSquadron:
                partial += 1
            else:
                full += 1

    return (full, partial)


def GetHardware(dogmaLocation):
    shipDogmaItem = dogmaLocation.GetShipItem()
    if not shipDogmaItem:
        return []
    hardwareDict = {}
    for module in shipDogmaItem.GetFittedItems().itervalues():
        typeID = module.typeID
        if IsCharge(typeID):
            continue
        flagID = module.flagID
        flagInHardware = hardwareDict.get(typeID, None)
        if flagInHardware:
            flagID = min(flagInHardware, flagID)
        hardwareDict[typeID] = flagID

    hardwareList = [ (flagID, typeID) for typeID, flagID in hardwareDict.iteritems() ]
    lst = sorted(hardwareList, key=lambda data: data[0])
    return [ x[1] for x in lst ]


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) == const.categoryCharge
