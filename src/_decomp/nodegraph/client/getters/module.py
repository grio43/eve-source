#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\module.py
from .base import GetterAtom
from collections import Iterable
from dogma.const import effectTurretFitted, effectLauncherFitted
from eve.common.script.sys.idCheckers import IsCharge
import evetypes
from inventorycommon.const import moduleSlotFlags
from nodegraph.common.util import get_object_predicate, get_object_in_list_predicate

class GetModule(GetterAtom):
    atom_id = None

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, type_list_id = None, required_attribute = None):
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id
        self.type_list_id = type_list_id
        self.required_attribute = required_attribute

    def _get_fitted_items(self):
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        ship_item = dogma_location.GetShipItem()
        if not ship_item:
            return {}
        return dogma_location.GetFittedItemsToShip()

    def _get_condition_checks(self):
        return []

    def _get_predicate(self):

        def predicate(item):
            checks = []
            if self.item_id:
                checks.append(get_object_predicate('itemID', self.item_id))
            elif self.type_id:
                checks.append(get_object_predicate('typeID', self.type_id))
            elif self.group_id:
                checks.append(get_object_predicate('groupID', self.group_id))
            elif self.category_id:
                checks.append(get_object_predicate('categoryID', self.category_id))
            elif self.type_list_id:
                valid_types = evetypes.GetTypeIDsByListID(self.type_list_id)
                checks.append(get_object_in_list_predicate('typeID', valid_types))
            if self.required_attribute:
                checks.append(self._has_attribute)
            checks += self._get_condition_checks()
            return all([ check(item) for check in checks ])

        return predicate

    def _has_attribute(self, item):
        return self.required_attribute in item.attributes

    def _get_item_data(self, item):
        item_id = slot_id = type_id = group_id = None
        if item:
            item_id = item.itemID
            if isinstance(item_id, Iterable):
                item_id = iter(item_id).next()
            slot_id = item.flagID
            type_id = item.typeID
            group_id = evetypes.GetGroupID(type_id)
        return {'item': item,
         'item_id': item_id,
         'slot_id': slot_id,
         'type_id': type_id,
         'group_id': group_id}

    def get_values(self):
        predicate = self._get_predicate()
        fitted_items = self._get_fitted_items()
        for item in fitted_items.itervalues():
            if predicate(item):
                return self._get_item_data(item)

        return self._get_item_data(None)


class GetFittedModule(GetModule):
    atom_id = 319

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, type_list_id = None, required_attribute = None, only_slots = None, only_weapons = None, only_turrets = None, only_launchers = None, only_online = None, exclude_charges = None, **kwargs):
        super(GetFittedModule, self).__init__(item_id, type_id, group_id, category_id, type_list_id, required_attribute)
        self.only_slots = self.get_atom_parameter_value('only_slots', only_slots)
        self.only_weapons = self.get_atom_parameter_value('only_weapons', only_weapons)
        self.only_turrets = self.get_atom_parameter_value('only_turrets', only_turrets)
        self.only_launchers = self.get_atom_parameter_value('only_launchers', only_launchers)
        self.only_online = self.get_atom_parameter_value('only_online', only_online)
        self.exclude_charges = self.get_atom_parameter_value('exclude_charges', exclude_charges)

    def _is_turret(self, item):
        return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(item.typeID, effectTurretFitted)

    def _is_launcher(self, item):
        return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(item.typeID, effectLauncherFitted)

    def _is_online(self, item):
        return item.IsOnline()

    def _is_not_charge(self, item):
        return not IsCharge(item.categoryID)

    def _get_condition_checks(self):
        checks = []
        if self.only_slots:
            checks.append(get_object_in_list_predicate('flagID', moduleSlotFlags))
        if self.only_weapons:
            weapon_module_types = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_WEAPON_MODULES)
            checks.append(get_object_in_list_predicate('typeID', weapon_module_types))
        if self.only_turrets:
            checks.append(self._is_turret)
        if self.only_launchers:
            checks.append(self._is_launcher)
        if self.only_online:
            checks.append(self._is_online)
        if self.exclude_charges:
            checks.append(self._is_not_charge)
        return checks

    @classmethod
    def get_subtitle(cls, item_id = None, type_id = None, group_id = None, category_id = None, only_slots = None, only_weapons = None, only_turrets = None, only_launchers = None, only_online = None, exclude_charges = None, **kwargs):
        if item_id:
            return 'Item {item_id}'.format(item_id=item_id)
        if type_id:
            return evetypes.GetName(type_id)
        if group_id:
            return evetypes.GetGroupNameByGroup(group_id)
        if category_id:
            return evetypes.GetCategoryNameByCategory(category_id)
        tags = []
        if only_slots:
            tags.append('Slots')
        if only_weapons:
            tags.append('Weapons')
        if only_turrets:
            tags.append('Turrets')
        if only_launchers:
            tags.append('Launchers')
        if only_online:
            tags.append('Online')
        if exclude_charges:
            tags.append('No charges')
        return ', '.join(tags)


