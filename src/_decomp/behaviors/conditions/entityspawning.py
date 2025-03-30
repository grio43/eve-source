#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\entityspawning.py
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class HasSpawnPointsGreaterThan(Task):

    @TimedFunction('behaviors::conditions::entityspawning::HasSpawnPointsGreaterThan::OnEnter')
    def OnEnter(self):
        spawn_pool_id = self.GetLastBlackboardValue(self.attributes.spawnPoolIdAddress)
        spawn_pool_manager = self._get_spawn_pool_manager()
        spawn_points = spawn_pool_manager.get_current_spawn_points(spawn_pool_id)
        self.SetStatusToSuccessIfTrueElseToFailed(spawn_points > self.attributes.minSpawnPointAmount)

    def _get_spawn_pool_manager(self):
        return self.context.entityLocation.GetSpawnPoolManager()
