#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\common\registry.py
from collections import defaultdict
from .aggregators import CreateAggregator
from .attribute import DynamicBuffAttribute
from ccpProfile import TimedFunction
from dbuff.storage import GetDbuffCollection
from dbuff.common.priorityQueue import BuffPriorityQueue
import gametime

class BuffRegistry(object):
    clientNotifier = None

    def __init__(self, modifierApplier, clientNotifier, dbuffEventLogger):
        self._modifierApplier = modifierApplier
        self.clientNotifier = clientNotifier
        self.dbuffEventLogger = dbuffEventLogger
        self._buffPriorityQueue = BuffPriorityQueue()
        self._dynamicBuffs = DynamicBuffStore()
        self._continuousBuffSourcesByItem = {}

    @TimedFunction('dbuff::BuffRegistry::ApplyBuffsToItems')
    def ApplyBuffsToItems(self, targetItemIDs, duration, collectionValues, sourceOwnerID = None):
        expiryTime = gametime.GetSimTime() + int(duration)
        for dbuffCollectionID, dbuffValue in collectionValues.iteritems():
            for targetItemID in targetItemIDs:
                dynamicBuff = self._GetDynamicBuffIfExists(targetItemID, dbuffCollectionID)
                if dynamicBuff is None:
                    self._InsertNewDynamicBuff(targetItemID, dbuffCollectionID, expiryTime, dbuffValue)
                else:
                    dynamicBuff.MergeNewTimedInput(expiryTime, dbuffValue)
                self.ScheduleClientUpdate(targetItemID)

        if sourceOwnerID and targetItemIDs:
            if self.dbuffEventLogger:
                self.dbuffEventLogger.LogDbuffApplied(sourceOwnerID, targetItemIDs, duration, collectionValues)

    @TimedFunction('dbuff::BuffRegistry::ApplyContinuousBuffsToItem')
    def ApplyContinuousBuffsToItem(self, itemID, collectionValues, sourceItemID = None, sourceOwnerID = None):
        for dbuffCollectionID, dbuffValue in collectionValues.iteritems():
            self._RegisterContinuousBuffAffectingItem(itemID, dbuffCollectionID, sourceItemID)
            dynamicBuff = self._GetDynamicBuffIfExists(itemID, dbuffCollectionID)
            if dynamicBuff is None:
                self._InsertNewDynamicBuff(itemID, dbuffCollectionID, None, dbuffValue)
            else:
                dynamicBuff.SetContinuousInput(dbuffValue)
            self.ScheduleClientUpdate(itemID)

        if sourceOwnerID:
            if self.dbuffEventLogger:
                self.dbuffEventLogger.LogContinuousDbuffApplied(sourceOwnerID, itemID, collectionValues)

    @TimedFunction('dbuff::BuffRegistry::ClearContinuousBuffsFromItem')
    def ClearContinuousBuffsFromItem(self, itemID, dbuffCollectionIDs, sourceItemID = None, sourceOwnerID = None):
        for dbuffCollectionID in dbuffCollectionIDs:
            dynamicBuff = self._GetDynamicBuffIfExists(itemID, dbuffCollectionID)
            if dynamicBuff is not None:
                if self._IsItemAffectedByContinuousBuff(itemID, dbuffCollectionID):
                    self._UnregisterContinuousBuffAffectingItem(itemID, dbuffCollectionID, sourceItemID)
                if not self._IsItemAffectedByContinuousBuff(itemID, dbuffCollectionID):
                    dynamicBuff.ClearContinuousInput()
            self.ScheduleClientUpdate(itemID)

        if sourceOwnerID:
            if self.dbuffEventLogger:
                self.dbuffEventLogger.LogContinuousDbuffCleared(sourceOwnerID, itemID, dbuffCollectionIDs)

    def RemoveBuffsFromItem(self, targetItemID):
        dynamicBuffsToRemove = self._dynamicBuffs.GetAllForTarget(targetItemID)
        if dynamicBuffsToRemove is not None:
            for dynamicBuff in dynamicBuffsToRemove:
                self._modifierApplier.RemoveFromDogmaItem(dynamicBuff)
                if dynamicBuff.GetNextExpiryTime() is not None:
                    self._buffPriorityQueue.Remove(dynamicBuff)

            self._dynamicBuffs.DeleteAllForTarget(targetItemID)
            self.ScheduleClientUpdate(targetItemID)

    @TimedFunction('dbuff::BuffRegistry::ProcessAllReadyBuffsInQueue')
    def ProcessAllReadyBuffsInQueue(self):
        now = gametime.GetSimTime()
        while self._ProcessNextReadyBuffInQueue(now):
            pass

    def _ProcessNextReadyBuffInQueue(self, now):
        nextBuff = self._buffPriorityQueue.PopNextReadyBuff(now)
        if nextBuff is None:
            return False
        nextBuff.RecalculateOutput(now)
        if nextBuff.IsExpired():
            self._Discard(nextBuff)
        self.ScheduleClientUpdate(nextBuff.targetItemID)
        return True

    def _InsertNewDynamicBuff(self, targetItemID, dbuffCollectionID, expiryTime, value):
        dynamicBuff = DynamicBuff(self._buffPriorityQueue, targetItemID, dbuffCollectionID, expiryTime, value)
        self._dynamicBuffs.Insert(targetItemID, dbuffCollectionID, dynamicBuff)
        self._modifierApplier.ApplyToDogmaItem(dynamicBuff)

    def _GetDynamicBuffIfExists(self, targetItemID, dbuffCollectionID):
        return self._dynamicBuffs.Get(targetItemID, dbuffCollectionID)

    def _Discard(self, dynamicBuff):
        self._modifierApplier.RemoveFromDogmaItem(dynamicBuff)
        self._dynamicBuffs.Delete(dynamicBuff.targetItemID, dynamicBuff.dbuffCollectionID)

    def ScheduleClientUpdate(self, itemID):
        if self.clientNotifier:
            self.clientNotifier.ScheduleClientUpdate(itemID)

    def GetDbuffStateForClient(self, itemID):
        buffs = self._dynamicBuffs.GetAllForTarget(itemID)
        if buffs:
            return [ buff.GetStateForClient() for buff in buffs ]

    def _RegisterContinuousBuffAffectingItem(self, itemID, dbuffCollectionID, sourceItemID):
        if sourceItemID is None:
            return
        if itemID not in self._continuousBuffSourcesByItem:
            self._continuousBuffSourcesByItem[itemID] = {}
        if dbuffCollectionID not in self._continuousBuffSourcesByItem[itemID]:
            self._continuousBuffSourcesByItem[itemID][dbuffCollectionID] = set()
        self._continuousBuffSourcesByItem[itemID][dbuffCollectionID].add(sourceItemID)

    def _IsItemAffectedByContinuousBuff(self, itemID, dbuffCollectionID):
        if itemID not in self._continuousBuffSourcesByItem:
            return False
        if dbuffCollectionID not in self._continuousBuffSourcesByItem[itemID]:
            return False
        return len(self._continuousBuffSourcesByItem[itemID][dbuffCollectionID]) > 0

    def _UnregisterContinuousBuffAffectingItem(self, itemID, dbuffCollectionID, sourceItemID):
        if sourceItemID is None:
            return
        self._continuousBuffSourcesByItem[itemID][dbuffCollectionID].discard(sourceItemID)
        if not self._IsItemAffectedByContinuousBuff(itemID, dbuffCollectionID):
            del self._continuousBuffSourcesByItem[itemID][dbuffCollectionID]
        if len(self._continuousBuffSourcesByItem[itemID]) == 0:
            del self._continuousBuffSourcesByItem[itemID]


