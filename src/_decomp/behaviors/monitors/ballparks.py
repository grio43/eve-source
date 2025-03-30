#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\ballparks.py
import logging
import uthread2
from ballpark.messenger.const import MESSAGE_INVULNERABILITY_CANCELED, MESSAGE_ON_BUBBLE_PROXIMITY_ENTERED
from ballpark.messenger.const import MESSAGE_ON_BALLPARK_ITEM_DESTROY
from ballpark.messenger.const import MESSAGE_ON_ITEM_REMOVED_FROM_PARK, MESSAGE_ON_PROXIMITY
from behaviors import status
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.ballparks import is_ball_cloaked
from behaviors.utility.blackboards import update_blackboard_set_if_changed
from behaviors.utility.components import get_proximity_sensors, get_proximity_sensor
from ccpProfile import TimedFunction
from npcs.server.tags import get_behavior_sensor_tags
logger = logging.getLogger(__name__)
PROXIMITY_EVENT = 'DoBubbleProximity'

class BubbleChangedMonitor(Task):

    @TimedFunction('behaviors::monitors::ballparks::BubbleChangedMonitor::OnEnter')
    def OnEnter(self):
        self.bubbleId = self.GetBubbleId()
        self.GetServiceManager().RegisterForNotifyEvent(self, PROXIMITY_EVENT)
        self.context.ballpark.SetBubbleEvents(self.bubbleId, True)
        self.SetStatusToSuccess()

    def GetBubbleId(self):
        if getattr(self.attributes, 'bubbleIdAddress', None) is None:
            return self.context.myBall.newBubbleId
        else:
            return self.GetLastBlackboardValue(self.attributes.bubbleIdAddress)

    def CleanUp(self):
        if not self.IsInvalid():
            self.GetServiceManager().UnregisterForNotifyEvent(self, PROXIMITY_EVENT)
            self.context.ballpark.SetBubbleEvents(self.bubbleId, False)
            self.bubbleId = None
        self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::ballparks::BubbleChangedMonitor::DoBubbleProximity')
    def DoBubbleProximity(self, solarSystemId, bubbleId, ballId, isEntering):
        if self.IsInvalid():
            return
        if bubbleId == self.bubbleId:
            self.behaviorTree.RequestReset(requestedBy=self)

    def GetServiceManager(self):
        return sm


class BallEnteredOrLeftBubbleGroupMonitor(Task, GroupTaskMixin):

    @TimedFunction('behaviors::monitors::ballparks::BallEnteredOrLeftBubbleGroupMonitor::OnEnter')
    def OnEnter(self):
        self.bubbleIdSet = self.GetMemberBubbleSet()
        self.GetServiceManager().RegisterForNotifyEvent(self, PROXIMITY_EVENT)
        for bubbleId in self.bubbleIdSet:
            self.context.ballpark.SetBubbleEvents(bubbleId, True)

        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.GetServiceManager().UnregisterForNotifyEvent(self, PROXIMITY_EVENT)
            for bubbleId in self.bubbleIdSet:
                self.context.ballpark.SetBubbleEvents(bubbleId, False)

        self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::ballparks::BallEnteredOrLeftBubbleGroupMonitor::DoBubbleProximity')
    def DoBubbleProximity(self, solarSystemId, bubbleId, ballId, isEntering):
        if self.IsInvalid():
            return
        if bubbleId in self.bubbleIdSet:
            self.behaviorTree.RequestReset(requestedBy=self)

    def GetServiceManager(self):
        return sm


class TargetChangingBubbleMonitor(BubbleChangedMonitor):

    def DoBubbleProximity(self, solarSystemId, bubbleId, ballId, isEntering):
        if self.IsInvalid():
            return
        if bubbleId != self.bubbleId:
            return
        if isEntering != self.attributes.resetOnEnter:
            return
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        if ballId != targetId:
            return
        logger.debug('Target %s is %s my bubble', ballId, 'entering' if isEntering else 'leaving')
        self.behaviorTree.RequestReset(requestedBy=self)


