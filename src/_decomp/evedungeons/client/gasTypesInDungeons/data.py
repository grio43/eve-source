#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\gasTypesInDungeons\data.py
from fsdBuiltData.common.base import BuiltDataLoader

class GasTypesInDungeons(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/gasTypesByDungeonID.static'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/gasTypesByDungeonID.static'


def _get_gas_types_by_dungeon():
    return GasTypesInDungeons.GetData()


def get_gas_types_in_dungeon(dungeonID):
    return _get_gas_types_by_dungeon().get(dungeonID, [])
