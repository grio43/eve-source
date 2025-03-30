#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\awareness.py
from ballpark.entities.awareness.enemy_cluster_generator import THREAT_TIME_WINDOW_SECONDS
from behaviors.blackboards.scopes import GetBlackboardIdFromScopeAndContext, GetBlackboardScopeFromAddress
from behaviors.const.combat import THREAT_MAX_DISTANCE_FROM_GUARD_OBJECT, FW_ATTACK_NONE
from behaviors.tasks import Task
from behaviors.utility.awareness import get_fleet_awareness, get_awareness_config
from behaviors.utility.ballparks import get_ball_positions, is_coordinate_in_range_of_ball, is_ball_in_park, is_ball_cloaked, get_ball_position
from behaviors.utility.dogmatic import get_dogma_lm
from behaviors.utility.owner import get_owner_id
from behaviors.utility.threat import get_damage_tracker, evaluate_target
from ccpProfile import TimedFunction
from evemath import weighted_choice, get_center_point, get_farthest_distance_from_point
import logging
logger = logging.getLogger(__name__)
MIN_CLUSTER_QUALITY = 0.1

class ClusterData(object):

    def __init__(self, item_ids, centroid, radius, threat):
        self.item_ids = item_ids
        self.centroid = centroid
        self.radius = radius
        self.quality = threat * self._calculate_cluster_quality()

    def _calculate_cluster_quality(self):
        cluster_radius_over_max_distance = self.radius / THREAT_MAX_DISTANCE_FROM_GUARD_OBJECT
        cluster_proportion = min(cluster_radius_over_max_distance, 1.0) / len(self.item_ids)
        return max(1.0 - cluster_proportion, MIN_CLUSTER_QUALITY)


class SendCentroidOfBallIds(Task):

    @TimedFunction('behaviors::actions::awareness::SendCentroidOfBallIds::OnEnter')
    def OnEnter(self):
        centroid = None
        ball_ids = self.GetLastBlackboardValue(self.attributes.ballIdListAddress)
        if ball_ids:
            position_list = get_ball_positions(self, ball_ids)
            try:
                centroid = get_center_point(position_list)
            except ValueError:
                logger.debug('No valid positions left in list with id %s', ball_ids)

        self.SendBlackboardValue(self.attributes.centroidPositionAddress, centroid)
        self.SetStatusToSuccess()


class ComputeCentroidAndRadiusOfItemIds(Task):

    @TimedFunction('behaviors::actions::awareness::ComputeCentroidAndRadiusOfItemIds::OnEnter')
    def OnEnter(self):
        centroid = None
        radius = None
        ball_ids = self.GetLastBlackboardValue(self.attributes.itemIdsAddress)
        if ball_ids:
            position_list = get_ball_positions(self, ball_ids)
            if position_list:
                centroid = get_center_point(position_list)
                radius = get_farthest_distance_from_point(centroid, position_list)
        self.SendBlackboardValue(self.attributes.centroidPositionAddress, centroid)
        self.SendBlackboardValue(self.attributes.radiusPositionAddress, radius)
        self.SetStatusToSuccess()


class InitializeGroupAwareness(Task):

    @TimedFunction('behaviors::actions::awareness::InitializeGroupAwareness::OnEnter')
    def OnEnter(self):
        manager = self.context.entityLocation.GetGroupAwarenessManager()
        member_collection_id = self.get_member_collection_id()
        if manager.is_registered(member_collection_id):
            logger.debug('Group %s already registered, ignoring.', member_collection_id)
            self.SetStatusToFailed()
        else:
            manager.register_group_awareness(member_collection_id, self.get_awareness_config())
            self.SetStatusToSuccess()

    def get_member_collection_id(self):
        return self.context.myEntityGroupId

    def get_awareness_config(self):
        config = get_awareness_config(self)
        config.standings_enabled = self.attributes.standingsEnabled
        config.react_to_disapproval = self.attributes.reactToDisapproval or False
        fwAttackMethod = self.attributes.fwAttackMethod
        if fwAttackMethod == FW_ATTACK_NONE:
            fwAttackMethod = None
        config.fw_attack_method = fwAttackMethod
        return config


class InitializeSpawnPoolFleetAwareness(InitializeGroupAwareness):

    def __init__(self, attributes = None):
        super(InitializeSpawnPoolFleetAwareness, self).__init__(attributes=attributes)
        self.spawn_pool_id = None

    @TimedFunction('behaviors::actions::awareness::InitializeSpawnPoolFleetAwareness::OnEnter')
    def OnEnter(self):
        self.spawn_pool_id = self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)
        get_owner_id(self)
        manager = self._get_awareness_manager()
        blackboard_scope = GetBlackboardScopeFromAddress(self.attributes.combatTargetsSetAddress)
        blackboard_id = GetBlackboardIdFromScopeAndContext(blackboard_scope, self.context)
        manager.register_spawn_pool_fleet_awareness(self.spawn_pool_id, get_owner_id(self), blackboard_id, self.behaviorTree.GetBehaviorId(), self.get_awareness_config())
        self.SetStatusToSuccess()

    def get_member_collection_id(self):
        return self.spawn_pool_id

    def _get_awareness_manager(self):
        return self.context.entityLocation.GetGroupAwarenessManager()

    def get_awareness_config(self):
        config = get_awareness_config(self)
        config.standings_enabled = False
        config.fw_attack_method = None
        return config