class DynamicBuffStore(object):

    def __init__(self):
        self._itemBuffs = defaultdict(dict)

    def Insert(self, targetItemID, dbuffCollectionID, dynamicBuff):
        self._itemBuffs[targetItemID][dbuffCollectionID] = dynamicBuff

    def Get(self, targetItemID, dbuffCollectionID):
        buffsByCollectionID = self._itemBuffs.get(targetItemID)
        if buffsByCollectionID is not None:
            return buffsByCollectionID.get(dbuffCollectionID)

    def GetAllForTarget(self, targetItemID):
        buffsByCollectionID = self._itemBuffs.get(targetItemID)
        if buffsByCollectionID is not None:
            return buffsByCollectionID.values()

    def Delete(self, targetItemID, dbuffCollectionID):
        buffsByCollectionID = self._itemBuffs.get(targetItemID)
        if buffsByCollectionID is not None:
            del buffsByCollectionID[dbuffCollectionID]
            if len(buffsByCollectionID) == 0:
                del self._itemBuffs[targetItemID]

    def DeleteAllForTarget(self, targetItemID):
        self._itemBuffs.pop(targetItemID, None)


class DynamicBuff(object):
    buffPriorityQueue = None
    targetItemID = None
    dbuffCollectionID = None
    aggregator = None
    dynamicBuffAttribute = None

    def __init__(self, buffPriorityQueue, targetItemID, dbuffCollectionID, expiryTime, outputValue):
        self.buffPriorityQueue = buffPriorityQueue
        self.targetItemID = targetItemID
        self.dbuffCollectionID = dbuffCollectionID
        self.aggregator = CreateAggregator(dbuffCollectionID, expiryTime, outputValue)
        self.dynamicBuffAttribute = DynamicBuffAttribute(outputValue)
        self._UpdatePositionInPriorityQueue()

    @TimedFunction('dbuff::DynamicBuff::MergeNewTimedInput')
    def MergeNewTimedInput(self, expiryTime, value):
        self.aggregator.MergeNewTimedInput(expiryTime, value)
        self.dynamicBuffAttribute.SetOutputValue(self.aggregator.GetCurrentOutputValue())
        self._UpdatePositionInPriorityQueue()

    @TimedFunction('dbuff::DynamicBuff::SetContinuousInput')
    def SetContinuousInput(self, value):
        self.aggregator.SetContinuousInput(value)
        self.dynamicBuffAttribute.SetOutputValue(self.aggregator.GetCurrentOutputValue())
        self._UpdatePositionInPriorityQueue()

    @TimedFunction('dbuff::DynamicBuff::ClearContinuousInput')
    def ClearContinuousInput(self):
        self.aggregator.ClearContinuousInput()
        if self.aggregator.HasInputs():
            self.dynamicBuffAttribute.SetOutputValue(self.aggregator.GetCurrentOutputValue())
        self._UpdatePositionInPriorityQueue()

    @TimedFunction('dbuff::DynamicBuff::RecalculateOutput')
    def RecalculateOutput(self, now):
        self.aggregator.DiscardExpiredTimedInputs(now)
        if self.aggregator.HasInputs():
            self.dynamicBuffAttribute.SetOutputValue(self.aggregator.GetCurrentOutputValue())
            self._UpdatePositionInPriorityQueue()

    def IsExpired(self):
        return not self.aggregator.HasInputs()

    def GetNextExpiryTime(self):
        return self.aggregator.GetNextExpiryTime()

    def _UpdatePositionInPriorityQueue(self):
        expiryTime = self.GetNextExpiryTime()
        if expiryTime is not None:
            self.buffPriorityQueue.Add(self, expiryTime)

    def GetStateForClient(self):
        return (self.dbuffCollectionID, self.aggregator.GetStateForClient())


