#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\combat.py
import logging
import ballpark.messenger.const as messages
import evetypes
from behaviors.blackboards import BlackboardDeletedError
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_ball_position
from behaviors.utility.owner import get_owner_id
from ccpProfile import TimedFunction
from crimewatch.util import GetAggressorId
from eveexceptions.exceptionEater import ExceptionEater
from eve.common.script.sys import idCheckers
logger = logging.getLogger(__name__)

class WaitForAggressiveAct(Task):

    @TimedFunction('behaviors::monitors::combat::WaitForAggressiveAct::OnEnter')
    def OnEnter(self):
        self.SubscribeItem(self.context.myItemId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)
        self.SubscribeItem(self.context.myItemId, messages.MESSAGE_INDIRECT_OFFENSE_EVENT, self._OnIndirectOffenseEvent)
        self.SetStatusToSuccess()

    def CleanUp(self):
        super(WaitForAggressiveAct, self).CleanUp()
        self.UnsubscribeItem(self.context.myItemId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)
        self.UnsubscribeItem(self.context.myItemId, messages.MESSAGE_INDIRECT_OFFENSE_EVENT, self._OnIndirectOffenseEvent)

    def AddAggressorAndResetTree(self, aggressorID, targetTypeID):
        try:
            combatSet = self.GetLastBlackboardValue(self.attributes.combatTargetsAddress) or set()
        except BlackboardDeletedError:
            logger.debug(u'WaitForAggressiveAct:::Combat target address references deleted blackboard: %s', unicode(self.attributes.combatTargetsAddress))
            return

        if aggressorID not in combatSet:
            logger.debug('Entity aggressed: %s', aggressorID)
            combatSet.add(aggressorID)
            self.SendBlackboardValue(self.attributes.combatTargetsAddress, combatSet)
            self.behaviorTree.RequestReset(requestedBy=self)
            self._LogAggression(aggressorID, targetTypeID)
            self.OnNewAggressorDetected()

    def AddAggressorsAndResetTree(self, categoryID, sourceOwnerID, aggressorID, targetTypeID):
        aggressorID = GetAggressorId(categoryID, sourceOwnerID, aggressorID)
        self.AddAggressorAndResetTree(aggressorID, targetTypeID)

    @TimedFunction('behaviors::monitors::combat::WaitForAggressiveAct::_OnCrimewatchEventStarted')
    def _OnCrimewatchEventStarted(self, effectKey, effectInfo):
        if self.IsInvalid():
            return
        if effectInfo.isAssistance:
            return
        aggressorID = effectKey.shipID
        categoryID = evetypes.GetCategoryID(effectInfo.moduleTypeID)
        if self.IsValidAggressor(aggressorID):
            self.AddAggressorsAndResetTree(categoryID, effectInfo.sourceOwnerID, aggressorID, effectInfo.targetTypeID)

    @TimedFunction('behaviors::monitors::combat::WaitForAggressiveAct::_OnIndirectOffenseEvent')
    def _OnIndirectOffenseEvent(self, sourceOwnerId, targetItem):
        if self.IsInvalid():
            return
        try:
            offendingOwner = self.context.ballpark.inventory2.GetItem(sourceOwnerId)
        except RuntimeError:
            pass
        else:
            if offendingOwner:
                offendingShipID = offendingOwner.locationID
                offendingItem = self.context.ballpark.inventory2.GetItem(offendingShipID)
                if self.IsValidAggressor(offendingShipID):
                    self.AddAggressorsAndResetTree(offendingItem.categoryID, sourceOwnerId, offendingShipID, targetItem.typeID)

    def _LogAggression(self, aggressorID, targetTypeID):
        with ExceptionEater('WaitForAggressiveAct.LogAggression'):
            entity_group = self.context.entityLocation.GetBehaviorEntityGroup(self.context.myEntityGroupId)
            self.context.eventLogger.log_behavior_aggressed(get_owner_id(self), self.behaviorTree.GetBehaviorId(), self._GetGroupBehaviorId(entity_group), targetTypeID, aggressorID)

    def OnNewAggressorDetected(self):
        pass

    def _GetGroupBehaviorId(self, entity_group):
        if entity_group is not None:
            return entity_group.GetBehaviorId()
        return self.behaviorTree.GetBehaviorId()

    def IsValidAggressor(self, aggressorID):
        if not aggressorID:
            return False
        ballpark = self.context.ballpark
        ball = ballpark.GetBallOrNone(aggressorID)
        if ball is None:
            return False
        return all((filterfunction(ballpark, ball) for filterfunction in self._GetFilterFunctions()))

    def _GetFilterFunctions(self):
        return [self._PlayerAggressorFilter]

    def _PlayerAggressorFilter(self, ballpark, ball):
        if getattr(self.attributes, 'onlyPlayerAggressors', False):
            slimItem = ballpark.GetSlimItem(ball.id)
            if not slimItem or slimItem.ownerID is None:
                return False
            if not idCheckers.IsPlayerOwner(slimItem.ownerID):
                return False
        return True


