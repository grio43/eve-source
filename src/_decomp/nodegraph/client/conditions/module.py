#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\module.py
import evetypes
import eve.common.script.sys.eveCfg as eveCfg
from nodegraph.common.util import get_operator_function, get_object_predicate, get_object_in_list_predicate
from inventoryutil.client.inventory import get_ship_inventory
from .base import Condition
from evetypes import GetName

class AvailableTurretSlots(Condition):
    atom_id = 30

    def __init__(self, amount = None, operator = None, **kwargs):
        super(AvailableTurretSlots, self).__init__(**kwargs)
        self.amount = self.get_atom_parameter_value('amount', amount)
        self.operator = self.get_atom_parameter_value('operator', operator)

    def validate(self, **kwargs):
        inventory = get_ship_inventory()
        if not inventory:
            return False
        return get_operator_function(self.operator)(inventory.GetAvailableTurretSlots(), self.amount)

    @classmethod
    def get_subtitle(cls, operator = None, amount = None, **kwargs):
        return u'{} {}'.format(cls.get_atom_parameter_value('operator', operator), cls.get_atom_parameter_value('amount', amount))


class ModuleActive(Condition):
    atom_id = 31

    def __init__(self, item_id = None, type_id = None, group_id = None, type_list_id = None, required_attribute = None, target_item_id = None, **kwargs):
        super(ModuleActive, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.type_list_id = type_list_id
        self.required_attribute = required_attribute
        self.target_item_id = target_item_id

    def validate(self, **kwargs):
        if not eveCfg.InShipInSpace():
            return False
        active_modules = sm.GetService('godma').GetStateManager().GetActiveModules()
        if self.target_item_id:
            active_modules = [ module for module in active_modules if module.defaultEffect.targetID == self.target_item_id ]
        if not active_modules:
            return False
        checks = []
        if self.item_id:
            checks.append(get_object_predicate('itemID', self.item_id))
        elif self.type_id:
            checks.append(get_object_predicate('typeID', self.type_id))
        elif self.group_id:
            checks.append(get_object_predicate('groupID', self.group_id))
        elif self.type_list_id:
            valid_types = evetypes.GetTypeIDsByListID(self.type_list_id)
            checks.append(get_object_in_list_predicate('typeID', valid_types))
        if self.required_attribute:

            def _has_attribute(item):
                return self.required_attribute in item.attributes

            checks.append(_has_attribute)
        if not checks:
            return True
        for module in active_modules:
            if all([ check(module) for check in checks ]):
                return True

        return False

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, **kwargs):
        if type_id:
            return evetypes.GetName(type_id)
        if group_id:
            return evetypes.GetGroupNameByGroup(group_id)
        return ''


class ModuleCondition(Condition):
    atom_id = None

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, quantity = None, operator = None, **kwargs):
        super(ModuleCondition, self).__init__(**kwargs)
        self.item_id = item_id
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id
        self.quantity = self.get_atom_parameter_value('quantity', quantity)
        self.operator = self.get_atom_parameter_value('operator', operator)

    def _get_fitted_items(self):
        dogma_im = sm.GetService('clientDogmaIM')
        dogma_lm = dogma_im.GetDogmaLocation()
        ship_dogma_item = dogma_lm.SafeGetDogmaItem(session.shipid)
        return ship_dogma_item.GetFittedItems()

    def _get_condition_checks(self):
        return []

    def _get_predicate(self):

        def predicate(item):
            checks = self._get_condition_checks()
            if self.item_id:
                checks.append(get_object_predicate('itemID', self.item_id))
            if self.type_id:
                checks.append(get_object_predicate('typeID', self.type_id))
            if self.group_id:
                checks.append(get_object_predicate('groupID', self.group_id))
            if self.category_id:
                checks.append(get_object_predicate('categoryID', self.category_id))
            return all([ check(item) for check in checks ])

        return predicate

    def validate(self, **kwargs):
        if not session.shipid:
            return False
        predicate = self._get_predicate()
        fitted_items = self._get_fitted_items().values()
        amount = 0
        operator_func = get_operator_function(self.operator)
        return_early = self.operator.startswith('greaterThan')
        for module in fitted_items:
            if predicate(module):
                if return_early and operator_func(amount, self.quantity):
                    return True
                amount += 1

        return operator_func(amount, self.quantity)

    @classmethod
    def get_subtitle(cls, type_id = None, group_id = None, category_id = None, operator = None, quantity = None, **kwargs):
        if type_id:
            name = evetypes.GetName(type_id)
        elif group_id:
            name = evetypes.GetGroupNameByGroup(group_id)
        elif category_id:
            name = evetypes.GetCategoryNameByCategory(category_id)
        else:
            name = ''
        operator_value = cls.get_atom_parameter_value('operator', operator)
        quantity_value = cls.get_atom_parameter_value('quantity', quantity)
        if operator_value and quantity_value:
            return u'{operator} {quantity} - {name}'.format(operator=operator_value, quantity=quantity_value, name=name)
        return name


