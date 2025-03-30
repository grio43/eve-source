#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\recommendation\recommendationController.py
import logging
from brennivin.itertoolsext import Bundle
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.shared.recommendation.const import NO_ACTIVE, REJECTED, COMPLETED, CURRENT_ACTIVE, ANOTHER_ACTIVE, BACKROUNDS_BY_TAG_ID, HINT_BY_TAG_ID, Sounds
from fsdBuiltData.common.tagsFSDLoader import TagsFSDLoader
from localization import GetByMessageID, GetByLabel
from operations.client.operationscontroller import GetOperationsController
from operations.common.fsdloaders import OperationsLoader
from signals import signal
logger = logging.getLogger(__name__)

class RecommendationController(object):

    def __init__(self, operationID, slotIdx, journeyID = None):
        self.operationID = operationID
        self.journeyID = journeyID
        self.slotIdx = slotIdx
        self._primaryTag = None
        self._operation = None
        self.status = None
        self.hasBeenSeenAfterCompletion = False
        self.recommendationSvc = sm.GetService('recommendationSvc')
        self.onNewRecommendation = signal.Signal(signalName='onNewRecommendation')
        self.onRequestTimeout = signal.Signal(signalName='onRequestTimeout')

    def TryPopulateController(self):
        if self.operationID:
            return
        self.ResetController()
        self.operationID, self.journeyID = self.recommendationSvc.GetRecommendationFromQueue()
        if not self.operationID or not self.journeyID:
            logger.exception('RecommendationController::TryPopulateController - missing operationID or journeyID')
            return
        self.onNewRecommendation()

    @property
    def operation(self):
        if not self._operation:
            operation = OperationsLoader.GetByID(self.operationID)
            if not operation:
                logger.error('Operation Recommendation not found in FSD: %d' % self.operationID)
                return
            self._operation = operation
        return self._operation

    def ResetController(self):
        self.operationID = None
        self.journeyID = None
        self.status = None
        self.hasBeenSeenAfterCompletion = False
        self._operation = None
        self._primaryTag = None

    @property
    def primaryTag(self):
        if not self._primaryTag:
            for tagID in self.operation.primaryTags:
                tag = TagsFSDLoader.GetByID(tagID)
                if tag:
                    self._primaryTag = Bundle(tagID=tagID, tagInfo=tag)
                    break

        return self._primaryTag

    def GetOperationName(self):
        return GetByMessageID(self.operation.title)

    def GetOperationDescription(self):
        return GetByMessageID(self.operation.description)

    def GetRecommendationIcon(self, solid = False):
        primaryTag = self.primaryTag
        if primaryTag:
            path = primaryTag.tagInfo.texturePath or ''
            if solid and path:
                path = path.replace('.png', 'White.png').replace('.jpg', 'White.jpg')
            return path
        return ''

    def GetRecommendationHint(self):
        primaryTag = self.primaryTag
        hintList = []
        if primaryTag:
            tagHintPath = HINT_BY_TAG_ID.get(primaryTag.tagID, None)
            if tagHintPath:
                tagText = GetByLabel(tagHintPath)
                if tagText:
                    tagHint = '%s%s' % (GetByLabel('UI/recommendations/Hints/TagHeader'), tagText)
                    hintList.append(tagHint)
        hintList.append(GetByMessageID(self.operation.extraHint) if self.operation.extraHint else None)
        hintList = filter(None, hintList)
        if hintList:
            return '<br><br>'.join(hintList)
        return ''

    def GetAgencyContentGroup(self):
        return self.operation.agencyContentGroupID

    def GetBackgroundPath(self):
        FALLBACK_IMAGE = ''
        primaryTag = self.primaryTag
        if primaryTag:
            tagID = primaryTag.tagID
            return BACKROUNDS_BY_TAG_ID.get(tagID, FALLBACK_IMAGE)
        return FALLBACK_IMAGE

    def RequestRecommendations(self, amount, allowOld = False):
        self.recommendationSvc.RequestRecommendations(amount, allowOld)

    def AcceptRecommendation(self, *args):
        PlaySound(Sounds.ACCEPT)
        self.recommendationSvc.AcceptRecommendation(self.operationID, self.journeyID)

    def QuitRecommendation(self, *args):
        PlaySound(Sounds.QUIT)
        self.recommendationSvc.QuitRecommendation(self.operationID, self.slotIdx)

    def DismissRecommendation(self, *args):
        PlaySound(Sounds.DISMISS)
        self.recommendationSvc.DismissRecommendation(self.operationID, self.journeyID, self.slotIdx)

    def RecommendationDisplayed(self):
        self.recommendationSvc.SendRecommendationDisplayedEvent(self.operationID, self.journeyID)

    def GetOperationState(self):
        activeOperationID = GetOperationsController().get_active_operation_id()
        if self.status in (REJECTED, COMPLETED):
            return self.status
        if not activeOperationID:
            return NO_ACTIVE
        if self.operationID == activeOperationID:
            return CURRENT_ACTIVE
        return ANOTHER_ACTIVE

    def SetStatus(self, newStatus):
        self.status = newStatus

    def IsCompleted(self):
        return self.status == COMPLETED

    def IsCompletedAndUnseen(self):
        return self.IsCompleted() and not self.hasBeenSeenAfterCompletion

    def MarkCompletionAnimationAsSeen(self):
        self.hasBeenSeenAfterCompletion = True


class LastActiveOperationInfo(object):

    def __init__(self, categoryID, operation, taskList):
        self.categoryID = categoryID
        self.operation = operation
        self.taskList = taskList
        self.operationID = operation.operationID if operation else None

    def __repr__(self):
        return 'LastActiveOperationInfo : %s ' % self.__dict__
