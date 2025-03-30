#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\sovHub\hubUtil.py
from collections import defaultdict
import eveicon
import evetypes
import sovereignty.client.sovHub.hubConst as hubConst
from const import HOUR, MIN
from inventorycommon.const import typeColonyReagentLava, typeColonyReagentIce
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
import sovereignty.upgrades.const as upgradesConst
from sovereignty.workforce import workforceConst

def UpdateEffectiveStatesForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts):
    powerUsed = 0
    workforceUsed = 0
    fuelUsed = defaultdict(int)
    ret = {}
    for upgradeData in upgrades:
        if not upgradeData.isConfiguredOnline:
            upgradeData.lackingResources = []
            continue
        lackingPower = upgradeData.staticData.power + powerUsed > availablePower
        lackingWorkforce = upgradeData.staticData.workforce + workforceUsed > availableWorkforce
        lackingFuel = False
        lackingStartupCost = False
        fuelCost = 0
        fuelTypeID = upgradeData.staticData.fuel_type_id
        if fuelTypeID:
            currentlyUsed = fuelUsed.get(fuelTypeID, 0)
            totalAvailable = fuelAmounts.get(fuelTypeID, 0)
            if upgradeData.isNewUpgrade or upgradeData.wasPending or upgradeData.wasOffline:
                startupCost = upgradeData.staticData.startup_cost
                lackingStartupCost = startupCost + currentlyUsed > totalAvailable
                fuelCost += startupCost
            fuelCost += 1 if upgradeData.staticData.consumption_per_hour else 0
            lackingFuel = fuelCost + currentlyUsed > totalAvailable
        if not lackingPower and not lackingWorkforce and not lackingFuel:
            upgradeData.powerState = upgradesConst.POWER_STATE_ONLINE
            powerUsed += upgradeData.staticData.power
            workforceUsed += upgradeData.staticData.workforce
            if fuelCost:
                fuelUsed[fuelTypeID] += fuelCost
        lackingList = [ y for x, y in ((lackingStartupCost, hubConst.LACKING_REAGENT_STARTUP),
         (lackingFuel, hubConst.LACKING_REAGENTS),
         (lackingPower, hubConst.LACKING_POWER),
         (lackingWorkforce, hubConst.LACKING_WORKFORCE)) if x ]
        if lackingStartupCost:
            upgradeData.powerState = upgradesConst.POWER_STATE_PENDING
        elif lackingFuel:
            upgradeData.powerState = upgradesConst.POWER_STATE_LOW
        elif lackingPower or lackingWorkforce:
            upgradeData.powerState = upgradesConst.POWER_STATE_LOW
        else:
            upgradeData.powerState = upgradesConst.POWER_STATE_ONLINE
        upgradeData.lackingResources = lackingList

    return ret


def GetWorkforceForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts):
    UpdateEffectiveStatesForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts)
    workforce = 0
    for upgrade in upgrades:
        if upgrade.isPowerStateFunctional:
            workforce += upgrade.staticData.workforce

    return workforce


def GetPowerForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts):
    UpdateEffectiveStatesForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts)
    power = 0
    for upgrade in upgrades:
        if upgrade.isPowerStateFunctional:
            power += upgrade.staticData.power

    return power


def GetConsumptionPerHour(upgrades, reagentTypeID, availablePower, availableWorkforce, fuelAmounts):
    UpdateEffectiveStatesForUpgrades(upgrades, availablePower, availableWorkforce, fuelAmounts)
    consumptionPerHour = 0
    for upgrade in upgrades:
        if upgrade.staticData.fuel_type_id != reagentTypeID:
            continue
        if upgrade.isPowerStateFunctional:
            consumptionPerHour += upgrade.staticData.consumption_per_hour

    return consumptionPerHour


def GetStartupCost(currentUpgrades, previousUpgrades, reagentTypeID, availablePower, availableWorkforce, fuelAmounts, includePending = True):
    UpdateEffectiveStatesForUpgrades(currentUpgrades, availablePower, availableWorkforce, fuelAmounts)
    return GetStartupCostForUpgrades(currentUpgrades, previousUpgrades, reagentTypeID, includePending)


def GetStartupCostForUpgrades(currentUpgrades, previousUpgrades, reagentTypeID, includePending = True):
    previousUpgradeStates = {x.upgrade_type_id:x.power_state for x in previousUpgrades}
    startupCost = 0
    for cUpgrade in currentUpgrades:
        if cUpgrade.staticData.fuel_type_id != reagentTypeID:
            continue
        if cUpgrade.powerState == upgradesConst.POWER_STATE_OFFLINE:
            continue
        if not includePending and cUpgrade.powerState == upgradesConst.POWER_STATE_PENDING:
            continue
        pState = previousUpgradeStates.get(cUpgrade.typeID, upgradesConst.POWER_STATE_OFFLINE)
        if pState in (upgradesConst.POWER_STATE_OFFLINE, upgradesConst.POWER_STATE_PENDING):
            startupCost += cUpgrade.staticData.startup_cost

    return startupCost


def GetStartupCostForPendingUpgrades(currentUpgrades, reagentTypeID):
    startupCost = 0
    for cUpgrade in currentUpgrades:
        if cUpgrade.staticData.fuel_type_id != reagentTypeID:
            continue
        if cUpgrade.powerState != upgradesConst.POWER_STATE_PENDING:
            continue
        startupCost += cUpgrade.staticData.startup_cost

    return startupCost


