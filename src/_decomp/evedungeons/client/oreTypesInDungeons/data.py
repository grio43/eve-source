#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\oreTypesInDungeons\data.py
import blue
import cPickle
from fsdBuiltData.common.base import BuiltDataLoader
from logging import getLogger
logger = getLogger(__name__)

class OreTypesInDungeons(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/oreTypesByDungeonID.static'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/oreTypesByDungeonID.static'


def _get_ore_types_by_dungeon():
    return OreTypesInDungeons.GetData()


def get_ore_types_in_dungeon(dungeon_id):
    return _get_ore_types_by_dungeon().get(dungeon_id, [])


def get_asteroid_types_by_solar_system(solar_system_id):
    asteroid_types = getattr(get_asteroid_types_by_solar_system, '_asteroid_types', None)
    if asteroid_types is None:
        asteroid_types = _load_asteroid_types()
        get_asteroid_types_by_solar_system._asteroid_types = asteroid_types
    return asteroid_types.get(solar_system_id, [])


def _load_asteroid_types():
    result = {}
    res = blue.ResFile()
    res_path = 'res:/staticdata/asteroidTypesBySolarSystemID.pickle'
    if not res.open('%s' % res_path):
        logger.error('Could not load asteroid typeID pickle file: %s' % res_path)
    else:
        try:
            pickle_data = res.Read()
            result = cPickle.loads(pickle_data)
        finally:
            res.Close()

    return result