class SetFlagAndResetWhenAggressed(WaitForAggressiveAct):

    def AddAggressorsAndResetTree(self, categoryID, sourceOwnerID, aggressorID, targetTypeID):
        self.SendBlackboardValue(self.attributes.flagAddress, True)
        self.behaviorTree.RequestReset(requestedBy=self)


class FlagAggressionAndReportMyPosition(WaitForAggressiveAct):

    def OnNewAggressorDetected(self):
        my_position = get_ball_position(self, self.context.myItemId)
        self.SendBlackboardValue(self.attributes.flagAddress, True)
        self.SendBlackboardValue(self.attributes.myPositionAddress, my_position)


class ClearValueAndResetIfTargetCloaks(Task):

    @TimedFunction('behaviors::monitors::combat::ClearValueAndResetIfTargetCloaks::OnEnter')
    def OnEnter(self):
        self.targetId = self.GetLastBlackboardValue(self.attributes.targetAddress)
        if self.targetId is not None:
            self.SubscribeToCloakChanged()
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeFromCloakChanged()
            self.targetId = None
            self.SetStatusToInvalid()

    def SubscribeToCloakChanged(self):
        self.SubscribeItem(self.targetId, messages.MESSAGE_ON_CLOAK_BALL, self._OnCloakBall)

    def UnsubscribeFromCloakChanged(self):
        self.UnsubscribeItem(self.targetId, messages.MESSAGE_ON_CLOAK_BALL, self._OnCloakBall)

    @TimedFunction('behaviors::monitors::combat::ClearValueAndResetIfTargetCloaks::_OnCloakChanged')
    def _OnCloakBall(self, itemId):
        self.SendBlackboardValue(self.attributes.valueAddress, None)
        self.behaviorTree.RequestReset(requestedBy=self)


class MaxLockedTargetsChangedMonitor(Task):

    @TimedFunction('behaviors::monitors::combat::MaxLockedTargetsChangedMonitor::OnEnter')
    def OnEnter(self):
        self.SubscribeItem(self.context.myItemId, messages.MESSAGE_MAX_LOCKED_TARGETS_CHANGED, self._OnMaxLockedTargetsChanged)
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, messages.MESSAGE_MAX_LOCKED_TARGETS_CHANGED, self._OnMaxLockedTargetsChanged)
        super(MaxLockedTargetsChangedMonitor, self).CleanUp()

    @TimedFunction('behaviors::monitors::combat::MaxLockedTargetsChangedMonitor::_OnMaxLockedTargetsChanged')
    def _OnMaxLockedTargetsChanged(self):
        if not self.IsInvalid():
            self.behaviorTree.RequestReset(requestedBy=self)