class TargetWithOwnerEnteredBubbleMonitor(Task):

    def __init__(self, attributes = None):
        super(TargetWithOwnerEnteredBubbleMonitor, self).__init__(attributes)
        self.bubbleIdSet = None

    @TimedFunction('behaviors::monitors::ballparks::TargetWithOwnerEnteredBubbleMonitor::OnEnter')
    def OnEnter(self):
        self.bubbleIdSet = None
        if self.attributes.ownerIds:
            self.bubbleIdSet = self.GetBubbleIdSet()
            self.bubbleIdSet.update(self.GetBubbleIdSet())
            self.SubscribeToBubbleEnter()
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid() and self.attributes.ownerIds:
            self.UnsubscribeFromBubbleEnter()
        self.SetStatusToInvalid()

    def SubscribeToBubbleEnter(self):
        for bubbleId in self.bubbleIdSet:
            self.SubscribeBubbleProximityEntered(bubbleId)
            self.context.ballpark.SetBubbleEvents(bubbleId, True)

    def SubscribeBubbleProximityEntered(self, bubbleId):
        messenger = self.GetEventMessenger()
        messenger.SubscribeBubble(bubbleId, MESSAGE_ON_BUBBLE_PROXIMITY_ENTERED, self.OnBubbleEntered)

    def UnsubscribeFromBubbleEnter(self):
        if self.bubbleIdSet is None:
            return
        for bubbleId in self.bubbleIdSet:
            self.UnsubscribeBubbleProximityEntered(bubbleId)
            self.context.ballpark.SetBubbleEvents(bubbleId, False)

        self.bubbleIdSet = None

    def UnsubscribeBubbleProximityEntered(self, bubbleId):
        messenger = self.GetEventMessenger()
        messenger.UnsubscribeBubble(bubbleId, MESSAGE_ON_BUBBLE_PROXIMITY_ENTERED, self.OnBubbleEntered)

    @TimedFunction('behaviors::monitors::ballparks::TargetWithOwnerEnteredBubbleMonitor::OnBubbleEntered')
    def OnBubbleEntered(self, ballId):
        if self.IsInvalid():
            return
        ballpark = self.context.ballpark
        slimItem = ballpark.slims.get(ballId)
        if slimItem and slimItem.ownerID not in self.attributes.ownerIds:
            return
        logger.debug('Target %s with owner %s is entering bubble %s', ballId, slimItem.ownerID, ballpark.balls[ballId].newBubbleId)
        targetSet = self.GetLastBlackboardValue(self.attributes.targetSetAddress) or set()
        if ballId not in targetSet:
            targetSet.add(ballId)
            self.SendBlackboardValue(self.attributes.targetSetAddress, targetSet)

    def GetBubbleIdSet(self):
        return {self.context.myBall.newBubbleId}


class TargetsWithOwnerEnteredBubbleMonitor(TargetWithOwnerEnteredBubbleMonitor, GroupTaskMixin):

    def GetBubbleIdSet(self):
        return self.GetMemberBubbleSet()


class TargetLeavingParkMonitor(Task):

    @TimedFunction('behaviors::monitors::ballparks::TargetLeavingParkMonitor::OnEnter')
    def OnEnter(self):
        self.targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        self.context.ballpark.eventMessenger.SubscribeItem(self.targetId, MESSAGE_ON_ITEM_REMOVED_FROM_PARK, self._OnItemLeavingPark)
        self.status = status.TaskSuccessStatus

    def CleanUp(self):
        if not self.IsInvalid():
            self.SetStatusToInvalid()
            self.context.ballpark.eventMessenger.UnsubscribeItem(self.targetId, MESSAGE_ON_ITEM_REMOVED_FROM_PARK, self._OnItemLeavingPark)

    def _OnItemLeavingPark(self, itemId):
        targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        if itemId != targetId:
            return
        if self.attributes.clearValue:
            self.SendBlackboardValue(self.attributes.targetAddress, None)
        self.behaviorTree.RequestReset(requestedBy=self)


