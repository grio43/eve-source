#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\group.py
from collections import defaultdict
import uthread2
from behaviors.blackboards import BlackboardDeletedError
from behaviors.const.behaviorroles import COMBAT_ROLES
from behaviors.const.combat import COMBAT_MAX_EFFECTIVE_FALLOFF_DISTANCE_FACTOR
from behaviors.const.combat import COMBAT_MIN_EFFECTIVE_COMBAT_RANGE_FACTOR
from behaviors.const.loot import EXTRA_LOOT_TABLES_BY_OWNER_ID_AND_ENTITY_GROUP_ID
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.trees.combat import ROLE_ADDRESS, COMBAT_ORBIT_RANGE, COMBAT_WARP_AT_DISTANCE
from behaviors.utility.ballparks import get_ship_balls_in_bubble, get_distance_between, get_ball, is_target_valid, get_slim_item, is_ball_cloaked
from behaviors.utility.dogmatic import type_has_effect, get_entity_max_missile_range
from behaviors.utility.inventory import get_type_id_by_item_id
from ccpProfile import TimedFunction
from dogma.const import effectMissileLaunchingForEntity, effectTargetAttack
from dogma.effects.restricted.util import get_effect_range_with_falloff_multiplier
from lootutils.grouploot import AssignAdditionalLootToGroupEntities
from random import choice
import logging
logger = logging.getLogger(__name__)
UNSPAWN_GROUP_SLEEP_DELAY_SEC = 0.2

