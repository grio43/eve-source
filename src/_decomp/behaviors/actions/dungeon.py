#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\dungeon.py
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
import logging
logger = logging.getLogger(__name__)

class SelectTeamMembersInRange(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        max_distance = self.GetLastBlackboardValue(self.attributes.maxDistanceAddress)
        reference_item_id = self.GetLastBlackboardValue(self.attributes.referenceItemIdAddress)
        groups_by_team = self.GetLastBlackboardValue(self.attributes.entityGroupsByTeamNameAddress)
        if not groups_by_team:
            logger.debug('cant find any groups by team')
            return
        team_name = self.GetLastBlackboardValue(self.attributes.teamNameAddress)
        group_ids = groups_by_team.get(team_name)
        if not group_ids:
            logger.debug('cant find any registered groups for team %s', team_name)
            return
        selected_ids = []
        group_manager = self.context.groupManager
        ballpark = self.context.ballpark
        for group_id in group_ids:
            group = group_manager.GetGroup(group_id)
            if group is None:
                continue
            group_member_ids = group.GetGroupMembers()
            for group_member_id in group_member_ids:
                distance = ballpark.GetSurfaceDist(reference_item_id, group_member_id)
                if distance <= max_distance:
                    selected_ids.append(group_member_id)

        self.SendBlackboardValue(self.attributes.selectedItemsAddress, selected_ids)
        if not selected_ids:
            logger.debug('cant find any members to select from team %s with in range', team_name)
            return
        self.SetStatusToSuccess()


class RegisterEntityGroupsByTeamName(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        team_name = self.GetLastBlackboardValue(self.attributes.teamNameAddress)
        entities_by_group = self.GetLastBlackboardValue(self.attributes.entityGroupsByTeamNameAddress) or {}
        group_ids_in_team = entities_by_group.get(team_name, set())
        group_id = self.context.myEntityGroupId
        if group_id not in group_ids_in_team:
            group_ids_in_team.add(group_id)
            entities_by_group[team_name] = group_ids_in_team
            self.SendBlackboardValue(self.attributes.entityGroupsByTeamNameAddress, entities_by_group)


class GetDungeonSpawnEntryPoint(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        spawn_id = self.GetLastBlackboardValue(self.attributes.dungeonSpawnIdAddress)
        if not spawn_id:
            logger.debug('Spawn ID not found in blackboard: %s', spawn_id)
            return
        if not self.context.keeper.DoesSpawnExist(spawn_id):
            logger.debug('Spawn %s does not exist', spawn_id)
            return
        spawn = self.context.keeper.GetSpawn(spawn_id)
        self.SendBlackboardValue(self.attributes.dungeonEntryCoordinatesAddress, spawn.entryPos)
        self.SetStatusToSuccess()


class SetContextDungeonSpawnId(Task):

    def OnEnter(self):
        spawn_id = self.GetLastBlackboardValue(self.attributes.dungeonSpawnIdAddress)
        self.context.myDungeonSpawnId = spawn_id
        self.ResetBlackboardAddressCache()
        self.SetStatusToSuccess()


class GetItemIdForDungeonObject(Task):

    def OnEnter(self):
        object_id = self.GetLastBlackboardValue(self.attributes.objectIdAddress)
        if not object_id:
            logger.debug('No object Id found to in blackboard for dungeon spawn %s', self.context.myDungeonSpawnId)
            self.SetStatusToFailed()
            return
        dungeon_spawn = self.context.keeper.GetSpawn(self.context.myDungeonSpawnId)
        item_id = self.context.keeper.GetItemIdForObject(dungeon_spawn, object_id)
        if not item_id:
            logger.debug('No item id found for object Id %s found in dungeon spawn %s', object_id, self.context.myDungeonSpawnId)
            self.SetStatusToFailed()
            return
        self.SendBlackboardValue(self.attributes.itemIdAddress, item_id)
        self.SetStatusToSuccess()
