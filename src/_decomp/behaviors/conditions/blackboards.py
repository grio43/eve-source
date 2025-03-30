#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\blackboards.py
from behaviors import status
from behaviors.blackboards import BlackboardDeletedError
from behaviors.blackboards.scopes import GetBlackboardIdFromScopeAndContext
from behaviors.tasks import Task
from carbon.common.lib.const import SEC
from ccpProfile import TimedFunction

class IsBlackboardValueNone(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueNone::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboardValue is None:
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus


class IsBlackboardValueNotNone(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueNotNone::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboardValue is None:
            self.status = status.TaskFailureStatus
        else:
            self.status = status.TaskSuccessStatus


class IsBlackboardValue3dVector(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueNotNone::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if type(blackboardValue) not in (list, tuple) or len(blackboardValue) != 3:
            self.status = status.TaskFailureStatus
        else:
            self.status = status.TaskSuccessStatus


class IsBlackboardValueTrue(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueTrue::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboardValue is True:
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus


class IsBlackboardValueFalse(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueTrue::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboardValue is False:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class IsBlackboardStringEqualToValue(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardStringEqualToValue::OnEnter')
    def OnEnter(self):
        blackboard_value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboard_value == self.attributes.expectedValue:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class BlackboardMessagesEqualCondition(Task):

    @TimedFunction('behaviors::condition::blackboards::BlackboardMessagesEqualCondition::OnEnter')
    def OnEnter(self):
        firstValue = self.GetLastBlackboardValue(self.attributes.firstMessageAddress)
        secondValue = self.GetLastBlackboardValue(self.attributes.secondMessageAddress)
        if firstValue == secondValue:
            self.status = status.TaskSuccessStatus
        else:
            self.status = status.TaskFailureStatus


class BlackboardValueUpdatedRecentlyCondition(Task):

    @TimedFunction('behaviors::condition::blackboards::BlackboardValueUpdatedRecentlyCondition::OnEnter')
    def OnEnter(self):
        messages = self.GetLastBlackboardValueWithMaxAge(self.attributes.address, maxAge=self.attributes.timeInSeconds * SEC)
        if messages:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class IsBlackboardValueInCollectionCondition(Task):

    @TimedFunction('behaviors::condition::blackboards::IsBlackboardValueInCollectionCondition::OnEnter')
    def OnEnter(self):
        value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        collection = self.GetLastBlackboardValue(self.attributes.collectionAddress)
        if collection and value in collection:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class BlackboardMessageAndMyItemIdEqualCondition(Task):

    @TimedFunction('behaviors::conditions::blackboards::BlackboardMessageEqualsContextCondition::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.messageAddress)
        result = self.IsEqual(blackboardValue)
        if getattr(self.attributes, 'isInverted', False):
            result = not result
        if result:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def IsEqual(self, blackboardValue):
        return blackboardValue == self.context.myItemId


class BlackboardMessageAndMyEntityGroupIdEqualCondition(BlackboardMessageAndMyItemIdEqualCondition):

    def IsEqual(self, blackboardValue):
        return blackboardValue == self.context.myEntityGroupId


class IsBlackboardIntegerEqualToValue(Task):

    @TimedFunction('behaviors::conditions::blackboards::IsBlackboardIntegerEqualToValue::OnEnter')
    def OnEnter(self):
        blackboardValue = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if blackboardValue == self.attributes.value:
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()


class IsBlackboardValueRatioLessThan(Task):

    @TimedFunction('behaviors::conditions::blackboards::IsBlackboardValueRatioLessThan::OnEnter')
    def OnEnter(self):
        firstValue = self.GetLastBlackboardValue(self.attributes.firstValueAddress)
        secondValue = self.GetLastBlackboardValue(self.attributes.secondValueAddress)
        if firstValue is None or secondValue is None:
            self.SetStatusToFailed()
            return
        ratioToCompare = self.GetLastBlackboardValue(self.attributes.ratioAddress)
        ratio = firstValue / float(secondValue)
        self.SetStatusToSuccessIfTrueElseToFailed(ratio < ratioToCompare)


class BlackboardValueEqualsBlackboardValueInDictionaryCondition(Task):

    @TimedFunction('behaviors::conditions::blackboards::BlackboardValueEqualsBlackboardValueInDictionaryCondition::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        expected_value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        blackboard_key = self.GetLastBlackboardValue(self.attributes.keyAddress)
        if expected_value is None or blackboard_key is None:
            return
        blackboard_dictionary = self.GetLastBlackboardValue(self.attributes.dictionaryAddress)
        if blackboard_dictionary is None:
            return
        if blackboard_key not in blackboard_dictionary:
            return
        if blackboard_dictionary[blackboard_key] != expected_value:
            return
        self.SetStatusToSuccess()


class IsBlackboardCollectionEmpty(Task):

    @TimedFunction('behaviors::conditions::blackboards::IsBlackboardCollectionEmpty::OnEnter')
    def OnEnter(self):
        collection = self.GetLastBlackboardValue(self.attributes.collectionAddress)
        self.SetStatusToSuccessIfTrueElseToFailed(collection is None or len(collection) == 0)


class IsBlackboardValueLessThenBlackboardValue(Task):

    @TimedFunction('behaviors::conditions::blackboards::IsBlackboardValueLessThenBlackboardValue::OnEnter')
    def OnEnter(self):
        blackboard_value_to_check = self.GetLastBlackboardValue(self.attributes.valueToCheckAddress)
        blackboard_value_to_compare = self.GetLastBlackboardValue(self.attributes.valueToCompareAddress)
        self.SetStatusToSuccessIfTrueElseToFailed(blackboard_value_to_check < blackboard_value_to_compare)


class IsBlackboardDeleted(Task):

    @TimedFunction('behaviors::conditions::blackboards::IsBlackboardDeleted::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        blackboardId = GetBlackboardIdFromScopeAndContext(self.attributes.scopeType, self.context)
        try:
            self.context.blackboardManager.GetBlackboard(blackboardId)
        except BlackboardDeletedError:
            self.SetStatusToSuccess()
