#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\dungeons.py
from behaviors.tasks import Task
from behaviors.utility.dungeons import does_spawn_exist

class DungeonIsMyDungeonSpawnAlive(Task):

    def OnEnter(self):
        self.SetStatusToFailed()
        if hasattr(self.context, 'myDungeonSpawnId') and does_spawn_exist(self):
            self.SetStatusToSuccess()
