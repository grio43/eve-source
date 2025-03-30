#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\recommendationSvc.py
import collections
import logging
import uuid
import launchdarkly
import uthread2
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.recommendation.const import CURRENT_ACTIVE, COMPLETED, NUM_SLOTS, MAX_QUEUE_LENGTH
from eve.client.script.ui.shared.recommendation.message_bus.recommendationMessenger import RecommendationMessenger
from eve.client.script.ui.shared.recommendation.recommendationController import RecommendationController, LastActiveOperationInfo
from eve.client.script.ui.shared.recommendation.uiConst import HAS_ACCEPTED, HAS_INTERACTED_WITH
from launchdarkly.client.const import OPPORTUNITIES_UI
from operations.client.operationscontroller import GetOperationsController
from operations.common.const import OPERATION_CATEGORY_RECOMMENDATIONS
logger = logging.getLogger(__name__)
FEATURE_FLAG_FALLBACK = False

class RecommendationService(Service):
    __guid__ = 'svc.recommendationSvc'
    __displayname__ = 'Recommendation Service'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = ['OnOperationCompleted', 'OnOperationMadeActive', 'OnSessionReset']

    def __init__(self):
        super(RecommendationService, self).__init__()
        self.ResetVariables()
        self._enabled = FEATURE_FLAG_FALLBACK
        launchdarkly.get_client().notify_flag(OPPORTUNITIES_UI, FEATURE_FLAG_FALLBACK, self._refresh_feature_flag)

    def _refresh_feature_flag(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self._enabled = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)

    def ResetVariables(self):
        self.availableRecommendationQueue = collections.deque(maxlen=MAX_QUEUE_LENGTH)
        self.recommendationControllerBySlotID = {}
        self.activeRecommendation = None
        self.characterHasReceivedRecommendations = False

    def OnSessionReset(self):
        self.ResetVariables()

    def HasRecommendations(self):
        return any([ controller.operationID for controller in self.recommendationControllerBySlotID.values() ])

    def AddToQueue(self, operation_recommendations):
        if not operation_recommendations:
            return
        for recommendation in operation_recommendations:
            operationID, journeyID = self.UnpackOperationRecommendation(recommendation)
            if not operationID or not journeyID:
                logger.error('recommendation is missing a required component, operationID or journeyID is None')
                continue
            self.availableRecommendationQueue.append((operationID, journeyID))

        self.TryPopulateAllSlotControllers()
        sm.GetService('infoPanel').UpdateOperationsPanel(OPERATION_CATEGORY_RECOMMENDATIONS)

    def TryPopulateAllSlotControllers(self):
        for slotIdx in range(NUM_SLOTS):
            self.TryPopulateSlotController(slotIdx)

    def TryPopulateSlotController(self, slotIdx):
        controller = self.GetRecommendationControllerForSlot(slotIdx)
        if not controller:
            logger.warn('TryPopulateSlotController: could not get recommendation controller for this slot: %d' % slotIdx)
            return
        controller.TryPopulateController()

    def GetRecommendationControllerForSlot(self, slotIdx):
        if slotIdx in self.recommendationControllerBySlotID:
            return self.recommendationControllerBySlotID[slotIdx]
        return self._CreateRecommendationControllerForSlot(slotIdx)

    def GetRecommendationFromQueue(self):
        try:
            operationRecommendation = self.availableRecommendationQueue.popleft()
        except IndexError:
            return (None, None)

        return operationRecommendation

    @staticmethod
    def UnpackOperationRecommendation(operationRecommendation):
        try:
            operationID = operationRecommendation.operation.sequential
            recommendationJourneyID = uuid.UUID(bytes=operationRecommendation.journey)
        except AttributeError:
            logger.exception('failed to unpack operation recommendation')
            return (None, None)

        return (operationID, recommendationJourneyID)

    def _CreateRecommendationControllerForSlot(self, slotIdx):
        if self.activeRecommendation and not self.IsActiveRecommendationInASlot():
            operationID = self.activeRecommendation.operationID
            journeyID = None
        else:
            operationID, journeyID = self.GetRecommendationFromQueue()
        recommendationController = RecommendationController(operationID=operationID, slotIdx=slotIdx, journeyID=journeyID)
        self.recommendationControllerBySlotID[slotIdx] = recommendationController
        return recommendationController

    def IsActiveRecommendationInASlot(self):
        if not self.activeRecommendation:
            return False
        return any((controller.operationID == self.activeRecommendation.operationID for controller in self.recommendationControllerBySlotID.values()))

    def AcceptRecommendation(self, operationID, journeyID):
        settings.char.ui.Set(HAS_ACCEPTED, True)
        uthread2.StartTasklet(self._SendRecommendationAcceptedEvent, operationID, journeyID)
        sm.ScatterEvent('OnRecommendationAccepted')

    def _SendRecommendationAcceptedEvent(self, operationID, journeyID):
        message_bus = RecommendationMessenger(self.publicGatewaySvc)
        message_bus.accepted(operationID, journeyID)

    def QuitRecommendation(self, operationID, slotIdx):
        if operationID != GetOperationsController().get_active_operation_id():
            logger.error("Can't quit an inactive operation")
            return
        GetOperationsController().manager.cancel_current_treatment_operation()
        self.activeRecommendation = None
        self.ClearSlot(slotIdx)
        self.RequestRecommendations(1, allowOld=False)

    def DismissRecommendation(self, operationID, journeyID, slotIdx):
        if operationID == GetOperationsController().get_active_operation_id():
            self.QuitRecommendation(operationID, slotIdx)
        self.ClearSlot(slotIdx)
        uthread2.StartTasklet(self._SendRecommendationDismissedEvent, operationID, journeyID)
        if len(self.availableRecommendationQueue):
            self.TryPopulateSlotController(slotIdx)
        else:
            uthread2.StartTasklet(self.RequestRecommendations, 1, False)

    def _SendRecommendationDismissedEvent(self, operationID, journeyID):
        if not operationID:
            logger.error('can not dismiss this operation recommendation, operationID is None')
            return
        message_bus = RecommendationMessenger(self.publicGatewaySvc)
        message_bus.dismissed(operationID, journeyID)

    def ClearSlot(self, slotIdx):
        controller = self.GetRecommendationControllerForSlot(slotIdx)
        if not controller:
            return
        controller.ResetController()

    def OnOperationMadeActive(self, categoryID, operationID, *args, **kwargs):
        if categoryID != OPERATION_CATEGORY_RECOMMENDATIONS:
            self.activeRecommendation = None
            return
        self.SetActiveRecommendation()
        if self.activeRecommendation and self.IsActiveRecommendationInASlot():
            slotIdx = self.GetSlotIDForOperation(operationID)
            self.SetStatusForRecommendation(slotIdx, CURRENT_ACTIVE)
        else:
            self.GetSlotForActiveRecommendation()

    def GetSlotForActiveRecommendation(self):
        for controller in self.recommendationControllerBySlotID.values():
            existingRecommendationID = controller.operationID
            existingRecommendationJourneyID = controller.journeyID
            self.availableRecommendationQueue.appendleft((existingRecommendationID, existingRecommendationJourneyID))
            controller.ResetController()
            controller.operationID = self.activeRecommendation.operationID
            break
        else:
            self.GetRecommendationControllerForSlot(0)

    def SetActiveRecommendation(self):
        activeOperation = GetOperationsController().get_active_operation()
        if not activeOperation:
            self.activeRecommendation = None
            return
        taskTuples = GetOperationsController().get_active_task_tuples()
        self.activeRecommendation = LastActiveOperationInfo(OPERATION_CATEGORY_RECOMMENDATIONS, activeOperation, taskTuples)

    def SendRecommendationDisplayedEvent(self, operationID, journeyID):
        message_bus = RecommendationMessenger(self.publicGatewaySvc)
        message_bus.displayed(operationID, journeyID)

    def OnOperationCompleted(self, categoryID, operationID):
        if categoryID != OPERATION_CATEGORY_RECOMMENDATIONS:
            return
        if not self.activeRecommendation:
            return
        hasCompletedActiveRecommendation = operationID == self.activeRecommendation.operationID
        if not hasCompletedActiveRecommendation:
            return
        slotIDx = self.GetSlotIDForOperation(operationID)
        self.SetStatusForRecommendation(slotIDx, COMPLETED)
        controller = self.recommendationControllerBySlotID.get(slotIDx, None)
        if not controller:
            logger.warn('could not get recommendation controller for this operationID: %d, slot: %d' % (operationID, slotIDx))
            return
        sm.ScatterEvent('OnOperationRecommendationCompleted', operationID)

    def GetSlotIDForOperation(self, operationID):
        slotIDx = None
        for slotID, controller in self.recommendationControllerBySlotID.iteritems():
            if operationID == controller.operationID:
                slotIDx = slotID

        return slotIDx

    def SetStatusForRecommendation(self, slotID, newStatus):
        controller = self.recommendationControllerBySlotID.get(slotID, None)
        if not controller:
            logger.warn('could not get recommendation controller for this slotID: %d' % slotID)
            return
        controller.SetStatus(newStatus)

    def IsActiveRecommendationComplete(self):
        if not self.activeRecommendation:
            return False
        operationID = self.activeRecommendation.operationID
        if not operationID:
            return False
        slotIDx = self.GetSlotIDForOperation(operationID)
        if not slotIDx:
            return False
        controller = self.GetRecommendationControllerForSlot(slotIDx)
        return controller.IsCompleted()

    def ShowLastCompleted(self):
        return self.IsActiveRecommendationComplete() and self.IsThereUnseenAndCompletedRecommendation()

    def IsThereUnseenAndCompletedRecommendation(self):
        for slotIdx in range(NUM_SLOTS):
            controller = self.GetRecommendationControllerForSlot(slotIdx)
            if not controller:
                logger.warn('could not get recommendation controller for this slot: %d' % slotIdx)
                continue
            if controller.IsCompletedAndUnseen():
                return True

        return False

    def RequestRecommendations(self, amount, allowOld = False):
        if not self.IsFeatureEnabled() or not self.publicGatewaySvc.is_available():
            return
        message_bus = RecommendationMessenger(self.publicGatewaySvc)
        message_bus.request_recommendations(amount, allowOld, response_function=self.AddToQueue, timeout_function=self.RequestTimeoutHandler)

    def RequestTimeoutHandler(self):
        for controller in self.recommendationControllerBySlotID.values():
            controller.onRequestTimeout()

    def ShouldInfoPanelBlink(self):
        if not settings.char.ui.Get(HAS_INTERACTED_WITH, False):
            return True
        return self.IsThereUnseenAndCompletedRecommendation()

    def IsFeatureEnabled(self):
        if not sm.GetService('publicGatewaySvc').is_available():
            return False
        return self._enabled

    @staticmethod
    def ShouldBtnsBlink():
        return not settings.char.ui.Get(HAS_INTERACTED_WITH, False)

    @staticmethod
    def HasEverAcceptedARecommendation():
        return settings.char.ui.Get(HAS_ACCEPTED, False)
