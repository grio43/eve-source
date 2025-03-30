#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\structures.py
from behaviors.tasks import Task
from behaviors.utility.ballparks import get_ball
from ccpProfile import TimedFunction

class IsStructureVulnerable(Task):

    @TimedFunction('behaviors::conditions::structures::IsStructureVulnerable::OnEnter')
    def OnEnter(self):
        structure_id = self._get_structure_id()
        structure = get_ball(self, structure_id)
        self.SetStatusToSuccessIfTrueElseToFailed(structure.IsVulnerable())

    def _get_structure_id(self):
        return self.GetLastBlackboardValue(self.attributes.structureIdAddress)
