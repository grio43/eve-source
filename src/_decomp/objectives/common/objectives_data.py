#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\common\objectives_data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import objectiveChainsLoader
except ImportError:
    objectiveChainsLoader = None

try:
    import objectiveTypesLoader
except ImportError:
    objectiveTypesLoader = None

try:
    import objectiveTaskTypesLoader
except ImportError:
    objectiveTaskTypesLoader = None

class ObjectiveChainsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/objectiveChains.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/objectiveChains.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/objectiveChains.fsdbinary'
    __loader__ = objectiveChainsLoader


class ObjectiveTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/objectiveTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/objectiveTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/objectiveTypes.fsdbinary'
    __loader__ = objectiveTypesLoader


class ObjectiveTaskTypesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticData/objectiveTaskTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/objectiveTaskTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/objectiveTaskTypes.fsdbinary'
    __loader__ = objectiveTaskTypesLoader


def get_objective_chains():
    return ObjectiveChainsLoader.GetData()


def get_objective_chain_data(objective_chain_id):
    return get_objective_chains().get(objective_chain_id, None)


def get_objective_types():
    return ObjectiveTypesLoader.GetData()


def get_objective_type_data(objective_type_id):
    return get_objective_types().get(objective_type_id, None)


def get_objective_task_types():
    return ObjectiveTaskTypesLoader.GetData()


def get_objective_task_type_data(objective_task_type_id):
    return get_objective_task_types().get(objective_task_type_id, None)
