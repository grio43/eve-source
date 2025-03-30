#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\capture_Point_ui.py
import eveui
import gametime
import uthread2
from battleground_capture_point_ui.client.camera_facing_container import CameraFacingUiContainer
from battleground_capture_point_ui.client.capture_point_state.contested import Contested
from battleground_capture_point_ui.client.capture_point_state.empty import Empty
from battleground_capture_point_ui.client.capture_point_state.uncontested import UnContested
from battleground_capture_point_ui.client.distance_thresholded_camera_facing_ui_container import DistanceThreasholdedCameraFacingUiContainer
from battleground_capture_point_ui.client.state import StateMachine
from battleground_capture_point_ui.client.ui_container import TimerRingUIContainer
from carbon.common.lib.const import SEC
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.uicore import uicore
from dynamicresources.client.ess.bracket.camera import InFlightCameraReference

class CapturePointUI(object):
    CONTESTED = 1
    UNCONTESTED = 2
    EMPTY = 3
    GAUGE_ZERO_THRESHOLD = 0.99999
    __notifyevents__ = ('OnWarpActive',)

    def __init__(self, item_id):
        self.defenderId = None
        self.attackerId = None
        self._item_id = item_id
        self._closed = False
        self._status_update_token = None
        self._michelle = ServiceManager.Instance().GetService('michelle')
        self._scene_manager = ServiceManager.Instance().GetService('sceneManager')
        self._camera = InFlightCameraReference(self._scene_manager)
        self._state_machine = StateMachine()
        self._ui = None
        self.distance_thresholded_camera_facing_ui = None
        self.timer_ui_state = None
        self.nextTickTime = None
        self.totalTickTime = None
        self.timerStarted = False
        self.runTimerLoop = True
        self._init()

    def _init(self):
        ball = self._wait_for_ball()
        scene = self._scene_manager.GetRegisteredScene('default', allowBlocking=True)
        self._ui = TimerRingUIContainer(ball=ball, scene=scene, camera=self._camera)
        self.distance_thresholded_camera_facing_ui = DistanceThreasholdedCameraFacingUiContainer(parent=uicore.layer.space_ui, ball=ball, camera=self._camera, scene=scene)
        self.camera_facing_ui = CameraFacingUiContainer(parent=uicore.layer.space_ui, ball=ball, camera=self._camera, scene=scene)
        ServiceManager.Instance().RegisterNotify(self)

    def set_next_tick_time(self, nextTickTime, totalTickTime):
        self.totalTickTime = totalTickTime
        self.nextTickTime = nextTickTime
        if totalTickTime == 0 or totalTickTime is None:
            return
        if not self.timerStarted:
            self.timerStarted = True
            uthread2.start_tasklet(self._timer_update_loop)

    def set_state(self, remainingDuration, totalDuration, currentKing, state):
        if state == CapturePointUI.UNCONTESTED:
            self.distance_thresholded_camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.timer_ui_state = self._state_machine.move_to(UnContested(self._ui, self.distance_thresholded_camera_facing_ui._ui, self.camera_facing_ui._ui, remainingDuration, totalDuration, currentKing))
        elif state == CapturePointUI.CONTESTED:
            self.distance_thresholded_camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.timer_ui_state = self._state_machine.move_to(Contested(self._ui, self.distance_thresholded_camera_facing_ui._ui, self.camera_facing_ui._ui, self.defenderId))
        else:
            self.distance_thresholded_camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.camera_facing_ui.SetCameraThresholdingEnabled(False)
            self.timer_ui_state = self._state_machine.move_to(Empty(self._ui, self.distance_thresholded_camera_facing_ui._ui, self.camera_facing_ui._ui))

    def _timer_update_loop(self):
        while self.runTimerLoop:
            eveui.wait_for_next_frame()
            if self.timer_ui_state is not None and self.timer_ui_state.IsReady():
                new_gauge_value = 1.0 - self._get_proportion_capture_point_tick_time_left()
                if new_gauge_value > self.GAUGE_ZERO_THRESHOLD:
                    self.nextTickTime = gametime.GetSimTime() + self.totalTickTime * SEC
                    self.timer_ui_state.NotifyTimerReset()
                self.timer_ui_state.SetTimerValue(new_gauge_value, animate=False)

    def _get_proportion_capture_point_tick_time_left(self):
        if self.totalTickTime == 0 or self.totalTickTime is None:
            return 0.0
        now = gametime.GetSimTime()
        simTimeLeft = self.nextTickTime - now
        proportionLeft = float(simTimeLeft) / float(self.totalTickTime * SEC)
        return proportionLeft

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
        self.runTimerLoop = False
        self._closed = True

        def clean_up():
            if self._state_machine.state:
                self.distance_thresholded_camera_facing_ui._ui.Flush()
                self.camera_facing_ui._ui.Flush()
                self._state_machine.state.exit()
                eveui.wait_for_next_frame()
            self._ui.remove_from_space()
            self.distance_thresholded_camera_facing_ui.remove_from_space()
            self.camera_facing_ui.remove_from_space()

        uthread2.start_tasklet(clean_up)
