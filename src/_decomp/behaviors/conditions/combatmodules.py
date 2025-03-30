#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\combatmodules.py
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class IsModuleActive(Task):

    @TimedFunction('behaviors::conditions::combatmodules::IsModuleActive::OnEnter')
    def OnEnter(self):
        self.SetStatusToFailed()
        module_id = self._get_module_from_address()
        if not module_id:
            return
        if not self._is_module_active(module_id):
            return
        self.SetStatusToSuccess()

    def _get_module_from_address(self):
        return self.GetLastBlackboardValue(self.attributes.moduleAddress)

    def _is_module_active(self, module_id):
        return self.context.dogmaLM.IsItemActive(module_id)