class GetFittedModules(GetFittedModule):
    atom_id = 389

    def get_values(self):
        fitted_modules = []
        predicate = self._get_predicate()
        fitted_items = self._get_fitted_items()
        for item in fitted_items.itervalues():
            if predicate(item):
                fitted_modules.append(item)

        return {'fitted_modules': fitted_modules}


class GetCharges(GetModule):
    atom_id = 421

    def _get_charge_item(self, charged_item):
        charge_id = self._get_charge_id(charged_item)
        fitted_items = self._get_fitted_items()
        for item in fitted_items.itervalues():
            if item.itemID == charge_id:
                return item

    def _get_charge_id(self, item):
        return item.GetOtherID()

    def _get_charge_amount(self, item):
        return item.GetQuantity()

    def _is_turret(self, item):
        return sm.GetService('clientDogmaStaticSvc').TypeHasEffect(item.typeID, effectTurretFitted)

    def _is_charged(self, item):
        return bool(self._get_charge_id(item))

    def _get_condition_checks(self):
        return [self._is_charged, self._is_turret]

    def _get_item_data(self, item):
        item_id = type_id = group_id = None
        quantity = 0
        if item:
            charge_item = self._get_charge_item(item)
            if charge_item:
                item_id = charge_item.itemID
                if isinstance(item_id, Iterable):
                    item_id = iter(item_id).next()
                type_id = charge_item.typeID
                group_id = charge_item.groupID
                quantity = self._get_charge_amount(charge_item)
        return {'item_id': item_id,
         'type_id': type_id,
         'group_id': group_id,
         'quantity': quantity}

    @classmethod
    def get_subtitle(cls, item_id = None, type_id = None, group_id = None, category_id = None, **kwargs):
        if item_id:
            return 'Item {item_id}'.format(item_id=item_id)
        if type_id:
            return evetypes.GetName(type_id)
        if group_id:
            return evetypes.GetGroupNameByGroup(group_id)
        if category_id:
            return evetypes.GetCategoryNameByCategory(category_id)
        return ''


class GetValidModuleSlot(GetterAtom):
    atom_id = 318

    def __init__(self, type_id = None, ignore_current_fitting = None):
        self.type_id = type_id
        self.ignore_current_fitting = self.get_atom_parameter_value('ignore_current_fitting', ignore_current_fitting)

    def get_values(self):
        result = GetValidModuleSlots(type_id=self.type_id, ignore_current_fitting=self.ignore_current_fitting).get_values()
        slots_ids = result.get('slot_ids') if result else []
        if slots_ids:
            return {'slot_id': slots_ids[0]}

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return evetypes.GetName(type_id)
        return ''


