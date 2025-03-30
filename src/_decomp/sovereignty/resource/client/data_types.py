#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\client\data_types.py
from datetimeutils import unix_to_blue
from eveProto.generated.eve_public.sovereignty.resource.planet import reagent_pb2
from uthread import SEC

class AvailableHubResources(object):
    power_allocated = None
    power_available = None
    power_local_harvest = None
    workforce_allocated = None
    workforce_available = None
    workforce_local_harvest = None

    def __init__(self, power_allocated, power_available, power_local_harvest, workforce_allocated, workforce_available, workforce_local_harvest):
        self.power_allocated = power_allocated
        self.power_available = power_available
        self.power_local_harvest = power_local_harvest
        self.workforce_allocated = workforce_allocated
        self.workforce_available = workforce_available
        self.workforce_local_harvest = workforce_local_harvest

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.power_allocated == other.power_allocated and self.power_available == other.power_available and self.power_local_harvest == other.power_local_harvest and self.workforce_allocated == other.workforce_allocated and self.workforce_available == other.workforce_available and self.workforce_local_harvest == other.workforce_local_harvest

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<AvailableHubResources %s>' % self.__dict__


class HarvestSplitConfiguration(object):
    amount_per_period = None
    period = None
    secure_ratio = None
    secure_capacity = None
    insecure_capacity = None

    def __init__(self, amount_per_period, period, secure_ratio, secure_capacity, insecure_capacity):
        self.amount_per_period = amount_per_period
        self.period = period
        self.secure_ratio = secure_ratio
        self.secure_capacity = secure_capacity
        self.insecure_capacity = insecure_capacity

    @classmethod
    def create_from_proto(cls, config_data):
        definition = HarvestSplitConfiguration(config_data.amount_per_cycle, config_data.cycle_period.ToSeconds(), float(config_data.secured_percentage) / 100.0, config_data.secured_capacity, config_data.unsecured_capacity)
        return definition

    @property
    def period_bluetime(self):
        return self.period * SEC

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.amount_per_period == other.amount_per_period and self.period == other.period and self.secure_ratio == other.secure_ratio and self.secure_capacity == other.secure_capacity and self.insecure_capacity == other.insecure_capacity

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<HarvestSplitConfiguration %s>' % self.__dict__


class HarvestSplitSimulationState(object):
    secure_amount = None
    insecure_amount = None
    harvested_timestamp = None

    def __init__(self, secure_amount, insecure_amount, harvested_timestamp):
        self.secure_amount = secure_amount
        self.insecure_amount = insecure_amount
        self.harvested_timestamp = harvested_timestamp

    @classmethod
    def create_from_proto(cls, simulation_data):
        definition = HarvestSplitSimulationState(simulation_data.secured_stock, simulation_data.unsecured_stock, unix_to_blue(simulation_data.last_cycle.ToSeconds()))
        return definition

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.secure_amount == other.secure_amount and self.insecure_amount == other.insecure_amount and self.harvested_timestamp == other.harvested_timestamp

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<HarvestSplitSimulationState %s>' % self.__dict__


class ReagentProductionSplitDynamicData(object):
    reagent_type_id = None
    split_function_dynamic = None

    def __init__(self, reagent_type_id, split_function_dynamic):
        self.reagent_type_id = reagent_type_id
        self.split_function_dynamic = split_function_dynamic

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.reagent_type_id == other.reagent_type_id and self.split_function_dynamic == other.split_function_dynamic

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<ReagentProductionSplitDynamicData %s>' % self.__dict__


class ReagentDefinition(object):
    type_id = None
    split_configuration = None

    def __init__(self, type_id, split_configuration):
        self.type_id = type_id
        self.split_configuration = split_configuration

    @classmethod
    def create_from_proto(cls, type_id, definition_data):
        definition = ReagentDefinition(type_id, HarvestSplitConfiguration.create_from_proto(definition_data))
        return definition

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.type_id == other.type_id and self.split_configuration == other.split_configuration

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<ReagentDefinition %s>' % self.__dict__
