#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\data.py
import collections
import datetime
import evetypes
import logging
import locks
from fsdBuiltData.common.base import BuiltDataLoader
logger = logging.getLogger(__name__)
try:
    import expertSystemsLoader
except ImportError:
    expertSystemsLoader = None

class ExpertSystemsDataLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/expertSystems.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/expertSystems.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/expertSystems.fsdbinary'
    __loader__ = expertSystemsLoader


class ExpertSystemsCache(object):
    __instance = None

    def __init__(self, loader):
        self._loader = loader
        self._is_primed = False
        self._expert_systems_by_type_id = {}
        self._expert_systems_by_associated_type_id = {}
        self._loader.ConnectToOnReload(self.reset)

    @staticmethod
    def instance():
        if ExpertSystemsCache.__instance is None:
            ExpertSystemsCache.__instance = ExpertSystemsCache(ExpertSystemsDataLoader)
        return ExpertSystemsCache.__instance

    def __getitem__(self, expert_system_type_id):
        self._ensure_primed()
        return self._expert_systems_by_type_id[expert_system_type_id]

    def __iter__(self):
        self._ensure_primed()
        return self._expert_systems_by_type_id.itervalues()

    def all(self):
        self._ensure_primed()
        return self._expert_systems_by_type_id.values()

    def visible(self):
        self._ensure_primed()
        return filter(lambda x: not x.hidden, self._expert_systems_by_type_id.values())

    def associated_with(self, type_id):
        self._ensure_primed()
        try:
            expert_systems = self._expert_systems_by_associated_type_id[type_id]
        except KeyError:
            logger.exception('Expert System KeyError::_expert_systems_by_associated_type_id is not initialized, even though _ensure_primed has been called. _is_primed: %s' % self._is_primed)
            return []

        return expert_systems

    def reload(self):
        self._loader.ReloadDataFromDisk()

    def reset(self):
        self._is_primed = False
        self._load_expert_systems_data()

    def _ensure_primed(self):
        if self._is_primed:
            return
        with locks.TempLock('PrimingExpertSystem'):
            if self._is_primed:
                return
            self._load_expert_systems_data()
            self._is_primed = True

    def _load_expert_systems_data(self):
        expert_systems_data = self._loader.GetData()
        self._expert_systems_by_type_id = {type_id:ExpertSystem(type_id, data) for type_id, data in expert_systems_data.iteritems()}
        self._expert_systems_by_associated_type_id = collections.defaultdict(list)
        for expert_system in self._expert_systems_by_type_id.itervalues():
            for ship_type_id in expert_system.associated_type_ids:
                self._expert_systems_by_associated_type_id[ship_type_id].append(expert_system)


cache = ExpertSystemsCache.instance()

class ExpertSystem(object):

    def __init__(self, type_id, data):
        self._type_id = type_id
        self._data = data

    @property
    def type_id(self):
        return int(self._type_id)

    @property
    def name(self):
        return evetypes.GetName(self.type_id)

    @property
    def description(self):
        return evetypes.GetDescription(self.type_id)

    @property
    def duration(self):
        return datetime.timedelta(days=self._data.durationDays)

    @property
    def hidden(self):
        return bool(self._data.esHidden)

    @property
    def retired(self):
        return bool(self._data.esRetired)

    @property
    def skills(self):
        return dict(self._data.skillsGranted)

    @property
    def associated_type_ids(self):
        if self._data.associatedShipTypes:
            return list(self._data.associatedShipTypes)
        return []

    @property
    def internal_name(self):
        return self._data.internalName

    def __eq__(self, other):
        return isinstance(other, ExpertSystem) and self.type_id == other.type_id

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.type_id)


def get_expert_systems(hidden = False, retired = False):
    return _filter_expert_systems(cache.all(), hidden, retired)


def is_expert_system(type_id):
    try:
        get_expert_system(type_id)
        return True
    except KeyError:
        return False


def get_expert_system(expert_system_id):
    return cache[expert_system_id]


def has_associated_expert_system(type_id, hidden = False, retired = False):
    return bool(get_associated_expert_systems(type_id, hidden, retired))


def get_associated_expert_systems(type_id, hidden = False, retired = False):
    return _filter_expert_systems(cache.associated_with(type_id), hidden, retired)


def _filter_expert_systems(expert_systems, hidden = False, retired = False):
    return filter(lambda expert_system: (not expert_system.hidden or hidden and expert_system.hidden) and (not expert_system.retired or retired and expert_system.retired), expert_systems)