class GetValidModuleSlots(GetterAtom):
    atom_id = 521

    def __init__(self, type_id = None, ignore_current_fitting = None):
        self.type_id = type_id
        self.ignore_current_fitting = self.get_atom_parameter_value('ignore_current_fitting', ignore_current_fitting)

    def __iter_current_ship_slots(self, dogma_location):
        from shipfitting.fittingStuff import GetSlotListForTypeID
        for slot_id in GetSlotListForTypeID(dogma_location, self.type_id):
            if dogma_location.SlotExists(dogma_location.GetCurrentShipID(), slot_id):
                yield slot_id

    def __iter_ignored_fitting_slots(self, dogma_location, dogmaStaticMgr, ship_type_id):
        from shipfitting.fittingStuff import GetModuleErrorInfo, IsRigTooSmall
        for slot_id in self.__iter_current_ship_slots(dogma_location):
            if GetModuleErrorInfo(dogma_location, self.type_id, ship_type_id) is not None:
                continue
            if IsRigTooSmall(dogmaStaticMgr, ship_type_id, self.type_id):
                continue
            yield slot_id

    def __iter_available_slots(self):
        from shipfitting.fittingStuff import GetErrorInfoDoesModuleTypeIDFitCurrentShip
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        used_slots = [ x.flagID for x in dogma_location.GetFittedItemsToShip().itervalues() ]
        for slot_id in self.__iter_current_ship_slots(dogma_location):
            if slot_id in used_slots:
                continue
            message = GetErrorInfoDoesModuleTypeIDFitCurrentShip(dogma_location, self.type_id, slot_id)
            if message is None:
                yield slot_id

    def ignored_fittings(self):
        from shipfitting.hardpointUtil import has_ship_any_hard_point_slot
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        ship_item = dogma_location.GetShipItem()
        if not ship_item:
            return []
        ship_type_id = ship_item.typeID
        dogmaStaticMgr = dogma_location.dogmaStaticMgr
        if not has_ship_any_hard_point_slot(dogmaStaticMgr, self.type_id, ship_type_id):
            return []
        return [ slot_id for slot_id in self.__iter_ignored_fitting_slots(dogma_location, dogmaStaticMgr, ship_type_id) ]

    def get_values(self, **kwargs):
        if not self.type_id:
            return None
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        ship_item = dogma_location.GetShipItem()
        if not ship_item:
            return {'slot_ids': []}
        if self.ignore_current_fitting:
            return {'slot_ids': self.ignored_fittings()}
        return {'slot_ids': [ slot_id for slot_id in self.__iter_available_slots() ]}

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return evetypes.GetName(type_id)
        return ''


class GetUsedWithType(GetterAtom):
    atom_id = 411

    def __init__(self, type_id = None):
        self.type_id = type_id

    def get_values(self):
        if not self.type_id:
            return None
        used_with_type = sm.GetService('info').GetUsedWithTypeIDs(self.type_id)
        return {'type_ids': list(used_with_type) if used_with_type else None}

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return evetypes.GetName(type_id)
        return ''


class GetMaxModuleRange(GetterAtom):
    atom_id = 480

    def __init__(self, item_id = None):
        self.item_id = item_id

    def get_values(self):
        if not self.item_id:
            return None
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        item = dogma_location.SafeGetDogmaItem(self.item_id)
        if not item:
            return None
        charge_id = item.GetOtherID()
        charge_item = dogma_location.SafeGetDogmaItem(charge_id)
        max_range, falloff_dist, _, _ = sm.GetService('tactical').FindMaxRange(item, charge_item, dogma_location)
        if falloff_dist > 1:
            max_range += falloff_dist
        return {'max_range': max_range}


class GetTakenHardpointSlots(GetterAtom):
    atom_id = 533

    def __init__(self, type_id = None):
        self.type_id = type_id

    def get_values(self):
        if not self.type_id:
            return None
        from shipfitting.hardpointUtil import get_fitted_launcher_slots_and_modules, get_fitted_turret_slots_and_modules, is_not_hard_point_module, is_launcher, is_turret
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogma_static_mgr = dogma_location.dogmaStaticMgr
        ship_id = session.shipid
        if is_not_hard_point_module(dogma_static_mgr, self.type_id):
            return {'slot_ids': []}
        if is_launcher(dogma_static_mgr, self.type_id):
            launcher_slots = get_fitted_launcher_slots_and_modules(dogma_location, ship_id).keys()
            return {'slot_ids': launcher_slots}
        if is_turret(dogma_static_mgr, self.type_id):
            turret_slots = get_fitted_turret_slots_and_modules(dogma_location, ship_id).keys()
            return {'slot_ids': turret_slots}

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return 'For {}'.format(evetypes.GetName(type_id))
        return ''
