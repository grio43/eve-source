#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evestations\data.py
import logging
from collections import defaultdict
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import localization
except ImportError:
    localization = None

try:
    import stationOperationsLoader
except ImportError:
    stationOperationsLoader = None

try:
    import stationServicesLoader
except ImportError:
    stationServicesLoader = None

logger = logging.getLogger(__name__)

class StationOperations(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/stationOperations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/stationOperations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/stationOperations.fsdbinary'
    __loader__ = stationOperationsLoader


class StationServices(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/stationServices.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/stationServices.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/stationServices.fsdbinary'
    __loader__ = stationServicesLoader


LOCATION_NPC_STATION_FORMATTER_NO_OP_NAME_RAW = 'UI/Locations/LocationNPCStationFormatter_NoOpName_Raw'
LOCATION_NPC_STATION_FORMATTER_RAW = 'UI/Locations/LocationNPCStationFormatter_Raw'
OWNER_AURA_IDENTIFIER = -1
OWNER_SYSTEM_IDENTIFIER = -2
OWNER_NAME_OVERRIDES = {OWNER_AURA_IDENTIFIER: 'UI/Agents/AuraAgentName',
 OWNER_SYSTEM_IDENTIFIER: 'UI/Chat/ChatEngine/EveSystem'}

def refresh_station_data_caches():
    for name, func in globals().iteritems():
        if callable(func) and hasattr(func, 'clear_memoized'):
            logger.debug('clearing memoize cache for function %s', name)
            func.clear_memoized()


StationOperations.ConnectToOnReload(refresh_station_data_caches)

def _get_station_operations():
    return StationOperations.GetData()


def _get_station_operation(operation_id):
    return _get_station_operations().get(operation_id, None)


def get_station_operation_ids():
    return {operation_id for operation_id in _get_station_operations()}


@Memoize
def get_station_operations_by_activity():
    operations = defaultdict(dict)
    for operation_id, station_operation in _get_station_operations().iteritems():
        operations[station_operation.activityID][operation_id] = station_operation

    return dict(operations)


def get_station_operations_for_activity(activity_id):
    return get_station_operations_by_activity().get(activity_id, None)


def _get_station_operation_attribute(operation_id, attribute):
    station_operation = _get_station_operation(operation_id)
    if station_operation is None:
        return
    return getattr(station_operation, attribute)


def get_station_operation_activity(operation_id):
    return _get_station_operation_attribute(operation_id, 'activityID')


def _get_localization_text(message_id, language_id = None):
    if language_id is not None:
        return localization.GetByMessageID(message_id, languageID=language_id)
    return localization.GetByMessageID(message_id)


def get_station_operation_name(operation_id, language_id = None):
    station_operation = _get_station_operation(operation_id)
    if station_operation is not None:
        return _get_localization_text(station_operation.operationNameID, language_id)


def get_station_operation_name_id(operation_id):
    return _get_station_operation_attribute(operation_id, 'operationNameID')


def get_station_operation_description(operation_id, language_id = None):
    station_operation = _get_station_operation(operation_id)
    if station_operation is not None:
        return _get_localization_text(station_operation.descriptionID, language_id)


@Memoize
def get_station_services_for_operation(operation_id):
    return _get_station_operation_attribute(operation_id, 'services')


def _get_station_services():
    return StationServices.GetData()


def _get_station_service(service_id):
    return _get_station_services().get(service_id, None)


def get_station_service_name(service_id, language_id = None):
    station_service = _get_station_service(service_id)
    if station_service is not None:
        return _get_localization_text(station_service.serviceNameID, language_id)


def get_station_service_description(service_id, language_id = None):
    station_service = _get_station_service(service_id)
    if station_service is not None:
        return _get_localization_text(station_service.descriptionID, language_id)


def get_station_operation_manufacturing_factor(operation_id):
    return _get_station_operation_attribute(operation_id, 'manufacturingFactor')


def get_station_operation_research_factor(operation_id):
    return _get_station_operation_attribute(operation_id, 'researchFactor')


def service_in_station_operation(operation_id, service_id):
    station_services = get_station_services_for_operation(operation_id)
    if station_services is None:
        return False
    return service_id in station_services


def get_station_service_masks():
    services = _get_station_services()
    service_masks = {}
    for enum, service_id in enumerate(sorted(services.iterkeys())):
        service_masks[service_id] = pow(2, enum)

    return service_masks


def get_station_service_mask(operation_id):
    service_mask = 0
    services = get_station_services_for_operation(operation_id)
    if services is None or len(services) == 0:
        return 0
    service_mask_by_service_id = get_station_service_masks()
    for serviceID in services:
        service_mask = service_mask | service_mask_by_service_id[serviceID]

    return service_mask
