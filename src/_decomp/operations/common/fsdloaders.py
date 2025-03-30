#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\common\fsdloaders.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import operationsLoader
except ImportError:
    operationsLoader = None

try:
    import operationTasksLoader
except ImportError:
    operationTasksLoader = None

try:
    import operationTreeStructuresLoader
except ImportError:
    operationTreeStructuresLoader = None

try:
    import operationCategoriesLoader
except ImportError:
    operationCategoriesLoader = None

try:
    import operationSitesLoader
except ImportError:
    operationSitesLoader = None

try:
    import schoolMapLoader
except ImportError:
    schoolMapLoader = None

class OperationsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/operations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/operations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/operations.fsdbinary'
    __loader__ = operationsLoader

    @classmethod
    def GetByID(cls, operationID):
        return cls.GetData().get(operationID, None)


class OperationTasksLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/operationTasks.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/operationTasks.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/operationTasks.fsdbinary'
    __loader__ = operationTasksLoader

    @classmethod
    def GetByID(cls, taskID):
        return cls.GetData().get(taskID, None)


class OperationTreeStructuresLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/operationTreeStructures.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/operationTreeStructures.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/operationTreeStructures.fsdbinary'
    __loader__ = operationTreeStructuresLoader

    @classmethod
    def GetByID(cls, treeID):
        return cls.GetData().get(treeID, None)


class OperationCategoriesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/operationCategories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/operationCategories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/operationCategories.fsdbinary'
    __loader__ = operationCategoriesLoader

    @classmethod
    def GetByID(cls, categoryID):
        return cls.GetData().get(categoryID, None)


class OperationSitesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/operationSites.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/operationSites.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/operationSites.fsdbinary'
    __loader__ = operationSitesLoader


class OperationSchoolMapLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/schoolMap.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/schoolMap.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/schoolMap.fsdbinary'
    __loader__ = schoolMapLoader

    @classmethod
    def GetConnections(cls):
        return cls.GetData().values()


def get_all_operation_categories():
    return OperationCategoriesLoader.GetData()


def get_all_operation_categorie_ids():
    return get_all_operation_categories().keys()
