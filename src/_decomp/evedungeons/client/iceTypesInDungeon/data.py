#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\iceTypesInDungeon\data.py
from fsdBuiltData.common.base import BuiltDataLoader

class IceTypesInDungeons(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/iceTypesByDungeonID.static'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/iceTypesByDungeonID.static'


def _get_ice_types_by_dungeon():
    return IceTypesInDungeons.GetData()


def get_ice_types_in_dungeon(dungeonID):
    return _get_ice_types_by_dungeon().get(dungeonID, [])
