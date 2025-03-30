#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\planetCommon.py
import math
import string
import blue.heapq as heapq
import dogma.data as dogma_data
import evetypes
import localization
from eve.common.lib import appConst as const
from eve.common.script.planet.surfacePoint import SurfacePoint
from inventorycommon.const import typePlanetShattered
from inventorycommon.const import typePlanetScorched
from utillib import KeyVal
LINK_MAX_UPGRADE = 10
LINK_UPGRADE_BASECOST = 0.1
NETWORK_UPDATE_DELAY = 5 * const.SEC
importExportThrottleTimer = 5 * const.SEC
MAX_WAYPOINTS = 5
PLANET_CACHE_TIMEOUT = 15 * const.MIN
RESOURCE_CACHE_TIMEOUT = 30 * const.MIN
ECU_MAX_HEADS = 10
RADIUS_DRILLAREAMAX = 0.05
RADIUS_DRILLAREAMIN = 0.01
RADIUS_DRILLAREADIFF = RADIUS_DRILLAREAMAX - RADIUS_DRILLAREAMIN

def GetCPUAndPowerForPinType(typeID):
    cpu = power = cpuOutput = powerOutput = 0
    for attribute in dogma_data.get_type_attributes(typeID):
        if attribute.attributeID == const.attributeCpuLoad:
            cpu = int(attribute.value)
        elif attribute.attributeID == const.attributePowerLoad:
            power = int(attribute.value)
        elif attribute.attributeID == const.attributeCpuOutput:
            cpuOutput = int(attribute.value)
        elif attribute.attributeID == const.attributePowerOutput:
            powerOutput = int(attribute.value)

    return KeyVal(cpuUsage=cpu, powerUsage=power, cpuOutput=cpuOutput, powerOutput=powerOutput)


def GetUsageParametersForLinkType(typeID):
    params = KeyVal(basePowerUsage=0, baseCpuUsage=0, powerUsagePerKm=0.0, cpuUsagePerKm=0.0, powerUsageLevelModifier=0.0, cpuUsageLevelModifier=0.0)
    for typeAttribute in dogma_data.get_type_attributes(typeID):
        if typeAttribute.attributeID == const.attributePowerLoad:
            params.basePowerUsage = int(typeAttribute.value)
        elif typeAttribute.attributeID == const.attributeCpuLoad:
            params.baseCpuUsage = int(typeAttribute.value)
        elif typeAttribute.attributeID == const.attributePowerLoadPerKm:
            params.powerUsagePerKm = float(typeAttribute.value)
        elif typeAttribute.attributeID == const.attributeCpuLoadPerKm:
            params.cpuUsagePerKm = float(typeAttribute.value)
        elif typeAttribute.attributeID == const.attributePowerLoadLevelModifier:
            params.powerUsageLevelModifier = float(typeAttribute.value)
        elif typeAttribute.attributeID == const.attributeCpuLoadLevelModifier:
            params.cpuUsageLevelModifier = float(typeAttribute.value)

    return params


def GetCpuUsageForLink(typeID, length, level, params = None):
    if params is None:
        params = GetUsageParametersForLinkType(typeID)
    return params.baseCpuUsage + int(math.ceil(params.cpuUsagePerKm * length / 1000.0 * float(level + 1.0) ** params.cpuUsageLevelModifier))


def GetPowerUsageForLink(typeID, length, level, params = None):
    if params is None:
        params = GetUsageParametersForLinkType(typeID)
    return params.basePowerUsage + int(math.ceil(params.powerUsagePerKm * length / 1000.0 * float(level + 1.0) ** params.powerUsageLevelModifier))


def GetDistanceBetweenPins(pinA, pinB, planetRadius):
    spA = SurfacePoint(radius=planetRadius, theta=pinA.longitude, phi=pinA.latitude)
    spB = SurfacePoint(radius=planetRadius, theta=pinB.longitude, phi=pinB.latitude)
    return spA.GetDistanceToOther(spB)


def GetCommodityTotalVolume(commodities):
    totalVolume = 0.0
    for typeID, quantity in commodities.iteritems():
        totalVolume += evetypes.GetVolume(typeID) * quantity

    return totalVolume


def GetExpeditedTransferTime(linkBandwidth, commodities):
    commodityVolume = GetCommodityTotalVolume(commodities)
    return long(math.ceil(max(5 * const.MIN, float(commodityVolume) / linkBandwidth * const.HOUR)))


def GetGenericPinName(typeID, itemID):
    if isinstance(itemID, tuple):
        return localization.GetByLabel('UI/PI/Common/PinNameNew', pinName=evetypes.GetName(typeID))
    else:
        return localization.GetByLabel('UI/PI/Common/PinNameAndID', pinName=evetypes.GetName(typeID), pinID=ItemIDToPinDesignator(itemID))


def ItemIDToPinDesignator(itemID):
    alnums = string.digits[1:] + string.ascii_uppercase
    hashNum = len(alnums) - 1
    ret = ''
    for i in xrange(0, 5):
        ret += alnums[itemID / hashNum ** i % hashNum]
        if i == 1:
            ret += '-'

    return ret


def GetBandwidth(commodityVolume, cycleTime):
    return commodityVolume * const.HOUR / float(cycleTime)


