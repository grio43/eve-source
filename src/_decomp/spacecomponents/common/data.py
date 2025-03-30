#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\data.py
import logging
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
from spacecomponents.common.componentConst import ALL_COMPONENTS
logger = logging.getLogger(__name__)
try:
    import spaceComponentsByTypeLoader
except ImportError:
    spaceComponentsByTypeLoader = None
    logger.debug('spaceComponentsByTypeLoader not available')

class SpaceComponentsByType(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/spaceComponentsByType.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/spaceComponentsByType.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/spaceComponentsByType.fsdbinary'
    __loader__ = spaceComponentsByTypeLoader


def _get_space_components_by_type():
    return SpaceComponentsByType.GetData()


def _get_space_components_for_type(type_id):
    return _get_space_components_by_type().get(type_id)


def get_space_component_for_type(type_id, component_name):
    return getattr(_get_space_components_for_type(type_id), component_name, None)


@Memoize
def get_space_component_names_for_type(type_id, component_names = ALL_COMPONENTS):
    type_components = _get_space_components_for_type(type_id)
    if type_components is None:
        return []
    return [ component_name for component_name in component_names if getattr(type_components, component_name, None) is not None ]


@Memoize
def get_type_ids_with_space_component(component_name):
    return [ typeID for typeID, type_components in _get_space_components_by_type().iteritems() if getattr(type_components, component_name, None) is not None ]


@Memoize
def type_has_space_component(type_id, component_name):
    type_components = _get_space_components_for_type(type_id)
    if type_components:
        return getattr(type_components, component_name, None) is not None
    else:
        return False


@Memoize
def type_has_space_component_cached(type_id, component_name):
    type_components = _get_space_components_for_type(type_id)
    if type_components:
        return getattr(type_components, component_name, None) is not None
    else:
        return False


def clear_space_component_cache():
    for name, func in globals().iteritems():
        if callable(func) and hasattr(func, 'clear_memoized'):
            logger.debug('clearing memoize cache for space component function %s', name)
            func.clear_memoized()


SpaceComponentsByType.ConnectToOnReload(clear_space_component_cache)