class MonitorAssistanceToTargets(WaitForAggressiveAct):

    @TimedFunction('behaviors::monitors::combat::MonitorAssistanceToTargets::OnEnter')
    def OnEnter(self):
        combatTargetIds = self.GetLastBlackboardValue(self.attributes.combatTargetsAddress)
        self.SubscribeToTargetsInBubble(combatTargetIds, self.context.myBall.newBubbleId)
        self.SetStatusToSuccess()

    def SubscribeToTargetsInBubble(self, combatTargetIds, bubbleId):
        if not combatTargetIds:
            return
        monitoredTargetSet = self.GetMonitoredTargets()
        destinyBalls = self.context.ballpark.balls
        for combatTargetId in combatTargetIds:
            ball = destinyBalls.get(combatTargetId)
            if ball and ball.newBubbleId == bubbleId:
                monitoredTargetSet.add(combatTargetId)
                self.SubscribeItem(combatTargetId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeFromMonitoredTargets()
            self.SetStatusToInvalid()

    def UnsubscribeFromMonitoredTargets(self):
        monitoredTargetSet = self.GetMonitoredTargets()
        if not monitoredTargetSet:
            return
        for monitoredTargetId in monitoredTargetSet:
            self.UnsubscribeItem(monitoredTargetId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)

        self.SetMonitoredTargets(None)

    @TimedFunction('behaviors::monitors::combat::MonitorAssistanceToTargets::_OnCrimewatchEventStarted')
    def _OnCrimewatchEventStarted(self, effectKey, effectInfo):
        if self.IsInvalid():
            return
        if not effectInfo.isAssistance:
            return
        aggressorID = effectKey.shipID
        categoryID = evetypes.GetCategoryID(effectInfo.moduleTypeID)
        self.AddAggressorsAndResetTree(categoryID, effectInfo.sourceOwnerID, aggressorID, effectInfo.targetTypeID)

    def GetMonitoredTargets(self):
        if not self.HasContextValue('monitoredTargetSet'):
            return set()
        return self.GetContextValue('monitoredTargetSet')

    def SetMonitoredTargets(self, monitoredTargetSet):
        self.SetContextValue('monitoredTargetSet', monitoredTargetSet)


class MonitorAssistanceToGroupTargets(MonitorAssistanceToTargets, GroupTaskMixin):

    def OnEnter(self):
        combatTargetIds = self.GetLastBlackboardValue(self.attributes.combatTargetsAddress)
        for bubbleId in self.GetMemberBubbleSet():
            self.SubscribeToTargetsInBubble(combatTargetIds, bubbleId)

        self.SetStatusToSuccess()


class MonitorAggressionTowardsTargets(WaitForAggressiveAct):

    @TimedFunction('behaviors::monitors::combat::MonitorAggressionTowardsTargets::OnEnter')
    def OnEnter(self):
        monitoredTargetIds = self.GetLastBlackboardValue(self.attributes.monitoredTargetsAddress)
        self.SubscribeToTargetsInBubble(monitoredTargetIds, self.context.myBall.newBubbleId)
        self.SetStatusToSuccess()

    def SubscribeToTargetsInBubble(self, monitoredTargetIds, bubbleId):
        if not monitoredTargetIds:
            return
        monitoredTargetSet = self.GetMonitoredTargets()
        destinyBalls = self.context.ballpark.balls
        for targetId in monitoredTargetIds:
            ball = destinyBalls.get(targetId)
            if ball and ball.newBubbleId == bubbleId:
                monitoredTargetSet.add(targetId)
                self.SubscribeItem(targetId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)
                self.SubscribeItem(targetId, messages.MESSAGE_INDIRECT_OFFENSE_EVENT, self._OnIndirectOffenseEvent)

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeFromMonitoredTargets()
            self.SetStatusToInvalid()

    def UnsubscribeFromMonitoredTargets(self):
        monitoredTargetSet = self.GetMonitoredTargets()
        if not monitoredTargetSet:
            return
        for monitoredTargetId in monitoredTargetSet:
            self.UnsubscribeItem(monitoredTargetId, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self._OnCrimewatchEventStarted)
            self.UnsubscribeItem(self.context.myItemId, messages.MESSAGE_INDIRECT_OFFENSE_EVENT, self._OnIndirectOffenseEvent)

        self.SetMonitoredTargets(None)

    @TimedFunction('behaviors::monitors::combat::MonitorAggressionTowardsTargets::_OnCrimewatchEventStarted')
    def _OnCrimewatchEventStarted(self, effectKey, effectInfo):
        if self.IsInvalid():
            return
        if not effectInfo.isOffensive:
            return
        aggressorID = effectKey.shipID
        categoryID = evetypes.GetCategoryID(effectInfo.moduleTypeID)
        self.AddAggressorsAndResetTree(categoryID, effectInfo.sourceOwnerID, aggressorID, effectInfo.targetTypeID)

    def GetMonitoredTargets(self):
        if not self.HasContextValue('monitoredTargetSet'):
            return set()
        return self.GetContextValue('monitoredTargetSet')

    def SetMonitoredTargets(self, monitoredTargetSet):
        self.SetContextValue('monitoredTargetSet', monitoredTargetSet)

    @TimedFunction('behaviors::monitors::combat::MonitorAggressionTowardsTargets::_OnIndirectOffenseEvent')
    def _OnIndirectOffenseEvent(self, sourceOwnerId, targetItem):
        if self.IsInvalid():
            return
        try:
            offendingOwner = self.context.ballpark.inventory2.GetItem(sourceOwnerId)
        except RuntimeError:
            pass
        else:
            if offendingOwner:
                offendingShipID = offendingOwner.locationID
                offendingItem = self.context.ballpark.inventory2.GetItem(offendingShipID)
                self.AddAggressorsAndResetTree(offendingItem.categoryID, sourceOwnerId, offendingShipID, targetItem.typeID)

    def _LogAggression(self, aggressorID, targetTypeID):
        with ExceptionEater('MonitorAggressionTowardsTargets.LogAggression'):
            entity_group = self.context.entityLocation.GetBehaviorEntityGroup(self.context.myEntityGroupId)
            self.context.eventLogger.log_monitored_target_aggressed(get_owner_id(self), self.behaviorTree.GetBehaviorId(), self._GetGroupBehaviorId(entity_group), targetTypeID, aggressorID)


class MonitorAggressionTowardsGroupTargets(MonitorAggressionTowardsTargets, GroupTaskMixin):

    def OnEnter(self):
        monitoredTargetIds = self.GetLastBlackboardValue(self.attributes.monitoredTargetsAddress)
        for bubbleId in self.GetMemberBubbleSet():
            self.SubscribeToTargetsInBubble(monitoredTargetIds, bubbleId)

        self.SetStatusToSuccess()


class MonitorSecurityStatusLoss(Task):

    def GetServiceManager(self):
        return sm

    def __init__(self, attributes = None):
        super(MonitorSecurityStatusLoss, self).__init__(attributes)
        self._solarSystemID = None

    @TimedFunction('behaviors::monitors::combat::MonitorSecurityStatusLoss::OnEnter')
    def OnEnter(self):
        if self.context.ballpark:
            self._solarSystemID = self.context.ballpark.solarsystemID
            self.SubscribeItem(self._solarSystemID, messages.MESSAGE_SEC_STATUS_LOST_EVENT, self.OnSecStatusLost)
        self.SetStatusToSuccess()

    def _GetBubbleID(self):
        return self.context.myBall.newBubbleId

    def CleanUp(self):
        super(MonitorSecurityStatusLoss, self).CleanUp()
        if self._solarSystemID:
            self.UnsubscribeItem(self._solarSystemID, messages.MESSAGE_CRIMEWATCH_EVENT_STARTED, self.OnSecStatusLost)

    @TimedFunction('behaviors::monitors::combat::MonitorSecurityStatusLoss::OnSecStatusLost')
    def OnSecStatusLost(self, ownerID, shipID):
        if self.IsInvalid() or shipID is None:
            return
        ballpark = self.context.ballpark
        if not ballpark:
            return
        ball = ballpark.GetBallOrNone(shipID)
        if not ball:
            return
        if not self._IsInSameBubble(ball):
            return
        if self.attributes.maxDistance is not None:
            try:
                distance = ballpark.DistanceBetween(self.context.myItemId, shipID)
                if distance > self.attributes.maxDistance:
                    return
            except StandardError:
                pass

        self.AddBallAsTargetAndResetTree(shipID)

    def _IsInSameBubble(self, ball):
        return ball.newBubbleId == self._GetBubbleID()

    def AddBallAsTargetAndResetTree(self, ballID):
        try:
            combatSet = self.GetLastBlackboardValue(self.attributes.combatTargetsAddress) or set()
        except BlackboardDeletedError:
            logger.debug(u'MonitorSecurityStatusLoss:::Combat target address references deleted blackboard: %s', unicode(self.attributes.combatTargetsAddress))
            return

        if ballID not in combatSet:
            combatSet.add(ballID)
            self.SendBlackboardValue(self.attributes.combatTargetsAddress, combatSet)
            self.behaviorTree.RequestReset(requestedBy=self)
