#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\battlefield.py
from behaviors.exceptions import BehaviorAuthoringException
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.awareness import get_spawn_pool_id, get_fleet_awareness_members_ids
from behaviors.utility.battlefield import get_npc_cost_by_group_id, get_player_cost_for_item_ids
from ccpProfile import TimedFunction
import logging
logger = logging.getLogger(__name__)

class IsFleetTypeEqualTo(Task):

    @TimedFunction('behaviors::conditions::battlefield::IsFleetTypeEqualTo::OnEnter')
    def OnEnter(self):
        fleet_type = self.GetLastBlackboardValue(self.attributes.fleetTypeToCounterAddress)
        is_equal = fleet_type == self.attributes.fleetType
        self.SetStatusToSuccessIfTrueElseToFailed(is_equal)


class IsAnyFleetMemberMemberAggressed(Task):

    @TimedFunction('behaviors::conditions::battlefield::IsAnyFleetMemberMemberAggressed::OnEnter')
    def OnEnter(self):
        member_ids = get_fleet_awareness_members_ids(self, get_spawn_pool_id(self))
        for member_id in member_ids:
            member_object_state = self.get_aggression_object_state(member_id)
            if member_object_state.IsAggressed():
                self.SetStatusToSuccess()
                return

        self.SetStatusToFailed()

    def get_aggression_object_state(self, member_id):
        return self.context.ballpark.dogmaLM.aggressionLM.GetObjectState(member_id)


class IsPlayerFleetRelativeStrengthToHigh(Task, GroupTaskMixin):

    @TimedFunction('behaviors::conditions::battlefield::IsPlayerFleetRelativeStrengthToHigh::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        relative_strength = self._get_relative_strength()
        if relative_strength > self.attributes.relativeStrengthThreshold:
            self.SetStatusToSuccess()

    def _get_relative_strength(self):
        spawn_table_id = self._get_spawn_table_id()
        if spawn_table_id is None:
            raise BehaviorAuthoringException('Behavior=%s is not spawned from spawn table and should not have IsPlayerFleetRelativeStrengthToHigh task assigned', self.behaviorTree.GetBehaviorId())
        npc_fleet_cost = self._get_npc_fleet_cost(spawn_table_id)
        player_fleet_cost = self._get_player_fleet_cost()
        return float(player_fleet_cost) / float(npc_fleet_cost)

    def _get_spawn_table_id(self):
        return getattr(self.context, 'mySpawnTableId', None)

    def _get_player_fleet_cost(self):
        item_ids = self._get_player_item_ids()
        return get_player_cost_for_item_ids(self, item_ids)

    def _get_player_item_ids(self):
        return self.GetLastBlackboardValue(self.attributes.playerItemIdsAddress)

    def _get_npc_fleet_cost(self, spawn_table_id):
        return get_npc_cost_by_group_id(self, self.context.myEntityGroupId, spawn_table_id)