def GetRouteValidationInfo(sourcePin, destPin, commodity):
    if destPin.IsStorage():
        if sourcePin.IsStorage():
            return (False, localization.GetByLabel('UI/PI/Common/CannotRouteStorageToStorage'), None)
        else:
            return (True, '', sourcePin.GetCycleTime())
    elif destPin.IsProcessor():
        if commodity in destPin.GetConsumables():
            if sourcePin.IsStorage():
                cycleTime = destPin.GetCycleTime()
            else:
                cycleTime = sourcePin.GetCycleTime()
            return (True, '', cycleTime)
        else:
            return (False, localization.GetByLabel('UI/PI/Common/CommodityCannotBeUsed'), None)
    elif destPin.IsExtractor():
        return (False, localization.GetByLabel('UI/PI/Common/CannotRouteToExtractors'), None)


def CanPutTypeInCustomsOffice(typeID):
    groupID = evetypes.GetGroupID(typeID)
    categoryID = evetypes.GetCategoryID(typeID)
    if categoryID not in (const.categoryCommodity, const.categoryPlanetaryResources, const.categoryPlanetaryCommodities):
        return False
    if categoryID == const.categoryCommodity and groupID != const.groupGeneral:
        return False
    return True


commandCenterInfoPerLevel = {0: KeyVal(powerOutput=6000, cpuOutput=1675, upgradeCost=0),
 1: KeyVal(powerOutput=9000, cpuOutput=7057, upgradeCost=580000),
 2: KeyVal(powerOutput=12000, cpuOutput=12136, upgradeCost=1510000),
 3: KeyVal(powerOutput=15000, cpuOutput=17215, upgradeCost=2710000),
 4: KeyVal(powerOutput=17000, cpuOutput=21315, upgradeCost=4210000),
 5: KeyVal(powerOutput=19000, cpuOutput=25415, upgradeCost=6310000)}

def GetPowerOutput(level):
    return commandCenterInfoPerLevel[level].powerOutput


def GetCPUOutput(level):
    return commandCenterInfoPerLevel[level].cpuOutput


def GetMaxCommandUpgradeLevel():
    return max(commandCenterInfoPerLevel.keys())


def GetUpgradeCost(currentLevel, desiredLevel):
    return commandCenterInfoPerLevel[desiredLevel].upgradeCost - commandCenterInfoPerLevel[currentLevel].upgradeCost


def GetPinEntityType(typeID):
    if not evetypes.Exists(typeID):
        raise RuntimeError('Unable to locate inventory type object for type ID', typeID)
    from eve.common.script.planet.entities.storagePin import StoragePin
    from eve.common.script.planet.entities.ecuPin import EcuPin
    from eve.common.script.planet.entities.spaceportPin import SpaceportPin
    from eve.common.script.planet.entities.processPin import ProcessPin
    from eve.common.script.planet.entities.extractorPin import ExtractorPin
    from eve.common.script.planet.entities.commandPin import CommandPin
    groupID = evetypes.GetGroupID(typeID)
    if groupID == const.groupCommandPins:
        return CommandPin
    if groupID == const.groupExtractorPins:
        return ExtractorPin
    if groupID == const.groupProcessPins:
        return ProcessPin
    if groupID == const.groupSpaceportPins:
        return SpaceportPin
    if groupID == const.groupStoragePins:
        return StoragePin
    if groupID == const.groupExtractionControlUnitPins:
        return EcuPin


def GetProgramLengthFromHeadRadius(headRadius):
    return (headRadius - RADIUS_DRILLAREAMIN) / RADIUS_DRILLAREADIFF * 335 + 1


def GetCycleTimeFromProgramLength(programLength):
    return 0.25 * 2 ** max(0, math.floor(math.log(programLength / 25.0, 2)) + 1)


def IsPlanetTypeBlackListed(planetTypeID):
    if planetTypeID == typePlanetShattered:
        return True
    if planetTypeID == typePlanetScorched:
        return True
    return False


class priority_dict(dict):

    def __init__(self, *args, **kwargs):
        super(priority_dict, self).__init__(*args, **kwargs)
        self._rebuild_heap()

    def _rebuild_heap(self):
        self._heap = [ (v, k) for k, v in self.iteritems() ]
        heapq.heapify(self._heap)

    def smallest(self):
        heap = self._heap
        v, k = heap[0]
        while k not in self or self[k] != v:
            heapq.heappop(heap)
            v, k = heap[0]

        return k

    def pop_smallest(self):
        heap = self._heap
        v, k = heapq.heappop(heap)
        while k not in self or self[k] != v:
            v, k = heapq.heappop(heap)

        del self[k]
        return k

    def __setitem__(self, key, val):
        super(priority_dict, self).__setitem__(key, val)
        if len(self._heap) < 2 * len(self):
            heapq.heappush(self._heap, (val, key))
        else:
            self._rebuild_heap()

    def setdefault(self, key, val):
        if key not in self:
            self[key] = val
            return val
        return self[key]

    def update(self, *args, **kwargs):
        super(priority_dict, self).update(*args, **kwargs)
        self._rebuild_heap()

    def sorted_iter(self):
        while self:
            yield self.pop_smallest()
