#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveDrones\droneDamageTracker.py
from eveDrones.droneConst import DAMAGESTATE_NOT_READY
from eveexceptions.exceptionEater import ExceptionEater
from inventorycommon.const import flagDroneBay, flagNone
import uthread2
import blue

class InBayDroneDamageTracker(object):
    __notifyevents__ = ['OnItemChange',
     'OnRepairDone',
     'OnDamageStateChange',
     'OnDroneControlLost']

    def __init__(self, dogmaLM, clientDogmaLM):
        self.droneDamageStatesByDroneIDs = {}
        sm.RegisterNotify(self)
        self.fetchingInfoForDrones = set()
        self.clearTimestamp = None
        self.SetDogmaLM(dogmaLM)
        self.clientDogmaLM = clientDogmaLM

    def SetDogmaLM(self, dogmaLM):
        self.dogmaLM = dogmaLM

    def FetchInBayDroneDamageToServer(self, droneIDs):
        droneIDsMissingDamage = self.FindDronesMissingDamageState(droneIDs)
        if not droneIDsMissingDamage:
            return
        self.fetchingInfoForDrones.update(droneIDsMissingDamage)
        callMadeTime = blue.os.GetSimTime()
        damageStateAndInfoForDrones = {}
        damagesForDrones = self.dogmaLM.GetLayerDamageValuesByItems(droneIDsMissingDamage)
        for droneID, droneDamage in damagesForDrones.iteritems():
            maxHull = self.clientDogmaLM.dogmaItems[droneID].attributes[const.attributeHp].GetValue()
            maxArmor = self.clientDogmaLM.dogmaItems[droneID].attributes[const.attributeArmorHP].GetValue()
            damageStateAndInfoForDrones[droneID] = [droneDamage.shieldInfo,
             1.0 - droneDamage.armorDamage / maxArmor,
             1.0 - droneDamage.hullDamage / maxHull,
             const.flagDroneBay]

        if not self.HasDictBeenClearedAfterCall(callMadeTime):
            damageStateDict = ConvertDroneStateToCorrectFormat(damageStateAndInfoForDrones)
            self.droneDamageStatesByDroneIDs.update(damageStateDict)
        self.fetchingInfoForDrones.difference_update(droneIDsMissingDamage)

    def FindDronesMissingDamageState(self, droneIDs):
        droneIDsMissingDamage = {x for x in droneIDs if x not in self.droneDamageStatesByDroneIDs}
        return droneIDsMissingDamage - self.fetchingInfoForDrones

    def HasDictBeenClearedAfterCall(self, callMadeTime):
        if self.clearTimestamp and self.clearTimestamp > callMadeTime:
            return True
        else:
            return False

    def GetDamageStateForDrone(self, droneID):
        if self.IsDroneDamageReady(droneID):
            return self.droneDamageStatesByDroneIDs.get(droneID, None)
        droneIDsMissingDamage = self.FindDronesMissingDamageState([droneID])
        if droneIDsMissingDamage:
            uthread2.StartTasklet(self.FetchInBayDroneDamageToServer, droneIDsMissingDamage)
        return DAMAGESTATE_NOT_READY

    def IsDroneDamageReady(self, droneID):
        return droneID in self.droneDamageStatesByDroneIDs

    def OnItemChange(self, item, *args):
        droneDamageState = self.droneDamageStatesByDroneIDs.get(item.itemID, None)
        if droneDamageState is None:
            return
        if item.flagID not in (flagDroneBay, flagNone):
            del self.droneDamageStatesByDroneIDs[item.itemID]
        else:
            droneDamageState.UpdateFlagID(item.flagID)

    def OnDroneControlLost(self, droneID):
        self.droneDamageStatesByDroneIDs.pop(droneID, None)

    def OnRepairDone(self, itemIDs, *args):
        for itemID in itemIDs:
            self.droneDamageStatesByDroneIDs.pop(itemID, None)

    def OnDamageStateChange(self, itemID, damageState):
        droneDamageInfo = self.droneDamageStatesByDroneIDs.get(itemID, None)
        if droneDamageInfo is None:
            return
        timestamp = blue.os.GetSimTime()
        droneDamageInfo.UpdateInfo(timestamp, damageState)


def ConvertDroneStateToCorrectFormat(damageStateForDrones):
    newDroneDamageDict = {}
    for itemID, ds in damageStateForDrones.iteritems():
        if ds is None:
            continue
        shieldInfo, armorHealth, hullHealth, flagID = ds
        shieldHealth = shieldInfo[0]
        shieldTau = shieldInfo[1]
        timestamp = shieldInfo[2]
        d = DroneDamageObject(itemID, shieldTau, timestamp, shieldHealth, armorHealth, hullHealth, flagID)
        newDroneDamageDict[itemID] = d

    return newDroneDamageDict


class DroneDamageObject:

    def __init__(self, itemID, shieldTau, timestamp, shieldHealth, armorHealth, hullHealth, flagID):
        self.itemID = itemID
        self.shieldTau = shieldTau
        self.timestamp = timestamp
        self.shieldHealth = shieldHealth
        self.armorHealth = armorHealth
        self.hullHealth = hullHealth
        self.flagID = flagID

    def UpdateInfo(self, timestamp, damageValues):
        self.UpdateShieldHealth(damageValues[0], timestamp)
        self.UpdateArmorHealth(damageValues[1])
        self.UpdateHullHealth(damageValues[2])

    def GetInfoInMichelleFormat(self):
        return [(self.shieldHealth, self.shieldTau, self.timestamp), self.armorHealth, self.hullHealth]

    def UpdateShieldHealth(self, shieldInfo, timestamp):
        if isinstance(shieldInfo, tuple):
            self.shieldHealth = shieldInfo[0]
        else:
            self.shieldHealth = shieldInfo
        self.timestamp = timestamp

    def UpdateArmorHealth(self, value):
        self.armorHealth = value

    def UpdateHullHealth(self, value):
        self.hullHealth = value

    def UpdateFlagID(self, flagID):
        self.flagID = flagID
