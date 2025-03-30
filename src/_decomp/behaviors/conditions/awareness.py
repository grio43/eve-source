#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\awareness.py
from behaviors.const.combat import THREAT_MAX_DISTANCE_FROM_GUARD_OBJECT
from behaviors.tasks import Task
from behaviors.utility.ballparks import is_ball_in_park, is_ball_in_range, is_ball_cloaked
from ccpProfile import TimedFunction

class AreClusterTargetsUsable(Task):

    @TimedFunction('behaviors::conditions::awareness::AreClusterTargetsUsable::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        guard_object_id = self._get_guard_object_id()
        if guard_object_id is None:
            return
        target_item_ids = self._get_cluster_targets()
        for item_id in target_item_ids:
            if self._is_target_valid(item_id, guard_object_id):
                self.SetStatusToSuccess()
                break

    def _get_cluster_targets(self):
        return self.GetLastBlackboardValue(self.attributes.clusterTargetSetAddress) or []

    def _get_guard_object_id(self):
        return self.GetLastBlackboardValue(self.attributes.guardObjectIdAddress)

    def _is_target_valid(self, item_id, guard_object_id):
        if not is_ball_in_park(self, item_id):
            return False
        if not is_ball_in_range(self, item_id, guard_object_id, THREAT_MAX_DISTANCE_FROM_GUARD_OBJECT):
            return False
        if is_ball_cloaked(self, item_id):
            return False
        return True