class MonitorProximitySensors(Task):

    def __init__(self, attributes = None):
        super(MonitorProximitySensors, self).__init__(attributes)
        self.proximitySensorIds = set()
        self.bubbleIdSet = None
        self.tags = set()

    @TimedFunction('behaviors::monitors::ballparks::MonitorProximitySensors::OnEnter')
    def OnEnter(self):
        self._SetTags()
        self.proximitySensorIds.clear()
        super(MonitorProximitySensors, self).OnEnter()
        self.SetBubbleIdSet(self.GetBubbleIdSet())
        proximitySensors = self.FindProximitySensorsForBubbleSet()
        itemIds = self.FindItemsInSensorRange(proximitySensors)
        self.ClassifyItems(itemIds)
        self.SubscribeToProximitySensor(proximitySensors)
        self.SetStatusToSuccess()

    def _SetTags(self):
        tags = getattr(self.attributes, 'tags', None) or []
        self.tags = get_behavior_sensor_tags(self.context, tags)

    def ClassifyItems(self, itemIds):
        update_blackboard_set_if_changed(self, itemIds, self.attributes.objectListAddress)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeProximitySensors()
        super(MonitorProximitySensors, self).CleanUp()

    def UnsubscribeProximitySensors(self):
        for itemId in self.proximitySensorIds:
            self.UnsubscribeItem(itemId, MESSAGE_ON_PROXIMITY, self.OnProximityDetected)

        self.proximitySensorIds.clear()

    @TimedFunction('behaviors::monitors::ballparks::MonitorProximitySensors::FindItemsInSensorRange')
    def FindItemsInSensorRange(self, proximitySensors):
        itemIds = set()
        for component in proximitySensors:
            for itemId in component.GetBallIdsInRange():
                if self.IsValidTarget(itemId):
                    itemIds.add(itemId)

        return itemIds

    @TimedFunction('behaviors::monitors::ballparks::MonitorProximitySensors::FindProximitySensorsInBubble')
    def FindProximitySensorsForBubbleSet(self):
        proximitySensorComponents = []
        for component in self.GetProximitySensors():
            if self.InSameBubble(component.GetBubbleId()):
                proximitySensorComponents.append(component)

        return proximitySensorComponents

    def SubscribeToProximitySensor(self, proximitySensors):
        for sensor in proximitySensors:
            self.proximitySensorIds.add(sensor.itemID)
            self.SubscribeItem(sensor.itemID, MESSAGE_ON_PROXIMITY, self.OnProximityDetected)

    @TimedFunction('behaviors::monitors::ballparks::MonitorProximitySensors::GetProximitySensors')
    def GetProximitySensors(self):
        return get_proximity_sensors(self, *self.tags)

    def IsValidTarget(self, itemId):
        slim = self.context.ballpark.slims.get(itemId)
        if not slim:
            return False
        if self.attributes.includedCategories and slim.categoryID not in self.attributes.includedCategories:
            return False
        if self.attributes.excludedGroups and slim.groupID in self.attributes.excludedGroups:
            return False
        if self.attributes.validOwnerIds and slim.ownerID not in self.attributes.validOwnerIds:
            return False
        if self.attributes.invalidOwnerIds and slim.ownerID in self.attributes.invalidOwnerIds:
            return False
        if is_ball_cloaked(self, itemId):
            return False
        return True

    def OnProximityDetected(self, ballId, isEntering):
        uthread2.start_tasklet(self._OnProximityDetected, ballId, isEntering)

    def _OnProximityDetected(self, ballId, isEntering):
        if self.IsInvalid():
            return
        if isEntering and self.IsValidTarget(ballId):
            self.ClassifyItems({ballId})

    def InSameBubble(self, bubbleId):
        return bubbleId in self.bubbleIdSet

    def SetBubbleIdSet(self, bubbleIdSet):
        self.bubbleIdSet = bubbleIdSet

    def GetBubbleIdSet(self):
        return {self.context.myBall.newBubbleId}


class MonitorProximitySensorsForGroupMembers(MonitorProximitySensors, GroupTaskMixin):

    def GetBubbleIdSet(self):
        return self.GetMemberBubbleSet()


