#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\client\data_sources.py
from locks import RLock
from publicGateway.grpc.exceptions import GenericException, BackedOffException
from sovereignty.resource.client.messenger import SovereigntyResourceMessenger
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from sovereignty.resource.shared.planetary_resources_data import PlanetaryResourcesData
from stackless_response_router.exceptions import TimeoutException
if False:
    from typing import Dict, List

def get_current_planetary_data(messenger, current_max_version):
    try:
        power_by_planet, workforce_by_planet, reagent_by_planet_id, resource_version = messenger.get_all_planet_definitions(current_max_version)
    except (GenericException, TimeoutException, BackedOffException) as e:
        raise DataUnavailableError(e)

    return PlanetaryResourcesData(power_by_planet, workforce_by_planet, reagent_by_planet_id, resource_version)


def get_versioned_planetary_data(messenger, version_to_get):
    try:
        power_by_planet, workforce_by_planet, reagent_by_planet_id, resource_version = messenger.get_all_planet_definitions_by_version(version_to_get)
    except (GenericException, TimeoutException, BackedOffException) as e:
        raise DataUnavailableError(e)

    return PlanetaryResourcesData(power_by_planet, workforce_by_planet, reagent_by_planet_id, resource_version)


class ConfigurationDataSource(object):
    _data_lock = RLock('ConfigurationDataSource')
    _is_primed = False

    def __init__(self, sov_resource_messenger, planet_data_cache):
        self._sov_resource_messenger = sov_resource_messenger
        self._planet_data_cache = planet_data_cache

    def prime_data(self):
        return self._prime_data_from_external_source()

    def _prime_data_from_external_source(self):
        if self._is_primed:
            return
        with self._data_lock:
            if self._is_primed:
                return
            try:
                power_by_star = self._sov_resource_messenger.get_all_star_configurations()
            except (GenericException, TimeoutException, BackedOffException) as e:
                raise DataUnavailableError(e)

            self._power_by_star = power_by_star
            self._is_primed = True

    def get_all_power_production(self, version = None):
        data = self._planet_data_cache.get_data(version)
        return data.power_by_planet

    def get_power_production(self, planet_id, version = None):
        data = self._planet_data_cache.get_data(version)
        return data.power_by_planet.get(planet_id, None)

    def get_all_workforce_production(self, version = None):
        data = self._planet_data_cache.get_data(version)
        return data.workforce_by_planet

    def get_workforce_production(self, planet_id, version = None):
        data = self._planet_data_cache.get_data(version)
        return data.workforce_by_planet.get(planet_id, None)

    def get_reagent_definitions(self, planet_id, version = None):
        data = self._planet_data_cache.get_data(version)
        return data.reagent_by_planet.get(planet_id, None)

    def get_first_reagent_definition(self, planet_id, version = None):
        reagent_definitions = self.get_reagent_definitions(planet_id, version)
        if reagent_definitions:
            return reagent_definitions[0]

    def get_power_production_for_star(self, star_id):
        self._prime_data_from_external_source()
        return self._power_by_star.get(star_id, None)
