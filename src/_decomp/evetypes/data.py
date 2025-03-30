#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evetypes\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import categoriesLoader
except ImportError:
    categoriesLoader = None

class Categories(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/categories.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/categories.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/categories.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/evetypes/categories'
    __loader__ = categoriesLoader


try:
    import groupsLoader
except ImportError:
    groupsLoader = None

class Groups(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/groups.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/groups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/groups.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/evetypes/groups'
    __loader__ = groupsLoader


try:
    import typesLoader
except ImportError:
    typesLoader = None

class Types(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/types.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/types.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/types.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/evetypes/types'
    __loader__ = typesLoader


try:
    import typeListLoader
except ImportError:
    typeListLoader = None

class TypeListLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/typeList.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/typeList.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/typeList.fsdbinary'
    __dataemporiumDatasetName__ = 'staticdata:/evetypelists/evetypelists'
    __loader__ = typeListLoader
