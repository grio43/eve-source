#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\group.py
from ballpark.entities.entitygroup import INVALID_ID
from behaviors.blackboards.scopes import EntityGroupScope
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.entity_groups import is_entity_group_initial_spawning_complete
from ccpProfile import TimedFunction

class IsMemberInEntityGroup(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::group::IsMemberTypeIdPartOfGroup::OnEnter')
    def OnEnter(self):
        memberId = self.GetLastBlackboardValue(self.attributes.memberIdAddress)
        isMemberInGroup = memberId is not None and self.IsMember(memberId)
        self.SetStatusToSuccessIfTrueElseToFailed(isMemberInGroup)


class IsMemberTypeIdPartOfGroup(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::group::IsMemberTypeIdPartOfGroup::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        if self._IsAnyMemberOfGroupOfGivenType():
            self.SetStatusToSuccess()

    def _IsAnyMemberOfGroupOfGivenType(self):
        typeId = self.attributes.typeId
        if typeId is None:
            return False
        memberIds = self.GetMemberIdList()
        for itemId in memberIds:
            memberTypeId = self.context.ballpark.inventory2.GetItem(itemId).typeID
            if memberTypeId == typeId:
                return True

        return False


class IsOtherEntityGroupBlackboardValueTrue(Task):

    @TimedFunction('behaviors::conditions::group::IsOtherEntityGroupBlackboardValueTrue::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        memberId = self.GetLastBlackboardValue(self.attributes.memberIdAddress)
        groupId = self.context.groupManager.FindGroupIDForItemID(memberId)
        if groupId == INVALID_ID:
            return
        blackboard = self.context.blackboardManager.GetBlackboard(EntityGroupScope(groupId))
        value = blackboard.GetLastMessageValue(self.attributes.messageName)
        self.SetStatusToSuccessIfTrueElseToFailed(value)


class IsAnyGroupMemberAggressed(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::group::IsAnyGroupMemberAggressed::OnEnter')
    def OnEnter(self):
        for memberId in self.GetMemberIdList():
            memberObjectState = self.context.ballpark.dogmaLM.aggressionLM.GetObjectState(memberId)
            if memberObjectState.IsAggressed():
                self.SetStatusToSuccess()
                return

        self.SetStatusToFailed()


class IsGroupInitialSpawningComplete(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::group::IsGroupInitialSpawningComplete::OnEnter')
    def OnEnter(self):
        if is_entity_group_initial_spawning_complete(self, self.context.myEntityGroupId):
            self.SetStatusToSuccess()
            return
        self.SetStatusToFailed()