class AddMyItemIdToSpawnPoolFleetAwareness(Task):

    @TimedFunction('behaviors::actions::awareness::AddMyItemIdToSpawnPoolFleetAwareness::OnEnter')
    def OnEnter(self):
        spawn_pool_id = self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)
        manager = self._get_awareness_manager()
        awareness = manager.get_spawn_pool_fleet_awareness(spawn_pool_id)
        if awareness is None:
            logger.error('Unable to find a spawn pool fleet awareness instance for spawn pool %s', spawn_pool_id, self.attributes.spawnPoolIdAddress)
            self.SetStatusToFailed()
        else:
            member_collection = awareness.get_member_collection()
            member_collection.add_item_id(self.context.myItemId)
            self.SetStatusToSuccess()

    def _get_awareness_manager(self):
        return self.context.entityLocation.GetGroupAwarenessManager()


class InitializeEnemyClusterGeneration(Task):

    @TimedFunction('behaviors::actions::awareness::InitializeEnemyClusterGeneration::OnEnter')
    def OnEnter(self):
        spawn_pool_id = self.get_spawn_pool_id()
        group_awareness = get_fleet_awareness(self, spawn_pool_id)
        if group_awareness.get_enemy_cluster_generator() is None:
            group_awareness.enable_enemy_cluster_generator(get_dogma_lm(self), get_damage_tracker(self), self.attributes.updateIntervalSeconds, self.GetChannelFromAddress(self.attributes.enemyClustersAddress))
        self.SetStatusToSuccess()

    def get_awareness_manager(self):
        return self.context.entityLocation.GetGroupAwarenessManager()

    def get_spawn_pool_id(self):
        return self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)


class SelectClusterWeightedByThreat(Task):

    @TimedFunction('behaviors::actions::awareness::SelectClusterWeightedByThreat::OnEnter')
    def OnEnter(self):
        enemy_clusters = self.get_updated_enemy_clusters(self.get_enemy_clusters())
        cluster = None
        if enemy_clusters:
            cluster = self.select_cluster_weighted_by_threat(enemy_clusters)
        if cluster:
            self.SendBlackboardValue(self.attributes.clusterCentroidAddress, cluster.centroid)
            self.SendBlackboardValue(self.attributes.clusterRadiusAddress, cluster.radius)
            self.SendBlackboardValue(self.attributes.clusterItemIdsAddress, cluster.item_ids)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def select_cluster_weighted_by_threat(self, enemy_clusters):
        return weighted_choice([ (cluster, cluster.quality) for cluster in enemy_clusters ])

    def get_updated_enemy_clusters(self, enemy_clusters):
        updated_enemy_clusters = []
        for cluster in enemy_clusters:
            item_ids = {item_id for item_id in cluster['item_ids'] if is_ball_in_park(self, item_id) and not is_ball_cloaked(self, item_id)}
            if not item_ids:
                continue
            points = [ get_ball_position(self, ball_id) for ball_id in item_ids ]
            centroid = get_center_point(points)
            if not self._is_in_range(centroid):
                continue
            updated_cluster = ClusterData(item_ids, centroid, get_farthest_distance_from_point(centroid, points), self._get_cluster_threat(item_ids))
            updated_enemy_clusters.append(updated_cluster)

        return updated_enemy_clusters

    def get_enemy_clusters(self):
        return self.GetLastBlackboardValue(self.attributes.enemyClustersAddress)

    def _is_in_range(self, cluster_coordinates):
        guard_object_id = self._get_guard_object_id()
        if guard_object_id is None:
            return True
        return is_coordinate_in_range_of_ball(self, guard_object_id, cluster_coordinates, THREAT_MAX_DISTANCE_FROM_GUARD_OBJECT)

    def _get_guard_object_id(self):
        if not self.HasAttribute('guardObjectIdAddress'):
            return
        guard_object_id = self.GetLastBlackboardValue(self.attributes.guardObjectIdAddress)
        if guard_object_id is None:
            return
        if not is_ball_in_park(self, guard_object_id):
            return
        return guard_object_id

    @TimedFunction('behaviors::actions::awareness::SelectClusterWeightedByThreat::_update_cluster_threat')
    def _get_cluster_threat(self, item_ids):
        return sum((self._get_item_threat(item_id) for item_id in item_ids))

    def _get_item_threat(self, item_id):
        return evaluate_target(self.context.damageTracker, self.context.dogmaLM, item_id, THREAT_TIME_WINDOW_SECONDS)
