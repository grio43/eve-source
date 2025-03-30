#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\droneUtil.py
from collections import defaultdict
from localization import GetByLabel
from shipfitting.fittingDogmaLocationUtil import GetDamageFromItem

def GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones):
    droneInfo = {}
    for droneID, qty in activeDrones.iteritems():
        damage = GetDamageFromItem(dogmaLocation, droneID)
        if damage == 0:
            continue
        damage *= qty
        damageMultiplier = dogmaLocation.GetAccurateAttributeValue(droneID, const.attributeDamageMultiplier)
        if damageMultiplier == 0:
            continue
        duration = dogmaLocation.GetAccurateAttributeValue(droneID, const.attributeRateOfFire)
        droneDps = damage * damageMultiplier / duration
        droneBandwidth = dogmaLocation.GetAccurateAttributeValue(droneID, const.attributeDroneBandwidthUsed)
        droneBandwidth *= qty
        droneDogmaItem = dogmaLocation.dogmaItems[droneID]
        droneInfo[droneID] = (droneDogmaItem.typeID, droneBandwidth, droneDps)

    return droneInfo


def GetSimpleGetDroneDamageOutput(drones, bwLeft, dronesLeft):
    totalDps = 0
    for droneID, droneInfo in drones.iteritems():
        typeID, bwNeeded, dps = droneInfo
        qty = 1
        noOfDrones = min(int(bwLeft) / int(bwNeeded), qty, dronesLeft)
        if noOfDrones == 0:
            break
        totalDps += qty * dps
        dronesLeft -= qty
        bwLeft -= qty * bwNeeded

    return totalDps


def GetDroneDps(shipID, dogmaLocation):
    activeDrones = dogmaLocation.GetActiveDrones()
    return GetOptimalDroneDamage(shipID, dogmaLocation, activeDrones)


def GetOptimalDroneDamage(shipID, dogmaLocation, activeDrones):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    droneInfo = GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones)
    dogmaLocation.LogInfo('Gathered drone info and found', len(droneInfo), 'types of drones')
    bandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    maxDrones = dogmaLocation.GetMaxActiveDrones()
    dps = GetSimpleGetDroneDamageOutput(droneInfo, bandwidth, maxDrones)
    return (dps * 1000, {})


def GetDroneRanges(shipID, dogmaLocation, activeDrones):
    maxRangeOfAll = 0
    minRangeOfAll = 0
    for droneID in activeDrones:
        maxRange = dogmaLocation.GetAttributeValue(droneID, const.attributeMaxRange)
        maxRangeOfAll = max(maxRangeOfAll, maxRange)
        if not minRangeOfAll:
            minRangeOfAll = maxRange
        else:
            minRangeOfAll = min(minRangeOfAll, maxRange)

    return (minRangeOfAll, maxRangeOfAll)


def GetDroneBandwidth(shipID, dogmaLocation, activeDrones):
    shipBandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    bandwidthUsed = 0
    for droneID, qty in activeDrones.iteritems():
        bandwidthUsed += qty * dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)

    return (bandwidthUsed, shipBandwidth)


class SelectedDroneTracker(object):

    def __init__(self):
        self.selectedDronesDict = defaultdict(int)

    def RegisterDroneAsActive(self, dogmaLocation, droneID, qty = 1, raiseError = True):
        numDronesSelected = sum(self.selectedDronesDict.itervalues())
        maxActive = dogmaLocation.GetMaxActiveDrones()
        if numDronesSelected >= max(maxActive, 5):
            if raiseError:
                raise UserError('CustomNotify', {'notify': GetByLabel('UI/Fitting/FittingWindow/ActiveDronesLimitWarning', limit=maxActive)})
            else:
                return
        shipID = dogmaLocation.GetCurrentShipID()
        bandwidthUsed, shipBandwith = GetDroneBandwidth(shipID, dogmaLocation, self.selectedDronesDict)
        droneBandwidth = qty * dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)
        if droneBandwidth + bandwidthUsed > shipBandwith:
            if raiseError:
                raise UserError('CustomNotify', {'notify': GetByLabel('UI/Fitting/FittingWindow/ActiveDroneBandwithWarning')})
            else:
                return
        self.selectedDronesDict[droneID] += qty

    def UnregisterDroneFromActive(self, droneID, qty = 1):
        if droneID in self.selectedDronesDict:
            self.selectedDronesDict[droneID] -= qty
            if self.selectedDronesDict[droneID] <= 0:
                self.selectedDronesDict.pop(droneID)

    def GetSelectedDrones(self):
        return self.selectedDronesDict.copy()

    def SetDroneActivityState(self, dogmaLocation, droneID, setActive, qty = 1):
        if setActive:
            self.RegisterDroneAsActive(dogmaLocation, droneID, qty=qty)
        else:
            self.UnregisterDroneFromActive(droneID, qty=qty)

    def Clear(self):
        self.selectedDronesDict.clear()