class ModifierApplier(object):

    def __init__(self, dogmaLM):
        self._AddM = dogmaLM.AddModifierWithSource
        self._AddLM = dogmaLM.AddLocationModifierWithSource
        self._AddLGM = dogmaLM.AddLocationGroupModifierWithSource
        self._AddLRSM = dogmaLM.AddLocationRequiredSkillModifierWithSource
        self._RemoveM = dogmaLM.RemoveModifierWithSource
        self._RemoveLM = dogmaLM.RemoveLocationModifierWithSource
        self._RemoveLGM = dogmaLM.RemoveLocationGroupModifierWithSource
        self._RemoveLRSM = dogmaLM.RemoveLocationRequiredSkillModifierWithSource
        self._IsItemLoaded = dogmaLM.IsItemLoaded
        self._IsItemUnloading = dogmaLM.IsItemUnloading

    @TimedFunction('dbuff::ModifierApplier::ApplyToDogmaItem')
    def ApplyToDogmaItem(self, dynamicBuff):
        targetItemID = dynamicBuff.targetItemID
        if not self._IsItemLoaded(targetItemID) or self._IsItemUnloading(targetItemID):
            return
        attribute = dynamicBuff.dynamicBuffAttribute
        dbuffCollection = GetDbuffCollection(dynamicBuff.dbuffCollectionID)
        operation = dbuffCollection.operation
        for itemMod in dbuffCollection.itemModifiers:
            self._AddM(operation, targetItemID, itemMod.dogmaAttributeID, attribute)

        for locationModifiers in dbuffCollection.locationModifiers:
            self._AddLM(operation, targetItemID, locationModifiers.dogmaAttributeID, attribute)

        for locationGroupModifier in dbuffCollection.locationGroupModifiers:
            self._AddLGM(operation, targetItemID, locationGroupModifier.groupID, locationGroupModifier.dogmaAttributeID, attribute)

        for locationRequiredSkillModifier in dbuffCollection.locationRequiredSkillModifiers:
            self._AddLRSM(operation, targetItemID, locationRequiredSkillModifier.skillID, locationRequiredSkillModifier.dogmaAttributeID, attribute)

    @TimedFunction('dbuff::ModifierApplier::RemoveFromDogmaItem')
    def RemoveFromDogmaItem(self, dynamicBuff):
        targetItemID = dynamicBuff.targetItemID
        if not self._IsItemLoaded(targetItemID):
            return
        attribute = dynamicBuff.dynamicBuffAttribute
        dbuffCollection = GetDbuffCollection(dynamicBuff.dbuffCollectionID)
        operation = dbuffCollection.operation
        for itemModifier in dbuffCollection.itemModifiers:
            self._RemoveM(operation, targetItemID, itemModifier.dogmaAttributeID, attribute)

        for locationModifiers in dbuffCollection.locationModifiers:
            self._RemoveLM(operation, targetItemID, locationModifiers.dogmaAttributeID, attribute)

        for locationGroupModifier in dbuffCollection.locationGroupModifiers:
            self._RemoveLGM(operation, targetItemID, locationGroupModifier.groupID, locationGroupModifier.dogmaAttributeID, attribute)

        for locationRequiredSkillModifier in dbuffCollection.locationRequiredSkillModifiers:
            self._RemoveLRSM(operation, targetItemID, locationRequiredSkillModifier.skillID, locationRequiredSkillModifier.dogmaAttributeID, attribute)
