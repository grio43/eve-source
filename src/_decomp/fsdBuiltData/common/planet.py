#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\planet.py
from collections import defaultdict
try:
    import schematicsLoader
except ImportError:
    schematicsLoader = None

try:
    import globalSecuritiesLoader
except ImportError:
    globalSecuritiesLoader = None

try:
    import globalRegionsLoader
except ImportError:
    globalRegionsLoader = None

try:
    import globalTypesLoader
except ImportError:
    globalTypesLoader = None

try:
    import resourceCriteriaLoader
except ImportError:
    resourceCriteriaLoader = None

try:
    import resourceDepositDefinitionsLoader
except ImportError:
    resourceDepositDefinitionsLoader = None

import localization
from fsdBuiltData.common.base import BuiltDataLoader

class SchematicsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/schematics.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/schematics.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/schematics.fsdbinary'
    __loader__ = schematicsLoader


class GlobalSecuritiesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/globalSecurities.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/globalSecurities.fsdbinary'
    __loader__ = globalSecuritiesLoader


class GlobalRegionsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/globalRegions.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/globalRegions.fsdbinary'
    __loader__ = globalRegionsLoader


class GlobalTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/globalTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/globalTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/globalTypes.fsdbinary'
    __loader__ = globalTypesLoader


class ResourceCriteriaLoaderLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/resourceCriteria.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/resourceCriteria.fsdbinary'
    __loader__ = resourceCriteriaLoader


class ResourceDepositDefinitionsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/resourceDepositDefinitions.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/resourceDepositDefinitions.fsdbinary'
    __loader__ = resourceDepositDefinitionsLoader


def _get_schematics():
    return SchematicsLoader.GetData()


def get_schematic(schematic_id, default = None):
    return _get_schematics().get(schematic_id, default)


def iter_schematics():
    for schematic_id, schematic in _get_schematics().iteritems():
        yield (schematic_id, schematic)


def get_schematic_name(schematic_id, schematic = None):
    if not schematic:
        schematic = get_schematic(schematic_id)
    return localization.GetByMessageID(schematic.nameID)


def get_schematic_cycle_time(schematic_id, default = None):
    schematic = get_schematic(schematic_id)
    if schematic:
        return schematic.cycleTime
    return default


def get_schematic_types(schematic_id, default = None):
    schematic = get_schematic(schematic_id)
    if schematic:
        return schematic.types
    return default


def get_schematic_ids_for_pin_type_id(pin_type_id):
    return {schematic_id for schematic_id, schematic in _get_schematics().iteritems() if pin_type_id in schematic.pins}


def get_schematic_info_for_type_id(type_id):
    return [ (schematic_id, schematic.types[type_id].isInput) for schematic_id, schematic in _get_schematics().iteritems() if type_id in schematic.types ]


def schematic_exists(schematic_id):
    return schematic_id in _get_schematics()


def _get_global_securities():
    return GlobalSecuritiesLoader.GetData()


def _get_global_regions():
    return GlobalRegionsLoader.GetData()


def _get_global_types():
    return GlobalTypesLoader.GetData()


def get_global_securities():
    return {securityBandID:{typeID:quality for typeID, quality in info.resourceDistribution.iteritems()} for securityBandID, info in _get_global_securities().iteritems()}


def get_global_regions():
    return {regionID:{typeID:quality for typeID, quality in info.resourceDistribution.iteritems()} for regionID, info in _get_global_regions().iteritems()}


def get_global_types():
    return {planetTypeID:{typeID:quality for typeID, quality in info.resourceDistribution.iteritems()} for planetTypeID, info in _get_global_types().iteritems()}


planet_type_ids_by_resource_type_id = defaultdict(list)
resource_type_ids_by_planet_type_id = defaultdict(list)

def create_reverse_lookups():
    global resource_type_ids_by_planet_type_id
    global planet_type_ids_by_resource_type_id
    if not (planet_type_ids_by_resource_type_id and resource_type_ids_by_planet_type_id):
        for planet_type_id, data in get_global_types().iteritems():
            for type_id, quality in data.iteritems():
                if quality > 0:
                    resource_type_ids_by_planet_type_id[planet_type_id].append(type_id)
                    planet_type_ids_by_resource_type_id[type_id].append(planet_type_id)


def get_planet_type_ids_for_resource_type_id(resource_type_id, default = None):
    create_reverse_lookups()
    return planet_type_ids_by_resource_type_id.get(resource_type_id, default)


def get_resource_type_ids_for_planet_type_id(planet_type_id, default = None):
    create_reverse_lookups()
    return resource_type_ids_by_planet_type_id.get(planet_type_id, default)


def iter_resource_type_ids_by_planet_type_id():
    create_reverse_lookups()
    for planet_type_id, resource_type_ids in resource_type_ids_by_planet_type_id.iteritems():
        yield (planet_type_id, resource_type_ids)


GlobalTypesLoader.ConnectToOnReload(create_reverse_lookups)

def get_resource_criteria():
    return ResourceCriteriaLoaderLoader.GetData()


def get_resource_criteria_for_resource_type_id(resource_type_id, default = None):
    resource_criteria = get_resource_criteria().get(resource_type_id)
    if resource_criteria:
        return resource_criteria.planets
    return default


def get_resource_deposit_definitions():
    return ResourceDepositDefinitionsLoader.GetData()
