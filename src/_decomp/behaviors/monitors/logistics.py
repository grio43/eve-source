#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\logistics.py
from ballpark.messenger.const import MESSAGE_ON_EFFECT_STOPPED
from behaviors.groups.mixin import GroupTaskMixin
from behaviors.tasks import Task
from behaviors.utility.dogmatic import is_my_effect_active, get_my_locked_targets, try_activate_effect
from behaviors.utility.logistics import get_damage_state_function_by_effect_id, get_damage_state_modifier, get_base_logistics_priority
from evemath import weighted_choice
import logging
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)

class ManageRemoteRepairEffect(Task, GroupTaskMixin):

    @TimedFunction('behaviors::monitors::logistics::ManageRemoteRepairEffect::OnEnter')
    def OnEnter(self):
        self.repair_effect_id = self.GetLastBlackboardValue(self.attributes.repairEffectIdAddress)
        self._get_damage_state = get_damage_state_function_by_effect_id(self.repair_effect_id)
        if not is_my_effect_active(self, self.repair_effect_id):
            self._apply_effect_on_best_target()
        self._start_monitor_effect()
        self.SetStatusToSuccess()

    def CleanUp(self):
        self._stop_monitoring_effects()
        self.SetStatusToInvalid()

    def _start_monitor_effect(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_EFFECT_STOPPED, self._apply_effect_on_best_target_if_repair_effect)

    def _stop_monitoring_effects(self):
        self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_EFFECT_STOPPED, self._apply_effect_on_best_target_if_repair_effect)

    def _apply_effect_on_best_target_if_repair_effect(self, effect_id):
        if effect_id != self.repair_effect_id:
            return
        self._apply_effect_on_best_target()

    @TimedFunction('behaviors::monitors::logistics::ManageRemoteRepairEffect::_apply_effect_on_best_target')
    def _apply_effect_on_best_target(self):
        prioritized_watchlist = self.GetLastBlackboardValue(self.attributes.prioritizedWatchlistAddress)
        if not prioritized_watchlist:
            logger.debug('ManageRemoteRepairEffect: %s has no prioritized watchlist to work with', self.context.myItemId)
            return
        locked_target_ids = get_my_locked_targets(self)
        if not locked_target_ids:
            logger.debug('ManageRemoteRepairEffect: %s has no locked targets to work with', self.context.myItemId)
            return
        candidates = self._generate_candidates(locked_target_ids, prioritized_watchlist)
        if not candidates:
            logger.debug('ManageRemoteRepairEffect: %s found no suitable candidates', self.context.myItemId)
            return
        item_id = weighted_choice(candidates)
        try_activate_effect(self, self.repair_effect_id, 0, target_id=item_id)
        logger.debug('ManageRemoteRepairEffect: %s activated effect %s on %s', self.context.myItemId, self.repair_effect_id, item_id)

    @TimedFunction('behaviors::monitors::logistics::ManageRemoteRepairEffect::_generate_candidates')
    def _generate_candidates(self, locked_target_ids, prioritized_watchlist):
        candidates = []
        for priority, item_id in prioritized_watchlist:
            if item_id in locked_target_ids:
                weight = get_damage_state_modifier(self, item_id, self._get_damage_state)
                if weight > 0.0:
                    weight += get_base_logistics_priority(self, item_id)
                    candidates.append((item_id, weight))

        return candidates
