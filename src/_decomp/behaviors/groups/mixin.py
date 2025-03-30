#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\groups\mixin.py
from npcs.npccorporations import get_corporation_faction_id

class EntityGroupNotFound(Exception):
    pass


class GroupTaskMixin(object):
    context = None

    def GetEntityGroup(self):
        groupManager = self.context.entityLocation.GetGroupManager()
        return groupManager.GetGroup(self.context.myEntityGroupId)

    def GetMemberIdList(self):
        entityGroup = self.GetEntityGroup()
        return entityGroup.GetGroupMembers()

    def GetMemberBubbleSet(self):
        bubbleIdSet = set()
        destinyBalls = self.context.ballpark.balls
        for memberId in self.GetMemberIdList():
            try:
                bubbleIdSet.add(destinyBalls[memberId].newBubbleId)
            except KeyError:
                pass

        return bubbleIdSet

    def GetGroupMessenger(self):
        group = self.GetEntityGroup()
        if group is None:
            raise EntityGroupNotFound('Entity group %s was not found' % self.context.myEntityGroupId)
        messenger = group.GetMessenger()
        return messenger

    def IsMember(self, itemId):
        group = self.GetEntityGroup()
        return group.HasEntity(itemId)

    def GetGroupOwnerId(self):
        return self.GetEntityGroup().GetGroupOwnerId()

    def GetGroupFactionId(self):
        return get_corporation_faction_id(self.GetGroupOwnerId())
