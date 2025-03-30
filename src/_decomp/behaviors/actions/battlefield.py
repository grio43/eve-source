#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\battlefield.py
from ballpark.entities.awareness.fleetmatching.player_fleet_report import convert_report_to_dict
from ballpark.fleets.fleet_types import FLEET_TYPE_SUPPORT, SUPPORTED_FLEET_TYPES, FLEET_TYPES_TO_COUNTER
from behaviors.tasks import Task
from behaviors.utility.context import get_extra_context
from behaviors.utility.owner import get_owner_id
from behaviors.utility.spawning import get_current_spawn_points, add_spawn_points
from behaviors.utility.threat import evaluate_target
from behaviors.utility.battlefield import generate_player_fleet_report, get_total_fleet_points, get_match_result
from ccpProfile import TimedFunction
from evemath import weighted_choice
from inventorycommon.const import categoryStructure
import logging
import mathext
import uthread2
THREAT_WINDOW_IN_SECONDS = 10
logger = logging.getLogger(__name__)
FULL_HEALTH = 1.0

class CalculateStructureSpawnPointMultiplier(Task):

    @TimedFunction('behaviors::actions::battlefield::CalculateStructureSpawnPointMultiplier::OnEnter')
    def OnEnter(self):
        if self.is_structure():
            multiplier = self._get_spawn_point_multiplier()
            self.SendBlackboardValue(self.attributes.spawnPointMultiplierAddress, multiplier)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def is_structure(self):
        return self.context.mySlimItem.categoryID == categoryStructure

    def _get_structure_health(self):
        structure = self.context.myBall
        if not structure.IsDamaged():
            return FULL_HEALTH
        elif structure.IsStateShieldVulnerable():
            return structure.GetShield()
        elif structure.IsStateArmorVulnerable():
            return structure.GetArmor()
        elif structure.IsStateHullVulnerable():
            return structure.GetHull()
        else:
            return FULL_HEALTH

    def _get_spawn_point_multiplier(self):
        health = self._get_structure_health()
        return self._get_multiplier_at(health)

    def _get_multiplier_at(self, health):
        min_val = self.attributes.minSpawnPointMultiplier
        max_val = self.attributes.maxSpawnPointMultiplier
        peak_health_fraction = self.attributes.peakHealthFraction
        multiplier = min_val + (max_val - min_val) * (FULL_HEALTH - health) ** 2 / (FULL_HEALTH - peak_health_fraction) ** 2
        return max(0.0, min(multiplier, max_val))


class SelectFleetToCounter(Task):

    @TimedFunction('behaviors::actions::battlefield::SelectFleetToCounter::OnEnter')
    def OnEnter(self):
        match_results = self.GetLastBlackboardValue(self.attributes.fleetMatchResultsAddress)
        if match_results:
            if len(match_results) > 1:
                weighted_results = self._get_weighted_results(match_results)
                match_result = weighted_choice(weighted_results)
                logger.debug('chose fleet_type %s from the weighted options %s', match_result['fleet_type'], weighted_results)
            else:
                match_result = match_results[0]
                logger.debug('chose fleet_type %s as it was the only option available', match_result['fleet_type'])
            self.SendBlackboardValue(self.attributes.fleetTypeToCounterAddress, match_result['fleet_type'])
            self.SetStatusToSuccess()
        else:
            logger.debug('No valid fleet type available to select from')
            self.SendBlackboardValue(self.attributes.fleetTypeToCounterAddress, None)
            self.SetStatusToSuccess()

    def _get_weighted_results(self, match_results):
        return [ (result, self._get_match_result_weight(result)) for result in match_results ]

    def _get_match_result_weight(self, result):
        threat = sum((self._get_threat(item_id) for item_id in result['item_ids']))
        return max(1, threat)

    def _get_threat(self, item_id):
        return evaluate_target(self.context.damageTracker, self.context.dogmaLM, item_id, THREAT_WINDOW_IN_SECONDS)