def GetHoursLeft(currentUpgrades, previousUpgrades, reagentTypeID, availablePower, availableWorkforce, fuelAmounts):
    startupCost = GetStartupCost(currentUpgrades, previousUpgrades, reagentTypeID, availablePower, availableWorkforce, fuelAmounts, includePending=False)
    amountInHub = fuelAmounts.get(reagentTypeID, 0)
    amountLeft = max(0, amountInHub - startupCost)
    perHour = GetConsumptionPerHour(currentUpgrades, reagentTypeID, availablePower, availableWorkforce, fuelAmounts)
    if not perHour:
        return
    numHours = float(amountLeft) / perHour
    return numHours


HOURS_IN_1_WEEK = 168
HOURS_IN_4_WEEKS = HOURS_IN_1_WEEK * 4

def GetTimeLeftTextForTypeID(hoursLeft):
    if hoursLeft is None:
        return '-'
    elif hoursLeft > 2 * HOURS_IN_1_WEEK:
        numWeeks = int(hoursLeft / HOURS_IN_1_WEEK)
        return GetByLabel('UI/Sovereignty/SovHub/HubWnd/NumWeeksShort', numWeeks=numWeeks)
    numHoursBlue = int(hoursLeft * HOUR)
    if hoursLeft > HOURS_IN_1_WEEK:
        return FormatTimeIntervalShortWritten(numHoursBlue, showFrom='day', showTo='day')
    elif hoursLeft > 24:
        return FormatTimeIntervalShortWritten(numHoursBlue, showFrom='hour', showTo='hour')
    elif numHoursBlue < 10 * MIN:
        return FormatTimeIntervalShortWritten(numHoursBlue, showFrom='hour', showTo='second')
    else:
        return FormatTimeIntervalShortWritten(numHoursBlue, showFrom='hour', showTo='minute')


def GetUpkeepCostForConfiguredOnline(upgradeDataList, reagentTypeID):
    totalPerHour = 0
    for upgrade in upgradeDataList:
        if upgrade.isConfiguredOnline and upgrade.staticData.fuel_type_id == reagentTypeID:
            totalPerHour += upgrade.staticData.consumption_per_hour

    return totalPerHour


def GetFuelStatus(upgradeList, reagentTypeID, fuelAmount):
    totalPerHour = GetUpkeepCostForConfiguredOnline(upgradeList, reagentTypeID)
    if not totalPerHour:
        return '-'
    numHoursLeft = fuelAmount / totalPerHour
    if numHoursLeft > HOURS_IN_4_WEEKS:
        return GetByLabel('UI/Sovereignty/HubPage/FuelFull')
    if numHoursLeft > HOURS_IN_1_WEEK:
        return GetByLabel('UI/Sovereignty/HubPage/FuelLow')
    return GetByLabel('UI/Sovereignty/HubPage/FuelCritical')


def GetHoursLeftProgress(numHoursLeft):
    if numHoursLeft is None:
        return
    if numHoursLeft > HOURS_IN_4_WEEKS:
        return 1.0
    return numHoursLeft / HOURS_IN_4_WEEKS


def GetColorForUpgrade(upgrade):
    from eve.client.script.ui import eveColor
    if upgrade.isPowerStateFunctional:
        return eveColor.TUNGSTEN_GREY
    if upgrade.isInRestrictedPowerState:
        return eveColor.DANGER_RED
    return eveColor.MATTE_BLACK


def GetTexturePathForWorkforceMode(mode):
    if mode == workforceConst.MODE_TRANSIT:
        return eveicon.arrow_right
    if mode == workforceConst.MODE_IMPORT:
        return eveicon.arrow_down
    if mode == workforceConst.MODE_EXPORT:
        return eveicon.arrow_up
    return eveicon.workforce


def GetPowerStateNameFromState(powerState):
    if powerState == upgradesConst.POWER_STATE_OFFLINE:
        return GetByLabel('UI/Common/Offline')
    if powerState == upgradesConst.POWER_STATE_ONLINE:
        return GetByLabel('UI/Common/Online')
    if powerState == upgradesConst.POWER_STATE_PENDING:
        return GetByLabel('UI/Sovereignty/SovHub/Upgrades/PendingPowerState')
    if powerState == upgradesConst.POWER_STATE_LOW:
        return GetByLabel('UI/Sovereignty/SovHub/Upgrades/LowPowerState')
    return GetByLabel('UI/Sovereignty/SovHub/Upgrades/UnknownPowerState')


def GetIconTexturePathForReagent(reagentTypeID):
    if reagentTypeID == typeColonyReagentLava:
        return eveicon.magmatic_gas
    if reagentTypeID == typeColonyReagentIce:
        return eveicon.superionic_ice


texturePathByTypeList = {evetypes.TYPE_LIST_SOVHUB_SERVICE_MODULE_UPGRADES: eveicon.strategic_upgrades,
 evetypes.TYPE_LIST_SOVHUB_MINING_SITE_UPGRADES: eveicon.mining,
 evetypes.TYPE_LIST_SOVHUB_COMBAT_SITE_UPGRADES: eveicon.military_upgrades}

def GetTexturePathForUpgradeTypeList(typeListID):
    return texturePathByTypeList.get(typeListID, '')


def GetTypeListTexturePathForType(typeID):
    for typeListID, texturePath in texturePathByTypeList.iteritems():
        if typeID in evetypes.GetTypeIDsByListID(typeListID):
            return texturePath
