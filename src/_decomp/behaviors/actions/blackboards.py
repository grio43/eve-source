#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\blackboards.py
from copy import copy
from behaviors.blackboards.scopes import GetBlackboardChannelNameFromAddress
from behaviors.blackboards.scopes import GetBlackboardScopeFromAddress
from behaviors.blackboards.scopes import Scope
from behaviors.tasks import Task
from ccpProfile import TimedFunction
from collections import defaultdict

class BlackboardSendMyItemIdMessageAction(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardContextMessageAction::OnEnter')
    def OnEnter(self):
        self.SendBlackboardValue(self.attributes.messageAddress, self.GetContextValue())
        self.SetStatusToSuccess()

    def GetContextValue(self):
        return self.context.myItemId


class BlackboardSendMyEntityGroupIdMessageAction(BlackboardSendMyItemIdMessageAction):

    def GetContextValue(self):
        return self.context.myEntityGroupId


class BlackboardCopyMessageAction(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardCopyMessageAction::OnEnter')
    def OnEnter(self):
        source = self._get_source_message()
        self.SendBlackboardValue(self.attributes.targetMessageAddress, copy(source))
        self.SetStatusToSuccess()

    def _get_source_message(self):
        return self.GetLastBlackboardValue(self.attributes.sourceMessageAddress)


class BlackboardSetMessageAsNoneAction(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardSetMessageAsNoneAction::OnEnter')
    def OnEnter(self):
        self.SendBlackboardValue(self.attributes.messageAddress, self.GetValue())
        self.SetStatusToSuccess()

    def GetValue(self):
        return None


class BlackboardSetMessageToBooleanValueAction(BlackboardSetMessageAsNoneAction):

    def GetValue(self):
        return self.attributes.value


class BlackboardSetMessageToIntegerValueAction(BlackboardSetMessageAsNoneAction):

    def GetValue(self):
        return self.attributes.value


class BlackboardSetMessageToFloatValueAction(BlackboardSetMessageAsNoneAction):

    def GetValue(self):
        return self.attributes.value


class BlackboardSetMessageToStringValueAction(BlackboardSetMessageAsNoneAction):

    def GetValue(self):
        return self.attributes.value


class BlackboardSendItemBubbleIdMessage(Task):

    def OnEnter(self):
        itemId = self.GetLastBlackboardValue(self.attributes.itemIdSourceAddress)
        ball = self.context.ballpark.balls.get(itemId, None)
        if ball is None:
            self.SetStatusToFailed()
        else:
            self.SendBlackboardValue(self.attributes.bubbleIdTargetAddress, ball.newBubbleId)
            self.SetStatusToSuccess()


class BlackboardIncrementCounter(Task):

    def OnEnter(self):
        counter = self.GetLastBlackboardValue(self.attributes.counterAddress) or 0
        self.SendBlackboardValue(self.attributes.counterAddress, counter + 1)
        self.SetStatusToSuccess()


class BlackboardDecrementCounter(Task):

    def OnEnter(self):
        counter = self.GetLastBlackboardValue(self.attributes.counterAddress) or 0
        self.SendBlackboardValue(self.attributes.counterAddress, counter - 1)
        self.SetStatusToSuccess()


class BlackboardAddNumericValues(Task):

    def OnEnter(self):
        first_value = self.GetLastBlackboardValue(self.attributes.firstValueAddress) or 0
        second_value = self.GetLastBlackboardValue(self.attributes.secondValueAddress) or 0
        result_value = first_value + second_value
        self.SendBlackboardValue(self.attributes.resultValueAddress, result_value)
        self.SetStatusToSuccess()


class BlackboardMergeCollectionsIntoSet(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        firstCollection = set(self.GetLastBlackboardValue(self.attributes.firstCollectionAddress) or [])
        secondCollection = set(self.GetLastBlackboardValue(self.attributes.secondCollectionAddress) or [])
        resultSet = firstCollection.union(secondCollection)
        self.SendBlackboardValue(self.attributes.resultSetAddress, resultSet)


class BlackboardRemoveCollectionFromSet(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        collection = set(self.GetLastBlackboardValue(self.attributes.collectionAddress) or [])
        targetSet = self.GetLastBlackboardValue(self.attributes.targetSetAddress) or set()
        resultSet = targetSet.difference(collection)
        self.SendBlackboardValue(self.attributes.targetSetAddress, resultSet)


class BlackboardSetBooleanFlags(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardSetBooleanFlags::OnEnter')
    def OnEnter(self):
        for address in self.attributes.flagAddressList:
            self.SendBlackboardValue(address, True)

        self.SetStatusToSuccess()


class BlackboardClearBooleanFlags(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardClearBooleanFlags::OnEnter')
    def OnEnter(self):
        for address in self.attributes.flagAddressList:
            self.SendBlackboardValue(address, False)

        self.SetStatusToSuccess()


class BlackboardAddBlackboardValueIntoBlackboardCollection(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardAddBlackboardValueIntoBlackboardCollection::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        blackboard_value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        if not self._is_blackboard_value_valid(blackboard_value):
            return
        blackboard_collection = set(self.GetLastBlackboardValue(self.attributes.collectionAddress) or [])
        if blackboard_value in blackboard_collection:
            return
        blackboard_collection.add(blackboard_value)
        self.SendBlackboardValue(self.attributes.collectionAddress, blackboard_collection)

    def _is_blackboard_value_valid(self, blackboard_value):
        return not (blackboard_value is None or blackboard_value == '')


class BlackboardAddValueByKeyIntoBlackboardDictionary(Task):

    @TimedFunction('behaviors::actions::blackboards::BlackboardAddValueByKeyIntoBlackboardDictionary::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        blackboard_key = self._get_blackboard_key()
        if not self._is_blackboard_entry_valid(blackboard_key):
            return
        blackboard_value = self._get_blackboard_value()
        if not self._is_blackboard_entry_valid(blackboard_value):
            return
        self._update_blackboard_dictionary(blackboard_key, blackboard_value)

    def _get_blackboard_key(self):
        return self.GetLastBlackboardValue(self.attributes.keyAddress)

    def _is_blackboard_entry_valid(self, blackboard_entry):
        return not (blackboard_entry is None or blackboard_entry == '')

    def _get_blackboard_value(self):
        return self.GetLastBlackboardValue(self.attributes.valueAddress)

    def _update_blackboard_dictionary(self, blackboard_key, blackboard_value):
        blackboard_dictionary = self.GetLastBlackboardValue(self.attributes.dictionaryAddress) or defaultdict(set)
        if blackboard_value in blackboard_dictionary[blackboard_key]:
            return
        blackboard_dictionary[blackboard_key].add(blackboard_value)
        self.SendBlackboardValue(self.attributes.dictionaryAddress, blackboard_dictionary)


class BlackboardSetValueByKeyInBlackboardDictionary(BlackboardAddValueByKeyIntoBlackboardDictionary):

    def _update_blackboard_dictionary(self, blackboard_key, blackboard_value):
        blackboard_dictionary = self.GetLastBlackboardValue(self.attributes.dictionaryAddress) or {}
        if blackboard_key in blackboard_dictionary and blackboard_dictionary[blackboard_key] == blackboard_value:
            return
        blackboard_dictionary[blackboard_key] = blackboard_value
        self.SendBlackboardValue(self.attributes.dictionaryAddress, blackboard_dictionary)


class BlackboardSetValueBySelfTypeInBlackboardDictionary(BlackboardSetValueByKeyInBlackboardDictionary):

    def _get_blackboard_key(self):
        return self.context.mySlimItem.typeID


class BlackboardAddSelfByKeyIntoBlackboardDictionary(BlackboardAddValueByKeyIntoBlackboardDictionary):

    def _get_blackboard_value(self):
        return self.context.myItemId


class BlackboardAddValueBySelfIntoBlackboardDictionary(BlackboardAddValueByKeyIntoBlackboardDictionary):

    def _get_blackboard_key(self):
        return self.context.myItemId


class BlackboardRemoveValueByKeyFromBlackboardDictionary(BlackboardAddValueByKeyIntoBlackboardDictionary):

    def _is_blackboard_key_valid(self, blackboard_key):
        return not (blackboard_key is None or blackboard_key == '')

    def _get_blackboard_value(self):
        return self.GetLastBlackboardValue(self.attributes.valueAddress)

    def _update_blackboard_dictionary(self, blackboard_key, blackboard_value):
        blackboard_dictionary = self.GetLastBlackboardValue(self.attributes.dictionaryAddress) or defaultdict(set)
        if not blackboard_dictionary or blackboard_value not in blackboard_dictionary[blackboard_key]:
            return
        blackboard_dictionary[blackboard_key].remove(blackboard_value)
        self.SendBlackboardValue(self.attributes.dictionaryAddress, blackboard_dictionary)


class BlackboardCopyValueBySelfTypeFromBlackboardDictionary(BlackboardCopyMessageAction):

    def _get_source_message(self):
        dictionary_message = self.GetLastBlackboardValue(self.attributes.sourceMessageAddress)
        if dictionary_message is None:
            return
        return dictionary_message.get(self.context.mySlimItem.typeID)


class BlackboardSetBooleanFlagsOnGroupRemoval(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        if self._is_already_set():
            return
        self._set_boolean_flag_on_group_removal()

    def _is_already_set(self):
        return self.GetLastBlackboardValue(self.attributes.oneShotAddress) is True

    def _set_boolean_flag_on_group_removal(self):
        for message_address in self.attributes.messageAddressList:
            channel = self.GetChannelFromAddress(message_address)
            self.context.groupManager.AddGroupRemovalHandler(self.context.myEntityGroupId, channel.SendMessage, (self.attributes.value,))

        self.SendBlackboardValue(self.attributes.oneShotAddress, True)


class BlackboardSetDictionaryValueByMyGroupId(BlackboardSetValueByKeyInBlackboardDictionary):

    def _get_blackboard_key(self):
        return self.context.myEntityGroupId


class BroadcastBlackboardValueToBlackboards(Task):

    def OnEnter(self):
        self.SetStatusToSuccess()
        object_ids = self.GetLastBlackboardValue(self.attributes.objectIdsAddress)
        if not object_ids:
            return
        value = self.GetLastBlackboardValue(self.attributes.valueAddress)
        scope_type = GetBlackboardScopeFromAddress(self.attributes.targetAddress)
        channel_name = GetBlackboardChannelNameFromAddress(self.attributes.targetAddress)
        blackboard_manager = self.context.blackboardManager
        for object_id in object_ids:
            blackboard_id = Scope(scope_type, object_id)
            if not blackboard_manager.HasBlackboard(blackboard_id):
                blackboard = blackboard_manager.GetBlackboard(blackboard_id)
                blackboard.SendMessage(channel_name, value)