class UpdateMaxMemberCount(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::UpdateMaxMemberCount::OnEnter')
    def OnEnter(self):
        current_count = self.GetEntityGroup().Count()
        last_count = self.GetLastBlackboardValue(self.attributes.maxMemberCountAddress)
        if last_count is None:
            self.SendBlackboardValue(self.attributes.maxMemberCountAddress, current_count)
        elif current_count > last_count:
            self.SendBlackboardValue(self.attributes.maxMemberCountAddress, current_count)
        self.SetStatusToSuccess()


class UpdateCurrentMemberCount(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::UpdateCurrentMemberCount::OnEnter')
    def OnEnter(self):
        current_count = self.GetEntityGroup().Count()
        last_count = self.GetLastBlackboardValue(self.attributes.currentMemberCountAddress)
        if current_count != last_count:
            self.SendBlackboardValue(self.attributes.currentMemberCountAddress, current_count)
        self.SetStatusToSuccess()


class ChooseCommander(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::ChooseCommander::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        requiredRole = getattr(self.attributes, 'requiredCommanderRole', None)
        existingCommanderItemId = self.GetLastBlackboardValue(self.attributes.commanderAddress)
        chosenGroupMemberId = self._ChooseCommanderFromGroup(requiredRole, existingCommanderItemId)
        if chosenGroupMemberId == existingCommanderItemId:
            return
        self.SendBlackboardValue(self.attributes.commanderAddress, chosenGroupMemberId)
        if chosenGroupMemberId:
            self._ResetCommanderNavigationRangesAndBehaviorTree(chosenGroupMemberId)

    def _ChooseCommanderFromGroup(self, requiredRole, existingCommanderItemId):
        membersWithCombatRoles = self._GetMembersWithCombatRoles()
        self._RemoveInvalidCommanderRoles(membersWithCombatRoles)
        if not membersWithCombatRoles:
            return None
        if self._IsCurrentCommanderValid(requiredRole, existingCommanderItemId, membersWithCombatRoles):
            return existingCommanderItemId
        if requiredRole and requiredRole in membersWithCombatRoles:
            return choice(membersWithCombatRoles[requiredRole])
        randomRole = choice(membersWithCombatRoles.keys())
        return choice(membersWithCombatRoles[randomRole])

    def _RemoveInvalidCommanderRoles(self, membersWithCombatRoles):
        for invalidRole in self.attributes.invalidCommanderRoles:
            if invalidRole in membersWithCombatRoles:
                del membersWithCombatRoles[invalidRole]

    def _IsCurrentCommanderValid(self, requiredRole, existingCommanderItemId, membersWithCombatRoles):
        if not existingCommanderItemId or not self.context.ballpark.HasBall(existingCommanderItemId):
            return False
        if not self._IsCurrentCommanderRoleValid(requiredRole, existingCommanderItemId, membersWithCombatRoles):
            return False
        return True

    def _IsCurrentCommanderRoleValid(self, requiredRole, existingCommanderItemId, membersWithCombatRoles):
        if not requiredRole or requiredRole not in membersWithCombatRoles:
            return True
        try:
            commandersRole = self._GetRoleByGroupMemberId(existingCommanderItemId)
            if commandersRole == requiredRole:
                return True
        except BlackboardDeletedError:
            return False

        return False

    def _GetRoleByGroupMemberId(self, groupMemberId):
        _, channelAddressName = ROLE_ADDRESS
        return self.GetMessageChannelForItemId(groupMemberId, channelAddressName).GetLastMessageValue()

    def _GetMembersWithCombatRoles(self):
        membersWithCombatRoles = defaultdict(list)
        memberIds = self.GetMemberIdList()
        for groupMemberId in memberIds:
            try:
                memberRole = self._GetRoleByGroupMemberId(groupMemberId)
                if memberRole in COMBAT_ROLES:
                    membersWithCombatRoles[memberRole].append(groupMemberId)
            except BlackboardDeletedError:
                continue

        return membersWithCombatRoles

    def _ResetCommanderNavigationRangesAndBehaviorTree(self, chosenGroupMemberId):
        _, combatOrbitAddress = COMBAT_ORBIT_RANGE
        _, combatWarpAtDistanceAddress = COMBAT_WARP_AT_DISTANCE
        self.GetMessageChannelForItemId(chosenGroupMemberId, combatOrbitAddress).SendMessage(None)
        self.GetMessageChannelForItemId(chosenGroupMemberId, combatWarpAtDistanceAddress).SendMessage(None)
        commanderBehaviorTree = self.context.entityLocation.GetBehaviorTreeManager().GetEntryByKey(chosenGroupMemberId)
        commanderBehaviorTree.ResetTree()


class GetMemberList(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::GetMemberList::OnEnter')
    def OnEnter(self):
        member_id_list = self.GetMemberIdList()
        self.SendBlackboardValue(self.attributes.memberListAddress, member_id_list)
        self.SetStatusToSuccess()


class AssignExtraLootTableByOwnerIdAndEntityGroupId(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::AssignExtraLootTableByOwnerIdAndEntityGroupId::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        newExtraLoot = self._GetExtraLootDataByOwnerId()
        if not newExtraLoot:
            return
        extraLoot = self.GetLastBlackboardValue(self.attributes.additionalLootTablesAddress) or defaultdict(set)
        for entityGroupId, lootTableIds in newExtraLoot.iteritems():
            extraLoot[entityGroupId].update(lootTableIds)

        self.SendBlackboardValue(self.attributes.additionalLootTablesAddress, extraLoot)
        AssignAdditionalLootToGroupEntities(self.context.entityLocation, self.context.myEntityGroupId)

    def _GetExtraLootDataByOwnerId(self):
        return EXTRA_LOOT_TABLES_BY_OWNER_ID_AND_ENTITY_GROUP_ID.get(self.GetGroupOwnerId())


class UnspawnGroup(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::UnspawnGroup::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        uthread2.StartTasklet(self._UnspawnGroup)

    def _UnspawnGroup(self):
        uthread2.sleep(UNSPAWN_GROUP_SLEEP_DELAY_SEC)
        self.context.entityLocation.UnspawnBehaviorEntityGroupWithRespawnEnabled(self.context.myEntityGroupId)


class PostWeaponRangesForGroup(Task, GroupTaskMixin):

    @TimedFunction('behaviors::actions::group::PostWeaponRangesForGroup::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        max_effective_weapon_range = self._get_max_effective_weapon_range()
        self.SendBlackboardValue(self.attributes.maxEffectiveWeaponRangeAddress, max_effective_weapon_range)
        min_effective_weapon_range = max_effective_weapon_range * COMBAT_MIN_EFFECTIVE_COMBAT_RANGE_FACTOR
        self.SendBlackboardValue(self.attributes.minEffectiveWeaponRangeAddress, min_effective_weapon_range)

    def _get_max_effective_weapon_range(self):
        max_effective_weapon_range_for_group = []
        entities_to_consider = self._get_entities_to_consider()
        if not entities_to_consider:
            return 0
        for entity_id in entities_to_consider:
            entity_type_id = get_type_id_by_item_id(self, entity_id)
            if entity_type_id is None:
                continue
            max_effective_weapon_range_for_entity = self._get_max_effective_weapon_range_for_entity(entity_id, entity_type_id)
            if max_effective_weapon_range_for_entity == 0:
                continue
            max_effective_weapon_range_for_group.append(max_effective_weapon_range_for_entity)
            logger.debug('Behavior: max effective weaponRange for entityType=%s set to=%s', entity_type_id, max_effective_weapon_range_for_entity)

        if not max_effective_weapon_range_for_group:
            return 0
        max_effective_weapon_range_for_group.sort()
        return max_effective_weapon_range_for_group[len(max_effective_weapon_range_for_group) / 2]

    def _get_entities_to_consider(self):
        roles_to_consider = self._get_roles_to_consider()
        if not roles_to_consider:
            return self.GetMemberIdList()
        entities_by_role = self._get_entities_by_role()
        entities_to_consider = []
        if entities_by_role is None:
            logger.debug('Behavior: no entities by role posted yet for PostWeaponRangesForGroup, most likely pending initial spawns')
            return entities_to_consider
        for role in roles_to_consider:
            if role in entities_by_role:
                entities_to_consider.extend(entities_by_role[role])

        return entities_to_consider

    def _get_roles_to_consider(self):
        return self.attributes.rolesToConsider

    def _get_entities_by_role(self):
        return self.GetLastBlackboardValue(self.attributes.entitiesByRole)

    def _get_max_effective_weapon_range_for_entity(self, entity_id, entity_type_id):
        turret_range = self._get_max_effective_turret_range_for_entity(entity_id, entity_type_id)
        missile_range = self._get_max_effective_missile_range_for_entity(entity_type_id)
        if turret_range == 0 and missile_range == 0:
            return 0
        if missile_range == 0 or turret_range < missile_range:
            return turret_range
        return missile_range

    def _get_max_effective_turret_range_for_entity(self, entity_id, entity_type_id):
        if not type_has_effect(self, entity_type_id, effectTargetAttack):
            return 0
        return get_effect_range_with_falloff_multiplier(self.context.dogmaLM, effectTargetAttack, entity_id, COMBAT_MAX_EFFECTIVE_FALLOFF_DISTANCE_FACTOR)

    def _get_max_effective_missile_range_for_entity(self, entity_type_id):
        if not type_has_effect(self, entity_type_id, effectMissileLaunchingForEntity):
            return 0
        return get_entity_max_missile_range(self, entity_type_id)


class GetClosestPlayerBallToGroupLeader(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        closest_player_ball_id = self._get_closest_player_ball_id_to_group()
        self.SendBlackboardValue(self.attributes.ballIdAddress, closest_player_ball_id)

    def _get_closest_player_ball_id_to_group(self):
        selected_group_member_id = self._select_group_member()
        bubble_id = get_ball(self, selected_group_member_id).newBubbleId
        return self._get_closest_player_to_member(selected_group_member_id, bubble_id)

    def _get_closest_player_to_member(self, selected_group_member_id, bubble_id):
        closest_player_ball_id = None
        shortest_distance = None
        for player_ship_ball_id in get_ship_balls_in_bubble(self, bubble_id):
            if not is_target_valid(self, player_ship_ball_id):
                continue
            distance = get_distance_between(self, selected_group_member_id, player_ship_ball_id)
            if shortest_distance is None or distance < shortest_distance:
                closest_player_ball_id = player_ship_ball_id
                shortest_distance = distance

        return closest_player_ball_id

    def _select_group_member(self):
        if not self.HasAttribute('commanderAddress'):
            return self.GetMemberIdList()[0]
        commander_id = self.GetLastBlackboardValue(self.attributes.commanderAddress)
        return commander_id or self.GetMemberIdList()[0]


class IsAnyPlayerShipOnGridWithGroupMember(Task, GroupTaskMixin):

    def OnEnter(self):
        self.SetStatusToSuccess()
        bubbles = self.GetMemberBubbleSet()
        for bubble_id in bubbles:
            if self._bubble_contains_player(bubble_id):
                self.SendBlackboardValue(self.attributes.resultAddress, True)
                return

        self.SendBlackboardValue(self.attributes.resultAddress, False)

    def _is_target_valid(self, target_id):
        if target_id is None:
            return False
        slim_item = get_slim_item(self, target_id)
        if slim_item is None:
            return False
        if not self.attributes.includeCloaked and is_ball_cloaked(self, target_id):
            return False
        return True

    def _bubble_contains_player(self, bubble_id):
        for player_ship_ball_id in get_ship_balls_in_bubble(self, bubble_id):
            if self._is_target_valid(player_ship_ball_id):
                return True

        return False
