#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\analysisbeacon\client\analysis_beacon_ui.py
import eveui
import threadutils
import uthread2
from analysisbeacon.client.beacon_state.active import Active
from analysisbeacon.client.beacon_state.paused import Paused
from analysisbeacon.client.camera_facing_ui_container import BeaconCameraFacingUiContainer
from analysisbeacon.client.state import StateMachine
from analysisbeacon.client.beacon_ui_container import BeaconUiContainer
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference

class AnalysisBeaconUI:
    __notifyevents__ = ('OnWarpActive',)

    def __init__(self, item_id):
        self._item_id = item_id
        self._closed = False
        self._status_update_token = None
        self._michelle = ServiceManager.Instance().GetService('michelle')
        self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        self._camera = InFlightCameraReference(self._scene_manager)
        self._state_machine = StateMachine()
        self._ui = None
        self._camera_facing_ui = None
        self._init()

    @threadutils.threaded
    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default', allowBlocking=True)
        self._ui = BeaconUiContainer(ball=ball, scene=scene, camera=self._camera)
        self._camera_facing_ui = BeaconCameraFacingUiContainer(parent=uicore.layer.space_ui, ball=ball, camera=self._camera, scene=scene)
        ServiceManager.Instance().RegisterNotify(self)

    def set_state(self, remainingDuration, totalDuration, paused, active, complete):
        if complete:
            if self._state_machine.state:
                uthread2.start_tasklet(self._state_machine.state.exit)
        elif paused:
            uthread2.start_tasklet(self._state_machine.move_to, Paused(self._ui, self._camera_facing_ui._ui, remainingDuration, totalDuration))
        elif active:
            uthread2.start_tasklet(self._state_machine.move_to, Active(self._ui, self._camera_facing_ui._ui, remainingDuration, totalDuration))

    def _wait_for_ball(self):
        ball = None
        while ball is None:
            if self._closed:
                return
            ball = self._michelle.GetBall(self._item_id)
            if ball is not None:
                break
            eveui.wait_for_next_frame()

        return ball

    def remove_from_space(self):
        self._closed = True

        def clean_up():
            if self._state_machine.state:
                self._camera_facing_ui._ui.Flush()
                self._state_machine.state.exit()
                eveui.wait_for_next_frame()
            self._ui.remove_from_space()
            self._camera_facing_ui.remove_from_space()

        uthread2.start_tasklet(clean_up)
