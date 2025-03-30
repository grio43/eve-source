#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\module.py
import dogma.const
from eve.common.lib import appConst
import eve.common.script.sys.idCheckers as idCheckers
from .base import Event
gun_module_effects = (dogma.const.effectProjectileFired, dogma.const.effectTargetAttack)

class ActivateModule(Event):
    atom_id = 72
    __notifyevents__ = ['OnModuleActivated']

    def OnModuleActivated(self, item_id, effect_id):
        self.invoke(item_id=item_id, effect_id=effect_id)


class ActivateGunModule(Event):
    atom_id = 73
    __notifyevents__ = ['OnModuleActivated']

    def OnModuleActivated(self, item_id, effect_id):
        if effect_id in gun_module_effects:
            self.invoke(item_id=item_id)


class ActivateRepairModule(Event):
    atom_id = 74
    __notifyevents__ = ['OnModuleActivated']

    def OnModuleActivated(self, item_id, effect_id):
        if effect_id == dogma.const.effectArmorRepair:
            self.invoke(item_id=item_id)


class ModuleDeactivated(Event):
    atom_id = 253
    __notifyevents__ = ['ProcessShipEffect']

    def ProcessShipEffect(self, state_manager, effect_state):
        effect = state_manager.GetEffect(effect_state.itemID, effect_state.effectName)
        if not effect:
            return
        if self._validate_effect(effect, effect_state):
            self.invoke(item_id=effect_state.itemID)

    def _validate_effect(self, effect, effect_state):
        if bool(effect_state.start) or bool(effect_state.active):
            return False
        return effect.isDefault


class GunModuleDeactivated(ModuleDeactivated):
    atom_id = 254

    def _validate_effect(self, effect, effect_state):
        valid = super(GunModuleDeactivated, self)._validate_effect(effect, effect_state)
        if not valid:
            return False
        return effect.effectID in gun_module_effects


class ModuleFittingChanged(Event):
    atom_id = 75
    __notifyevents__ = ['OnItemChanged']

    def OnItemChanged(self, item, change, location):
        if appConst.ixFlag not in change:
            return
        if change[appConst.ixFlag] not in appConst.fittingFlags and item.flagID not in appConst.fittingFlags:
            return
        if not self._validate(item.flagID, item.categoryID):
            return
        self.invoke(item_id=item.itemID, flag_id=item.flagID, old_flag_id=change[appConst.ixFlag], type_id=item.typeID)

    def _validate(self, flag_id, category_id):
        return True


class ModuleFitted(ModuleFittingChanged):
    atom_id = 76

    def _validate(self, flag_id, category_id):
        if flag_id not in appConst.fittingFlags or not idCheckers.IsModule(category_id):
            return False
        return True


class ModuleUnfitted(ModuleFittingChanged):
    atom_id = 77

    def _validate(self, flag_id, category_id):
        if flag_id in appConst.fittingFlags or not idCheckers.IsModule(category_id):
            return False
        return True


class ModuleChargeLoaded(ModuleFittingChanged):
    atom_id = 78

    def _validate(self, flag_id, category_id):
        if flag_id not in appConst.fittingFlags or not idCheckers.IsCharge(category_id):
            return False
        return True


class ModuleChargeUnloaded(ModuleFittingChanged):
    atom_id = 79

    def _validate(self, flag_id, category_id):
        if flag_id in appConst.fittingFlags or not idCheckers.IsCharge(category_id):
            return False
        return True


class ModuleOnlineStatusChanged(Event):
    atom_id = 128
    __notifyevents__ = ['OnModuleOnlineChange']

    def OnModuleOnlineChange(self, item, old_value, new_value):
        self.invoke(item_id=item.itemID, is_online=bool(new_value))
