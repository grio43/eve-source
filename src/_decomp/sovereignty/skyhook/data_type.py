#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\skyhook\data_type.py
import datetime
import gametime
from const import SEC
from datetimeutils import datetime_to_filetime
from sovereignty.resource.client.data_types import HarvestSplitSimulationState, HarvestSplitConfiguration, ReagentProductionSplitDynamicData, ReagentDefinition
STALE_DATA_GRACE_PERIOD = 30 * SEC
import logging
logger = logging.getLogger(__name__)

def get_skyhook_object(skyhook_id, active, reagent_simulations, reagent_definitions, vulnerability_data, workforce, resource_version):
    reagent_simulation_data_list = []
    reagent_definition_list = []
    for simulation in reagent_simulations:
        reagent_simulation_data_list.append(ReagentProductionSplitDynamicData(reagent_type_id=simulation.reagent_type.sequential, split_function_dynamic=HarvestSplitSimulationState.create_from_proto(simulation.simulation)))

    for definition in reagent_definitions:
        reagent_type = definition.reagent_type.sequential
        reagent_config = HarvestSplitConfiguration.create_from_proto(definition.definition)
        reagent_definition_list.append(ReagentDefinition(reagent_type, reagent_config))

    if vulnerability_data is not None:
        vulnerability_data = SkyhookTheftVulnerabilityData(vulnerability_data.vulnerable, vulnerability_data.start.ToDatetime(), vulnerability_data.end.ToDatetime())
    return Skyhook(skyhook_id, active, reagent_simulation_data_list, reagent_definition_list, vulnerability_data, workforce, resource_version)


class ReagentData:

    def __init__(self, type_id, configuration = None, simulation = None):
        self.type_id = type_id
        self.configuration = configuration
        self.simulation = simulation

    def __eq__(self, other):
        return self.type_id == other.type_id and self.configuration == other.configuration and self.simulation == other.simulation

    def __ne__(self, other):
        return not self.__eq__(other)


class Skyhook(object):
    ID = 0
    active = False
    reagent_data = None
    vulnerability_data = None

    def __init__(self, skyhook_id, active, reagent_simulation_data_list, reagent_definition_list, vulnerability_data, workforce, resource_version):
        super(Skyhook, self).__init__()
        self.reagent_data = {}
        self.ID = skyhook_id
        self.active = active
        self.vulnerability_data = vulnerability_data
        self.set_simulations(reagent_simulation_data_list)
        self.set_configurations(reagent_definition_list)
        self.workforce = workforce
        self.resource_version = resource_version

    def set_simulations(self, reagent_production_data_list):
        for prod_data in reagent_production_data_list:
            if prod_data.reagent_type_id not in self.reagent_data:
                if prod_data.reagent_type_id == 0:
                    continue
                self.reagent_data[prod_data.reagent_type_id] = ReagentData(prod_data.reagent_type_id, simulation=prod_data.split_function_dynamic)
            else:
                self.reagent_data[prod_data.reagent_type_id].simulation = prod_data.split_function_dynamic

    def set_configurations(self, reagent_definition_list):
        for data in reagent_definition_list:
            if data.type_id == 0:
                continue
            if data.type_id not in self.reagent_data:
                self.reagent_data[data.type_id] = ReagentData(data.type_id, configuration=data.split_configuration)
            else:
                self.reagent_data[data.type_id].configuration = data.split_configuration

    def __eq__(self, other):
        if not isinstance(other, Skyhook):
            return NotImplemented
        return self.ID == other.ID and self.active == other.active and len(self.reagent_data) == len(other.reagent_data) and self.workforce == other.workforce and self.resource_version == other.resource_version

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_first_simulation(self):
        keys = self.reagent_data.keys()
        if keys:
            return self.reagent_data[keys[0]].simulation

    def get_first_configuration(self):
        keys = self.reagent_data.keys()
        if keys:
            return self.reagent_data[keys[0]].configuration

    def get_first_reagent_data(self):
        keys = self.reagent_data.keys()
        if keys:
            return self.reagent_data[keys[0]]

    def set_vulnerability_schedule(self, start_datetime, end_datetime):
        vulnerable = self.vulnerability_data.vulnerable = datetime_to_filetime(start_datetime) < gametime.GetWallclockTime()
        if self.vulnerability_data:
            self.vulnerability_data.start = start_datetime
            self.vulnerability_data.end = end_datetime
        else:
            self.vulnerability_data = SkyhookTheftVulnerabilityData(vulnerable, start_datetime, end_datetime)

    def set_vulnerability(self, vulnerability):
        if self.vulnerability_data:
            self.vulnerability_data.vulnerability = vulnerability
        else:
            self.vulnerability_data = SkyhookTheftVulnerabilityData(vulnerability, datetime.datetime.now(), datetime.datetime.now())

    def set_vulnerability_end(self, end_datetime, vulnerability):
        if self.vulnerability_data:
            self.vulnerability_data.vulnerable = vulnerability
            self.vulnerability_data.end = end_datetime
        else:
            self.vulnerability_data = SkyhookTheftVulnerabilityData(vulnerability, datetime.datetime.now(), end_datetime)

    def set_activation_status(self, activation_status):
        self.active = activation_status

    def is_vulnerability_stale(self, now):
        is_reagent_skyhook = self.get_first_simulation() is not None
        is_reagent_skyhook_without_vulnerability = is_reagent_skyhook and self.vulnerability_data is None
        is_reagent_skyhook_with_stale_vulnerability = self.vulnerability_data is not None and self.vulnerability_data.is_stale_at_time(now)
        return is_reagent_skyhook_with_stale_vulnerability or is_reagent_skyhook_without_vulnerability


class SkyhookTheftVulnerabilityData(object):

    def __init__(self, vulnerable, start, end):
        self.vulnerable = vulnerable
        self.start = start
        self.end = end

    def __eq__(self, other):
        if not isinstance(other, SkyhookTheftVulnerabilityData):
            return NotImplemented
        return self.vulnerable == other.vulnerable and self.start == other.start and self.end == other.end

    def is_stale_at_time(self, time):
        end_time_wallclock = datetime_to_filetime(self.end) + STALE_DATA_GRACE_PERIOD
        start_time_wallclock = datetime_to_filetime(self.start) + STALE_DATA_GRACE_PERIOD
        if self.vulnerable:
            is_stale = end_time_wallclock < time or start_time_wallclock > time
        else:
            is_stale = start_time_wallclock < time and end_time_wallclock > time
        return is_stale


class PlanetAndSkyhookTheftVulnerabilityData(object):

    def __init__(self, skyhook_id, planet_id, expiry):
        self.skyhook_id = skyhook_id
        self.planet_id = planet_id
        self.expiry = expiry

    def __eq__(self, other):
        if not isinstance(other, PlanetAndSkyhookTheftVulnerabilityData):
            return NotImplemented
        return self.skyhook_id == other.skyhook_id and self.planet_id == other.planet_id and self.expiry == other.expiry
