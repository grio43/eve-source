#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\service.py
from globalConfig import ShouldUseProjectDiscoveryNewDrawingTool
from projectdiscovery.client.baseservice import CommonProjectDiscoveryClientService

class CovidClientService(CommonProjectDiscoveryClientService):
    __notifyevents__ = CommonProjectDiscoveryClientService.__notifyevents__ + ['OnCharacterSessionChanged', 'OnGlobalConfigChanged']

    def Run(self, *args, **kwargs):
        super(CovidClientService, self).Run(*args, **kwargs)
        self.character_id = None
        self._is_tutorial_complete = None
        self._is_intro_complete = None
        self._is_flow_cytometer_intro_complete = None
        self._is_transition_complete = None
        self._sample_tutorial_step = -1
        self._is_new_drawing_tool_enabled = ShouldUseProjectDiscoveryNewDrawingTool(machoNet=sm.GetService('machoNet'))

    def OnCharacterSessionChanged(self, _oldCharacterID, _newCharacterID):
        if self.character_id != session.charid:
            self.character_id = session.charid
            self._is_tutorial_complete = self.remote_service.initialize_tutorial_status()
            self._is_intro_complete = self._is_tutorial_complete
            self._is_flow_cytometer_intro_complete = self._is_tutorial_complete
            self._is_transition_complete = self._is_tutorial_complete
            self._sample_tutorial_step = -1

    def OnGlobalConfigChanged(self, *args, **kwargs):
        self._is_new_drawing_tool_enabled = ShouldUseProjectDiscoveryNewDrawingTool(machoNet=sm.GetService('machoNet'))

    def should_use_new_drawing_tool(self):
        return self._is_new_drawing_tool_enabled

    def restart_all(self):
        self.remote_service.reset_tutorial()
        self._is_tutorial_complete = False
        self._is_intro_complete = False
        self._is_flow_cytometer_intro_complete = False
        self._is_transition_complete = False
        self._sample_tutorial_step = -1

    def complete_intro(self):
        self._is_intro_complete = True

    def is_intro_complete(self):
        return self._is_intro_complete

    def complete_flow_cytometer_intro(self):
        self._is_intro_complete = True
        self._is_flow_cytometer_intro_complete = True

    def is_flow_cytometer_intro_complete(self):
        return self._is_flow_cytometer_intro_complete

    def complete_transition(self):
        self._is_intro_complete = True
        self._is_flow_cytometer_intro_complete = True
        self._is_transition_complete = True

    def is_transition_complete(self):
        return self._is_transition_complete

    def go_to_next_sample_tutorial_step(self):
        self._is_intro_complete = True
        self._is_flow_cytometer_intro_complete = True
        self._is_transition_complete = True
        self._sample_tutorial_step += 1

    def go_to_sample_3_tutorial(self):
        self._is_tutorial_complete = False
        self._is_intro_complete = True
        self._is_flow_cytometer_intro_complete = True
        self._is_transition_complete = True
        self._sample_tutorial_step = 2

    def get_sample_tutorial_step(self):
        return self._sample_tutorial_step

    def is_tutorial_complete(self):
        if self._is_tutorial_complete is None:
            self._is_tutorial_complete = self.remote_service.get_tutorial_completion_status()
        return self._is_tutorial_complete

    def should_offer_retraining(self):
        if not self.is_tutorial_complete():
            return False
        has_ever_been_offered_to_retrain = settings.user.ui.Get('project_discovery_retraining_offered', False)
        if has_ever_been_offered_to_retrain:
            return False
        return True

    def disable_retraining_offer(self):
        settings.user.ui.Set('project_discovery_retraining_offered', True)

    def complete_tutorial(self):
        self._is_intro_complete = True
        self._is_flow_cytometer_intro_complete = True
        self._is_transition_complete = True
        self.remote_service.skip_tutorial()
        self._is_tutorial_complete = True
