#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\data.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import dungeonsLoader
except ImportError:
    dungeonsLoader = None

try:
    import dungeonObjectivesLoader
except ImportError:
    dungeonObjectivesLoader = None

class DungeonsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dungeons.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/dungeons.fsdbinary'
    __loader__ = dungeonsLoader


class DungeonObjectivesLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/dungeonObjectives.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/client/dungeonObjectives.fsdbinary'
    __loader__ = dungeonObjectivesLoader


def GetDungeons():
    return DungeonsLoader.GetData()


def GetDungeon(dungeonID):
    return GetDungeons().get(int(dungeonID), None)


def GetDungeonObjectivesData(dungeonID):
    dungeon = GetDungeon(dungeonID)
    if not dungeon or not dungeon.objectivesID:
        return
    allData = DungeonObjectivesLoader.GetData()
    data = allData.get(dungeon.objectivesID, None)
    if data:
        return data.clientObjectives
    else:
        return
