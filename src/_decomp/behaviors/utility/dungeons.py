#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\dungeons.py


def does_spawn_exist(task):
    return task.context.keeper.DoesSpawnExist(task.context.myDungeonSpawnId)
