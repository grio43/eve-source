#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\common\ess\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import essReserveKeysLoader
except ImportError:
    essReserveKeysLoader = None

class EssReserveKeysDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/essReserveKeys.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/essReserveKeys.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/essReserveKeys.fsdbinary'
    __loader__ = essReserveKeysLoader


class EssReserveKeysCache(object):
    __instance = None

    def __init__(self, loader):
        self._loader = loader
        self._is_primed = False
        self._ess_keys_by_type_id = {}
        self._loader.ConnectToOnReload(self.reset)

    @staticmethod
    def instance():
        if EssReserveKeysCache.__instance is None:
            EssReserveKeysCache.__instance = EssReserveKeysCache(EssReserveKeysDataLoader)
        return EssReserveKeysCache.__instance

    def __getitem__(self, ess_key_type_id):
        self._ensure_primed()
        return self._ess_keys_by_type_id[ess_key_type_id]

    def __iter__(self):
        self._ensure_primed()
        return self._ess_keys_by_type_id.itervalues()

    def all(self):
        self._ensure_primed()
        return self._ess_keys_by_type_id.values()

    def reload(self):
        self._loader.ReloadDataFromDisk()

    def reset(self):
        self._is_primed = False
        self._load_expert_systems_data()

    def _ensure_primed(self):
        if not self._is_primed:
            self._is_primed = True
            self._load_ess_key_data()

    def _load_ess_key_data(self):
        ess_key_data = self._loader.GetData()
        self._ess_keys_by_type_id = {data.keyTypeID:EssReserveBankKey(data) for data in ess_key_data.itervalues()}


cache = EssReserveKeysCache.instance()

class EssReserveBankKey(object):

    def __init__(self, data):
        self._data = data

    @property
    def type_id(self):
        return int(self._data.keyTypeID)

    @property
    def location_list(self):
        return self._data.locationListID

    @property
    def total_pulses(self):
        return self._data.totalPulses


def get_key_by_type(key_type_id):
    return cache[key_type_id]
