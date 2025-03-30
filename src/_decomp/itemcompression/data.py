#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\data.py
from collections import defaultdict
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import compressibleTypesLoader
except ImportError:
    compressibleTypesLoader = None

class CompressibleTypesDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/compressibleTypes.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/compressibleTypes.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/compressibleTypes.fsdbinary'
    __loader__ = compressibleTypesLoader


class CompressibleTypesDataCache(object):
    __instance = None

    def __init__(self, loader):
        self._loader = loader
        self._is_primed = False
        self._compressed_type_by_source_type = {}
        self._source_types_by_compressed_type = {}
        self._loader.ConnectToOnReload(self.reset)

    @staticmethod
    def instance():
        if CompressibleTypesDataCache.__instance is None:
            CompressibleTypesDataCache.__instance = CompressibleTypesDataCache(CompressibleTypesDataLoader)
        return CompressibleTypesDataCache.__instance

    @property
    def source_types_by_compressed_type(self):
        return self._source_types_by_compressed_type

    def __getitem__(self, source_type_id):
        self._ensure_primed()
        return self._compressed_type_by_source_type[source_type_id]

    def __iter__(self):
        self._ensure_primed()
        return self._compressed_type_by_source_type.iteritems()

    def __contains__(self, source_type_id):
        self._ensure_primed()
        return source_type_id in self._compressed_type_by_source_type

    def all(self):
        self._ensure_primed()
        return self._compressed_type_by_source_type.values()

    def reload(self):
        self._loader.ReloadDataFromDisk()

    def reset(self):
        self._is_primed = False
        self._load_compressible_types_data()

    def _ensure_primed(self):
        if not self._is_primed:
            self._is_primed = True
            self._load_compressible_types_data()

    def _load_compressible_types_data(self):
        compressible_types_data = self._loader.GetData()
        self._compressed_type_by_source_type = {source_type_id:compressed_type_id for source_type_id, compressed_type_id in compressible_types_data.iteritems()}
        source_types_by_compressed_type = defaultdict(list)
        for source_type_id, compressed_type_id in compressible_types_data.iteritems():
            source_types_by_compressed_type[compressed_type_id].append(source_type_id)

        self._source_types_by_compressed_type = dict(source_types_by_compressed_type)


cache = CompressibleTypesDataCache.instance()

def get_compressed_type_id(source_type_id):
    return cache[source_type_id]


def is_compressible_type(source_type_id):
    return source_type_id in cache


def get_compression_source_type_ids(compressed_type_id):
    return cache.source_types_by_compressed_type[compressed_type_id]


def is_compressed_type(type_id):
    return type_id in cache.source_types_by_compressed_type
