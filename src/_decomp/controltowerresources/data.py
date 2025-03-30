#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\controltowerresources\data.py
from caching.memoize import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import localization
except ImportError:
    localization = None

try:
    import controlTowerResourcesLoader
except ImportError:
    controlTowerResourcesLoader = None

class ControlTowerResources(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/controlTowerResources.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/controlTowerResources.fsdbinary'
    __loader__ = controlTowerResourcesLoader


def _get_resources():
    return ControlTowerResources.GetData()


def get_control_tower_type_ids():
    return [ type_id for type_id in _get_resources().iterkeys() ]


def get_control_tower_resources(type_id):
    control_tower_data = _get_resources().get(type_id)
    if control_tower_data:
        return control_tower_data.resources
    else:
        return []


def get_resources_for_tower_by_purpose(type_id, purpose):
    resources = get_control_tower_resources(type_id)
    if not resources:
        return []
    return [ resource for resource in resources if resource.purpose == purpose ]
