#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\hardpointUtil.py
import dogma.const as dogmaConst
import inventorycommon.const as invConst
from inventorycommon.util import IsShipFittingFlag

def num_turret_hard_points(dogma_static_mgr, ship_type_id):
    return int(dogma_static_mgr.GetTypeAttribute2(typeID=ship_type_id, attributeID=dogmaConst.attributeTurretSlotsLeft))


def num_launcher_hard_points(dogma_static_mgr, ship_type_id):
    return int(dogma_static_mgr.GetTypeAttribute2(typeID=ship_type_id, attributeID=dogmaConst.attributeLauncherSlotsLeft))


def can_fit_turrets(dogma_static_mgr, ship_type_id):
    total_turret_slots = num_turret_hard_points(dogma_static_mgr=dogma_static_mgr, ship_type_id=ship_type_id)
    return total_turret_slots > 0


def can_fit_launchers(dogma_static_mgr, ship_type_id):
    total_launcher_slots = num_launcher_hard_points(dogma_static_mgr=dogma_static_mgr, ship_type_id=ship_type_id)
    return total_launcher_slots > 0


def get_ship_slots(dogma_location, ship_id):
    module_slots = [ slot_id for slot_id in invConst.moduleSlotFlags if dogma_location.SlotExists(ship_id, slot_id) ]
    rig_slots = [ slot_id for slot_id in invConst.rigSlotFlags if dogma_location.SlotExists(ship_id, slot_id) ]
    return module_slots + rig_slots


def get_all_slots_and_modules(dogma_location, ship_id):
    ship_item = dogma_location.dogmaItems[ship_id]
    ship_fitted_modules = ship_item.GetFittedItems().values()
    dogma_static_mgr = dogma_location.dogmaStaticMgr
    modules_in_slots = {slot_id:{} for slot_id in get_ship_slots(dogma_location, ship_id)}
    for module in ship_fitted_modules:
        if not IsShipFittingFlag(module.flagID):
            continue
        modules_in_slots[module.flagID] = {module.typeID: {dogmaConst.effectTurretFitted: False,
                         dogmaConst.effectLauncherFitted: False}}
        if is_launcher(dogma_static_mgr, module.typeID):
            modules_in_slots[module.flagID][module.typeID][dogmaConst.effectLauncherFitted] = True
        if is_turret(dogma_static_mgr, module.typeID):
            modules_in_slots[module.flagID][module.typeID][dogmaConst.effectTurretFitted] = True

    return modules_in_slots


def get_all_high_slots_and_modules(dogma_location, ship_id):
    slots_and_modules = get_all_slots_and_modules(dogma_location, ship_id)
    return {slot_id:module for slot_id, module in slots_and_modules.iteritems() if slot_id in invConst.hiSlotFlags}


def get_available_high_slots(dogma_location, ship_id):
    slots_and_modules = get_all_high_slots_and_modules(dogma_location, ship_id)
    result = []
    for slot_id, module in slots_and_modules.iteritems():
        if not module:
            result.append(slot_id)

    return result


def get_fitted_hard_point_slots_and_modules(dogma_location, ship_id, effect_id):
    slot_module_layout = get_all_high_slots_and_modules(dogma_location, ship_id)
    slots_and_modules = {}
    for slot_id, module in slot_module_layout.iteritems():
        if not module:
            continue
        module_type_id = module.keys()[0]
        if module[module_type_id][effect_id]:
            slots_and_modules[slot_id] = module_type_id

    return slots_and_modules


def get_fitted_launcher_slots_and_modules(dogma_location, ship_id):
    return get_fitted_hard_point_slots_and_modules(dogma_location, ship_id, dogmaConst.effectLauncherFitted)


def get_fitted_turret_slots_and_modules(dogma_location, ship_id):
    return get_fitted_hard_point_slots_and_modules(dogma_location, ship_id, dogmaConst.effectTurretFitted)


def num_available_launcher_hard_points(dogma_location, ship_id):
    total_launcher_hard_points = num_launcher_hard_points(dogma_static_mgr=dogma_location.dogmaStaticMgr, ship_type_id=dogma_location.dogmaItems[ship_id].typeID)
    used_launcher_hard_points = len(get_fitted_launcher_slots_and_modules(dogma_location, ship_id))
    return total_launcher_hard_points - used_launcher_hard_points


def get_available_launcher_slots(dogma_location, ship_id):
    if not num_available_launcher_hard_points(dogma_location, ship_id):
        return []
    return get_available_high_slots(dogma_location=dogma_location, ship_id=ship_id)


def num_available_turret_hard_points(dogma_location, ship_id):
    total_turret_hard_points = num_turret_hard_points(dogma_static_mgr=dogma_location.dogmaStaticMgr, ship_type_id=dogma_location.dogmaItems[ship_id].typeID)
    used_turret_hard_points = len(get_fitted_turret_slots_and_modules(dogma_location=dogma_location, ship_id=ship_id))
    return total_turret_hard_points - used_turret_hard_points


def get_available_turret_slots(dogma_location, ship_id):
    if not num_available_turret_hard_points(dogma_location, ship_id):
        return []
    return get_available_high_slots(dogma_location=dogma_location, ship_id=ship_id)


def is_hard_point(dogma_static_mgr, module_type_id, effect_id):
    return dogma_static_mgr.TypeHasEffect(module_type_id, effect_id)


def is_launcher(dogma_static_mgr, module_type_id):
    return is_hard_point(dogma_static_mgr, module_type_id, dogmaConst.effectLauncherFitted)


def is_turret(dogma_static_mgr, module_type_id):
    return is_hard_point(dogma_static_mgr, module_type_id, dogmaConst.effectTurretFitted)


def is_not_hard_point_module(dogma_static_mgr, module_type_id):
    return not is_launcher(dogma_static_mgr, module_type_id) and not is_turret(dogma_static_mgr, module_type_id)


def has_ship_any_hard_point_slot(dogma_static_mgr, module_type_id, ship_type_id):
    if is_launcher(dogma_static_mgr, module_type_id):
        return can_fit_launchers(dogma_static_mgr, ship_type_id)
    if is_turret(dogma_static_mgr, module_type_id):
        return can_fit_turrets(dogma_static_mgr, ship_type_id)
    return True


def has_ship_free_hard_point_for_module(dogma_location, module_type_id, ship_id):
    if is_launcher(dogma_location.dogmaStaticMgr, module_type_id):
        return bool(num_available_launcher_hard_points(dogma_location, ship_id))
    if is_turret(dogma_location.dogmaStaticMgr, module_type_id):
        return bool(num_available_turret_hard_points(dogma_location, ship_id))
    return True
