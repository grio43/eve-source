#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\resourcewars.py
import random
from behaviors.actions.combattargets import FindTarget
from behaviors.targetEvaluation import ThreatTargetEvaluator
from behaviors.utility.ballparks import get_slim_item, get_ball, is_ship
from behaviors.utility.inventory import get_cargo_used_fraction
from behaviors.utility.item_modules import has_fitted_from_type_list
from behaviors.utility.math import get_normalized_dict
from inventorycommon.const import groupNpcIndustrialCommand, groupMiningDrone
HAULER_GROUP_IDS = []

class ResourceWarsFindTarget(FindTarget):

    def OnEnter(self):
        super(ResourceWarsFindTarget, self).OnEnter()

    def SetTargetEvaluator(self):
        if not self.HasContextValue('targetEvaluator'):
            self.SetContextValue('targetEvaluator', ThreatTargetEvaluator(self.context, self.attributes))

    def PickTarget(self, target_list):
        target_evaluator = self.GetTargetEvaluator()
        weight_by_item_id = {item_id:target_evaluator.EvaluateTarget(item_id) for item_id in target_list}
        weight_by_item_id = get_normalized_dict(weight_by_item_id)
        cargo_fraction_by_hauler_item_id = {item_id:get_cargo_used_fraction(self, item_id) for item_id in target_list if self._is_hauler(item_id)}
        if self._should_prioritize_haulers(cargo_fraction_by_hauler_item_id):
            self._update_hauler_weights(weight_by_item_id, cargo_fraction_by_hauler_item_id)
        elif self._should_prioritize_miners():
            self._update_miner_weights(weight_by_item_id)
        sorted_target_ids = sorted(weight_by_item_id.keys(), key=lambda item_id: weight_by_item_id[item_id])
        return sorted_target_ids[-1]

    def _update_hauler_weights(self, weight_by_item_id, cargo_fraction_by_hauler_item_id):
        for item_id, cargo_fraction in cargo_fraction_by_hauler_item_id.iteritems():
            weight_by_item_id[item_id] += 1.0 + cargo_fraction

    def _is_hauler(self, item_id):
        return get_slim_item(self, item_id).groupID == groupNpcIndustrialCommand

    def _should_prioritize_haulers(self, cargo_fraction_by_hauler_item_id):
        if random.random() > self._get_chance_of_preferring_filling_haulers():
            return False
        cargo_full_fraction_threshold = self._get_cargo_full_fraction_threshold()
        return any((cargo_fraction >= cargo_full_fraction_threshold for cargo_fraction in cargo_fraction_by_hauler_item_id.itervalues()))

    def _should_prioritize_miners(self):
        return random.random() <= self._get_chance_of_preferring_miners()

    def _update_miner_weights(self, weight_by_item_id):
        mining_drone_operators = self._get_mining_drone_operators(weight_by_item_id)
        for item_id in weight_by_item_id:
            if self._is_miner(item_id) or item_id in mining_drone_operators:
                weight_by_item_id[item_id] += 2.0

    def _get_mining_drone_operators(self, weight_by_item_id):
        mining_drone_operators = set()
        for item_id in weight_by_item_id:
            slim_item = get_slim_item(self, item_id)
            if slim_item.groupID != groupMiningDrone:
                continue
            ball = get_ball(self, item_id)
            mining_drone_operators.add(ball.sourceID)

        return mining_drone_operators

    def _is_miner(self, item_id):
        return is_ship(self, item_id) and has_fitted_from_type_list(self, item_id, self.attributes.miningModuleTypeListID)

    def _get_chance_of_preferring_filling_haulers(self):
        return self.GetLastBlackboardValue(self.attributes.chanceOfPreferringFillingHaulersAddress)

    def _get_chance_of_preferring_miners(self):
        return self.GetLastBlackboardValue(self.attributes.chanceOfPreferringMinersAddress)

    def _get_cargo_full_fraction_threshold(self):
        return self.GetLastBlackboardValue(self.attributes.cargoFullFractionThresholdAddress)