class MonitorSpecificProximitySensor(MonitorProximitySensors):

    @TimedFunction('behaviors::monitors::ballparks::MonitorSpecificProximitySensor::GetProximitySensors')
    def GetProximitySensors(self):
        proximitySensorId = self.GetLastBlackboardValue(self.attributes.proximitySensorAddress)
        if proximitySensorId and self.context.ballpark.HasBall(proximitySensorId):
            proximitySensor = get_proximity_sensor(self, proximitySensorId)
            return [proximitySensor]
        return []


class MonitorSpecificProximitySensorForGroupMembers(MonitorSpecificProximitySensor, GroupTaskMixin):

    def GetBubbleIdSet(self):
        return self.GetMemberBubbleSet()


class MonitorInvulnerabilityCanceledInBubble(Task):

    def __init__(self, attributes = None):
        super(MonitorInvulnerabilityCanceledInBubble, self).__init__(attributes)
        self.bubbleIdSet = None

    @TimedFunction('behaviors::monitors::ballparks::MonitorInvulnerabilityCanceledInBubble::OnEnter')
    def OnEnter(self):
        self.SubscribeToInvulnerabilityCanceledInBubbles()
        self.SetStatusToSuccess()

    def SubscribeToInvulnerabilityCanceledInBubbles(self):
        self.bubbleIdSet = self.GetBubbleIds()
        messenger = self.GetEventMessenger()
        for bubbleId in self.bubbleIdSet:
            messenger.SubscribeBubble(bubbleId, MESSAGE_INVULNERABILITY_CANCELED, self.OnInvulnerabilityCanceled)

    def UnsubscribeToInvulnerabilityCanceledInBubbles(self):
        messenger = self.GetEventMessenger()
        for bubbleId in self.bubbleIdSet:
            messenger.UnsubscribeBubble(bubbleId, MESSAGE_INVULNERABILITY_CANCELED, self.OnInvulnerabilityCanceled)

        self.bubbleIdSet = None

    def GetBubbleIds(self):
        return {self.context.myBall.newBubbleId}

    @TimedFunction('behaviors::monitors::ballparks::MonitorInvulnerabilityCanceledInBubble::OnInvulnerabilityCanceled')
    def OnInvulnerabilityCanceled(self, itemId, isCompleted, reason):
        if self.IsInvalid():
            return
        if not self.IsValidTarget(itemId):
            return
        logger.debug('Invulnerability canceled isCompleted=%s reason=%s', isCompleted, reason)
        self.behaviorTree.RequestReset(requestedBy=self)

    def IsValidTarget(self, itemId):
        if self.attributes.targetIdListAddress is None:
            return True
        targetIdList = self.GetLastBlackboardValue(self.attributes.targetIdListAddress)
        if targetIdList and itemId in targetIdList:
            return True
        return False

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeToInvulnerabilityCanceledInBubbles()
        super(MonitorInvulnerabilityCanceledInBubble, self).CleanUp()


class MonitorInvulnerabilityCanceledInGroupBubbles(MonitorInvulnerabilityCanceledInBubble, GroupTaskMixin):

    def GetBubbleIds(self):
        return self.GetMemberBubbleSet()


class ClearBlackboardChannelOnItemExplosion(Task):

    @TimedFunction('behaviors::monitors::ballparks::MonitorItemExplosion::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        item_id = self.GetLastBlackboardValue(self.attributes.itemIdAddress)
        if self.context.ballpark.HasBall(item_id):
            self.item_id = item_id
            self.SubscribeItem(item_id, MESSAGE_ON_BALLPARK_ITEM_DESTROY, self._clear_black_board_channel_on_explosion)
        else:
            self.item_id = None

    def _clear_black_board_channel_on_explosion(self, exploding_item_id):
        if exploding_item_id == self.item_id:
            self.SendBlackboardValue(self.attributes.blackBoardChannelAddress, None)
            self.behaviorTree.RequestReset(self)

    def CleanUp(self):
        if not self.IsInvalid() and self.item_id is not None:
            self.UnsubscribeItem(self.item_id, MESSAGE_ON_BALLPARK_ITEM_DESTROY, self._clear_black_board_channel_on_explosion)
        self.SetStatusToInvalid()
