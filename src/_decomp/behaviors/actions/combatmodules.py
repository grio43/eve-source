#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\combatmodules.py
from random import randrange
from behaviors.utility.ballparks import is_ball_in_park, is_ship
from behaviors.utility.item_modules import has_fitted_from_type_list
from ccpProfile import TimedFunction
from collections import defaultdict
import uthread2
from behaviors.tasks import Task
from behaviors.utility.dogmatic import try_activate_effect, can_activate_effect_on_target
from behaviors.utility.dogmatic import get_default_effect_id_for_type
from behaviors.utility.inventory import get_inventory_item, get_type_id_by_item_id
import logging
logger = logging.getLogger(__name__)

class ActivateModuleTypeOnTarget(Task):

    @TimedFunction('behaviors::actions::combatmodules::ActivateModuleTypeOnTarget::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        assigned_module_id = self._get_my_module()
        my_target_id = self._get_my_target()
        if my_target_id is None:
            return
        module_type_id = get_inventory_item(self, assigned_module_id).typeID
        effect_id = get_default_effect_id_for_type(self, module_type_id)
        if can_activate_effect_on_target(self, module_type_id, effect_id, my_target_id):
            self.SetStatusToSuccess()
            uthread2.start_tasklet(self._start_module_on_target, assigned_module_id, my_target_id)

    def _get_my_module(self):
        return self.GetLastBlackboardValue(self.attributes.moduleAddress)

    def _get_my_target(self):
        return self.GetLastBlackboardValue(self.attributes.targetAddress)

    def _start_module_on_target(self, module_id, my_target):
        cycles = self._get_cycles()
        try_activate_effect(self, None, self.attributes.repeats, target_id=my_target, module_id=module_id, cycles=cycles)

    def _get_cycles(self):
        min_cycles = max_cycles = 0
        if self.HasAttribute('min_cycles'):
            min_cycles = self.attributes.min_cycles
        if self.HasAttribute('max_cycles'):
            max_cycles = self.attributes.max_cycles
        return randrange(min_cycles, max_cycles)


class FindAndRegisterModule(Task):

    @TimedFunction('behaviors::actions::combatmodules::FindAndRegisterModule::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        registered_modules = self._get_registered_modules() or set()
        assigned_module_id = self._get_my_module(registered_modules)
        if assigned_module_id is None:
            logger.info('Behavior %s tried registering more modules of group %s than has fitted', self.behaviorTree.GetBehaviorId(), self.attributes.moduleTypeId)
            self.SetStatusToFailed()
            return
        self.SendBlackboardValue(self.attributes.moduleAddress, assigned_module_id)
        registered_modules.add(assigned_module_id)
        self.SendBlackboardValue(self.attributes.registeredModulesAddress, registered_modules)

    def _get_registered_modules(self):
        return self.GetLastBlackboardValue(self.attributes.registeredModulesAddress)

    def _get_my_module(self, registered_modules):
        fitted_modules = self._get_fitted_modules() or set()
        for module_id in fitted_modules.get(self.attributes.moduleTypeId, []):
            if self._is_module_available(module_id, registered_modules):
                return module_id

    def _get_fitted_modules(self):
        fitted_modules = defaultdict(set)
        for module_item_key in self._get_my_fitted_modules():
            if isinstance(module_item_key, tuple):
                module_item_id = module_item_key[0]
            else:
                module_item_id = module_item_key
            fitted_modules[get_type_id_by_item_id(self, module_item_id)].add(module_item_id)

        return fitted_modules

    def _get_my_fitted_modules(self):
        return self._get_dogma_item().GetFittedItems()

    def _get_dogma_item(self):
        return self.context.dogmaLM.dogmaItems.get(self.context.myItemId)

    def _is_module_available(self, module_id, registered_modules):
        return not registered_modules or module_id not in registered_modules


class FilterItemsWithModules(Task):

    @TimedFunction('behaviors::actions::combatmodules::FilterItemsWithModules::OnEnter')
    def OnEnter(self):
        self.SetStatusToSuccess()
        source_item_set = self.GetLastBlackboardValue(self.attributes.sourceItemSetAddress)
        target_item_set = set()
        if source_item_set:
            for item_id in source_item_set:
                if is_ball_in_park(self, item_id) and is_ship(self, item_id) and has_fitted_from_type_list(self, item_id, self.attributes.typeListId):
                    target_item_set.add(item_id)

        self.SendBlackboardValue(self.attributes.targetItemSetAddress, target_item_set)