class AnalyzeBattlefieldFleetMatching(Task):

    def __init__(self, attributes = None):
        super(AnalyzeBattlefieldFleetMatching, self).__init__(attributes=attributes)
        self.is_analysing = False

    @TimedFunction('behaviors::actions::battlefield::AnalyzeBattlefieldFleetMatching::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        entity_group_id_by_fleet_type = self.get_entity_group_id_by_fleet_type_dict()
        spawn_pool_id = self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)
        spawn_table_id = self.GetLastBlackboardValue(self.attributes.spawnTableIdAddress)
        min_spawn_points = self.attributes.minimumSpawnPoints
        max_spawn_points = self.attributes.maximumSpawnPoints
        spawn_point_multiplier = self.GetLastBlackboardValue(self.attributes.spawnPointMultiplierAddress)
        if spawn_pool_id and spawn_pool_id and spawn_point_multiplier:
            self.start_analysis(entity_group_id_by_fleet_type, spawn_point_multiplier, spawn_pool_id, spawn_table_id, min_spawn_points, max_spawn_points)
            self.SetStatusToSuccess()

    def start_analysis(self, entity_group_id_by_fleet_type, spawn_point_multiplier, spawn_pool_id, spawn_table_id, min_spawn_points, max_spawn_points):
        uthread2.start_tasklet(self.analyze_battlefield_fleet_matching, spawn_pool_id, spawn_table_id, spawn_point_multiplier, entity_group_id_by_fleet_type, min_spawn_points, max_spawn_points)

    def get_entity_group_id_by_fleet_type_dict(self):
        entity_group_id_by_fleet_type = {}
        for fleet_type, entity_group_id_address in self.attributes.entityGroupIdAddressByFleetType.iteritems():
            if entity_group_id_address is None:
                continue
            entity_group_id = self.GetLastBlackboardValue(entity_group_id_address)
            if entity_group_id is None:
                continue
            entity_group_id_by_fleet_type[fleet_type] = entity_group_id

        return entity_group_id_by_fleet_type

    @TimedFunction('behaviors::actions::battlefield::AnalyzeBattlefieldFleetMatching::analyze_battlefield_fleet_matching')
    def analyze_battlefield_fleet_matching(self, spawn_pool_id, spawn_table_id, spawn_point_multiplier, entity_group_id_by_fleet_type, min_spawn_points, max_spawn_points):
        if self.is_analysing:
            logger.warning('analysis already in progress pool=%s table=%s multiplier=%s groups_by_fleet_type=%s min_amount=%s max_amount=%s', spawn_pool_id, spawn_table_id, spawn_point_multiplier, entity_group_id_by_fleet_type, min_spawn_points, max_spawn_points)
            return
        self.is_analysing = True
        try:
            self._analyze_battlefield_fleet_matching(spawn_pool_id, spawn_table_id, spawn_point_multiplier, entity_group_id_by_fleet_type, min_spawn_points, max_spawn_points)
        except:
            logger.exception('error while analyzing battle field')
        finally:
            self.is_analysing = False

    def _analyze_battlefield_fleet_matching(self, spawn_pool_id, spawn_table_id, spawn_point_multiplier, entity_group_id_by_fleet_type, min_spawn_points, max_spawn_points):
        player_report = generate_player_fleet_report(self, spawn_pool_id)
        spawn_point_difference = self.calculate_spawn_points_difference(player_report, spawn_point_multiplier, spawn_pool_id, spawn_table_id)
        self.assign_spawn_points(spawn_pool_id, spawn_point_difference, min_spawn_points, max_spawn_points)
        match_results = self.match_fleets(entity_group_id_by_fleet_type, player_report, spawn_point_multiplier, spawn_table_id)
        self.post_results(player_report, match_results)

    def post_results(self, player_report, match_results):
        self.SendBlackboardValue(self.attributes.playerFleetReportAddress, convert_report_to_dict(player_report))
        self.SendBlackboardValue(self.attributes.fleetMatchResultsAddress, match_results)

    @TimedFunction('behaviors::actions::battlefield::AnalyzeBattlefieldFleetMatching::match_fleets')
    def match_fleets(self, entity_group_id_by_fleet_type, player_report, spawn_point_multiplier, spawn_table_id):
        support_points = player_report.fleet_by_type[FLEET_TYPE_SUPPORT].fleet_cost
        supported_fleet_points = float(sum((r.fleet_cost for fleet_type, r in player_report.fleet_by_type.iteritems() if fleet_type in SUPPORTED_FLEET_TYPES)))
        match_results = []
        for fleet_type in FLEET_TYPES_TO_COUNTER:
            match_result = get_match_result(self, spawn_table_id, fleet_type, player_report, spawn_point_multiplier, support_points, supported_fleet_points, entity_group_id_by_fleet_type)
            if match_result['player_fleet_points'] > 0:
                match_results.append(match_result)

        return match_results

    @TimedFunction('behaviors::actions::battlefield::AnalyzeBattlefieldFleetMatching::calculate_spawn_points_difference')
    def calculate_spawn_points_difference(self, player_report, spawn_point_multiplier, spawn_pool_id, spawn_table_id):
        total_npc_fleet_cost = get_total_fleet_points(self, spawn_pool_id, spawn_table_id)
        fleet_cost_difference = player_report.total_fleet_cost * spawn_point_multiplier - total_npc_fleet_cost
        current_spawn_points = get_current_spawn_points(self, spawn_pool_id)
        spawn_point_difference = fleet_cost_difference - current_spawn_points
        logger.debug('assign_spawn_pool_points: total_npc_points=%s total_player_points=%s current_pool=%s differences=%s multiplier=%s', total_npc_fleet_cost, player_report.total_fleet_cost, current_spawn_points, spawn_point_difference, spawn_point_multiplier)
        return spawn_point_difference

    def assign_spawn_points(self, spawn_pool_id, requested_spawn_points, min_spawn_points, max_spawn_points):
        actual_spawn_points = mathext.clamp(requested_spawn_points, min_spawn_points, max_spawn_points)
        add_spawn_points(self, spawn_pool_id, actual_spawn_points)
        self.context.eventLogger.log_adding_spawn_points(get_owner_id(self), spawn_pool_id, requested_spawn_points, min_spawn_points, max_spawn_points, actual_spawn_points, get_extra_context(self))