class ModuleCharged(ModuleCondition):
    atom_id = 32

    def __init__(self, item_id = None, type_id = None, group_id = None, category_id = None, quantity = None, operator = None, charge_type_id = None, charge_quantity = None, charge_operator = None, **kwargs):
        super(ModuleCharged, self).__init__(item_id, type_id, group_id, category_id, quantity, operator, **kwargs)
        self.charge_type_id = charge_type_id
        self.charge_quantity = charge_quantity
        self.charge_operator = charge_operator

    def _get_charge_item(self, charged_item):
        charge_id = self._get_charge_id(charged_item)
        fitted_items = self._get_fitted_items()
        for item in fitted_items.itervalues():
            if item.itemID == charge_id:
                return item

    def _get_charge_id(self, item):
        return item.GetOtherID()

    def _is_charged(self, item):
        return bool(self._get_charge_id(item))

    def _has_charge(self, item):
        if not self.charge_type_id and not self.charge_quantity:
            return True
        charge_item = self._get_charge_item(item)
        if not charge_item:
            return False
        if self.charge_type_id and charge_item.typeID != self.charge_type_id:
            return False
        if self.charge_quantity:
            charge_quantity = charge_item.GetQuantity()
            operator_func = get_operator_function(self.charge_operator) if self.charge_operator else (lambda a, b: a == b)
            if not operator_func(charge_quantity, self.charge_quantity):
                return False
        return True

    def _get_condition_checks(self):
        return [self._is_charged, self._has_charge]


class ModuleOnline(ModuleCondition):
    atom_id = 129

    def _is_online(self, module):
        return module.IsOnline()

    def _get_condition_checks(self):
        return [self._is_online]


class ModuleDamaged(Condition):
    atom_id = 387

    def __init__(self, item_id = None, burnt_out = None, **kwargs):
        super(ModuleDamaged, self).__init__(**kwargs)
        self.item_id = item_id
        self.burnt_out = self.get_atom_parameter_value('burnt_out', burnt_out)

    def validate(self, **kwargs):
        if not self.item_id:
            return False
        import repair
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.burnt_out:
            return repair.IsModuleBurntOut(self.item_id, dogma_location)
        else:
            return repair.IsModuleDamaged(self.item_id, dogma_location)


class CanModuleBeFit(Condition):
    atom_id = 524

    def __init__(self, type_id = None, ignore_current_fitting = None, **kwargs):
        super(CanModuleBeFit, self).__init__(**kwargs)
        self.type_id = type_id
        self.ignore_current_fitting = self.get_atom_parameter_value('ignore_current_fitting', ignore_current_fitting)

    def validate(self, **kwargs):
        if not self.type_id:
            return False
        from nodegraph.client.getters.module import GetValidModuleSlots
        result = GetValidModuleSlots(type_id=self.type_id, ignore_current_fitting=self.ignore_current_fitting).get_values()
        return bool(result and result.get('slot_ids'))

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return GetName(type_id)
        return ''


class AreHardpointsAvailable(Condition):
    atom_id = 537

    def __init__(self, type_id = None, **kwargs):
        super(AreHardpointsAvailable, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        from shipfitting.hardpointUtil import has_ship_free_hard_point_for_module
        dogma_location = sm.GetService('clientDogmaIM').GetDogmaLocation()
        return has_ship_free_hard_point_for_module(dogma_location=dogma_location, module_type_id=self.type_id, ship_id=session.shipid)

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if type_id:
            return 'For {}'.format(GetName(type_id))
        return ''
