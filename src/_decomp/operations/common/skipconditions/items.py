#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\skipconditions\items.py
from eve.common.lib.appConst import containerHangar
from eve.common.script.sys.idCheckers import IsShip
from evetypes import GetGroupID
from inventorycommon.const import flagHangar, flagCargo, fittingFlags, typeSurvivor, typeScientist
import logging
from operations.common.skipconditions.skipconditions import SkipCondition, OPERATOR_STRING_TO_EVALUATION_FUNCTION
logger = logging.getLogger(__name__)

def get_ship_inventory():
    shipID = session.shipid
    if shipID:
        try:
            shipItem = sm.GetService('godma').GetItem(shipID)
            if shipItem:
                shipItemCategoryID = shipItem.categoryID
                if IsShip(shipItemCategoryID):
                    return sm.GetService('invCache').GetInventoryFromId(shipID)
        except Exception:
            pass


def get_hangar_inventory():
    if session.stationid:
        try:
            return sm.GetService('invCache').GetInventory(containerHangar)
        except Exception:
            pass


class BaseConditionItemOwned(SkipCondition):
    INVENTORY_FLAGS = {}

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Item Owned condition evaluation requires integer parameter')

        try:
            type_id = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Item Owned condition evaluation requires integer as the item typeID identifier')

        owned_count = self.get_owned_count(type_id)
        return operator_func(owned_count, operand)

    def get_owned_count(self, type_id):
        count = 0
        inventories = {inventory for inventory in self.get_inventories() if inventory}
        for inventory in inventories:
            for flag in self.INVENTORY_FLAGS:
                for item in inventory.List(flag):
                    if item.typeID == type_id:
                        count += 1

        return count

    def get_inventories(self):
        raise NotImplementedError('Must implement get_inventories in derived class')


class ConditionItemInHangar(BaseConditionItemOwned):
    INVENTORY_FLAGS = {flagHangar}

    def get_inventories(self):
        hangar_inventory = get_hangar_inventory()
        if hangar_inventory:
            return [hangar_inventory]
        return []


class BaseConditionItemInShip(BaseConditionItemOwned):
    INVENTORY_FLAGS = {}

    def get_inventories(self):
        ship_inventory = get_ship_inventory()
        if ship_inventory:
            return [ship_inventory]
        return []


class ConditionItemInCargo(BaseConditionItemInShip):
    INVENTORY_FLAGS = {flagCargo}


class ConditionItemFitted(BaseConditionItemInShip):
    INVENTORY_FLAGS = fittingFlags


class ConditionItemOwned(ConditionItemInHangar, ConditionItemInCargo, ConditionItemFitted):
    INVENTORY_FLAGS = ConditionItemInHangar.INVENTORY_FLAGS.union(ConditionItemInCargo.INVENTORY_FLAGS, ConditionItemFitted.INVENTORY_FLAGS)

    def get_inventories(self):
        return [ inventory for inventory in [get_ship_inventory(), get_hangar_inventory()] if inventory ]


class ConditionSurvivorOwned(ConditionItemOwned):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Survivor Owned condition evaluation requires integer parameter')

        survivors_owned = self.get_owned_count(typeSurvivor) + self.get_owned_count(typeScientist)
        return operator_func(survivors_owned, operand)


class ConditionModuleCharged(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Module Charged condition evaluation requires integer parameter')

        try:
            type_id = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Module Charged condition evaluation requires integer as the module typeID identifier')

        is_charged = self.count_charged_modules_of_type_on_current_ship(type_id)
        owned_count = int(is_charged)
        return operator_func(owned_count, operand)

    def count_charged_modules_of_type_on_current_ship(self, type_id):
        if not session.shipid:
            return 0
        clientDogmaIM = sm.GetService('clientDogmaIM')
        clientDogmaLM = clientDogmaIM.GetDogmaLocation()
        shipDogmaItem = clientDogmaLM.SafeGetDogmaItem(session.shipid)
        fittedItems = shipDogmaItem.GetFittedItems().values()
        return len([ module for module in fittedItems if module.typeID == type_id and module.GetOtherID() ])


class GodmaSkipCondition(SkipCondition):

    def __init__(self):
        self.godma_state_manager = None

    def get_godma_state_manager(self):
        if self.godma_state_manager is None:
            self.godma_state_manager = sm.GetService('godma').GetStateManager()
        return self.godma_state_manager


class ConditionModuleActive(GodmaSkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        try:
            operand = int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Module active condition evaluation requires integer parameter as an operand')

        try:
            identifier = int(condition_parameters.identifier)
        except ValueError:
            raise RuntimeError('Module active condition evaluation requires an integer identifier')

        is_module_active = self.is_module_active(identifier)
        module_active_count = int(is_module_active)
        return operator_func(module_active_count, operand)

    def is_module_active(self, identifier):
        raise NotImplementedError('Module active check not implemented for base class ConditionModuleActive')

    def get_active_module_types(self):
        return self.get_godma_state_manager().GetActiveModuleTypes()


class ConditionModuleTypeActive(ConditionModuleActive):

    def is_module_active(self, type_id):
        return type_id in self.get_active_module_types()


class ConditionModuleGroupActive(ConditionModuleActive):

    def is_module_active(self, group_id):
        active_module_group_ids = []
        for active_module_type_id in self.get_active_module_types():
            active_module_group_id = GetGroupID(active_module_type_id)
            active_module_group_ids.append(active_module_group_id)

        return group_id in active_module_group_ids


class BaseConditionShipAttributeValue(GodmaSkipCondition):
    ATTRIBUTE_KEY = None

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        operand = self._read_operand(condition_parameters)
        try:
            attribute_value = self.get_attribute_value()
        except Exception as exc:
            logger.exception('Failed to evaluate ship attribute skip condition, could not retrieve dogma attribute value for key %s' % self.ATTRIBUTE_KEY, exc=exc)
            return False

        return operator_func(attribute_value, operand)

    def _read_operand(self, condition_parameters):
        try:
            return float(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Ship attribute skip condition requires operand as a decimal number')

    def get_attribute_value(self):
        return self.get_godma_state_manager().GetAttributeValueByID(session.shipid, self.ATTRIBUTE_KEY)


class ConditionFreeTurretSlots(SkipCondition):

    def Evaluate(self, character_id, condition_parameters):
        operator_func = OPERATOR_STRING_TO_EVALUATION_FUNCTION.get(condition_parameters.operator)
        operand = self._read_operand(condition_parameters)
        try:
            number_of_free_turret_slots = self._get_number_of_free_turret_slots()
        except Exception as exc:
            logger.exception('Failed to evaluate free turret slots skip condition, could not access ship data', exc=exc)
            return False

        return operator_func(number_of_free_turret_slots, operand)

    def _read_operand(self, condition_parameters):
        try:
            return int(condition_parameters.operand)
        except ValueError:
            raise RuntimeError('Free turret slots skip condition requires operand as an integer number')

    def _get_number_of_free_turret_slots(self):
        ship_inventory = get_ship_inventory()
        if ship_inventory:
            return ship_inventory.GetAvailableTurretSlots()
        return 0
