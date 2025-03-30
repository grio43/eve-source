#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\airnpe.py
import carbonui.const as uiconst
import logging
import uthread2
from eve.client.script.parklife.sceneManager import GetSceneManager
from storylines.client.metrics import send_metric
from storylines.common.airnpeconstants import AirNpeState, AIR_NPE_CLIENT_NODE_GRAPH_ID
from uihider import get_ui_hider
logger = logging.getLogger(__name__)

def is_air_npe_active():
    return get_air_npe_controller().is_air_npe_active()


def is_air_npe_focused():
    if not is_air_npe_active():
        return False
    node_graph = sm.GetService('node_graph').get_active_node_graph_by_id(AIR_NPE_CLIENT_NODE_GRAPH_ID)
    return bool(node_graph and node_graph.context.get_value('mission_focused'))


def is_air_npe_completed():
    return get_air_npe_controller().is_air_npe_completed()


def skip_air_npe(confirmation_dialog = 'ConfirmActionWhileTutorialActive'):
    return get_air_npe_controller().skip_air_npe(confirmation_dialog)


def is_air_npe_enabled():
    return get_air_npe_controller().is_air_npe_enabled()


air_npe_controller = None

def get_air_npe_controller():
    global air_npe_controller
    if air_npe_controller is None:
        air_npe_controller = AirNpeController()
    return air_npe_controller


class AirNpeController(object):
    __notifyevents__ = ['OnAirNpeStateChanged', 'OnGlobalConfigChanged']

    def __init__(self):
        self.cached_air_npe_state_by_character = {}
        self.remote_air_npe_controller = sm.RemoteSvc('air_npe')
        self._is_air_npe_enabled = None
        sm.RegisterNotify(self)

    def is_air_npe_enabled(self):
        if self._is_air_npe_enabled is None:
            self._is_air_npe_enabled = self.remote_air_npe_controller.is_air_npe_enabled()
        return self._is_air_npe_enabled

    def OnAirNpeStateChanged(self, character_id, new_state_id):
        self.cached_air_npe_state_by_character[character_id] = new_state_id
        if new_state_id in (AirNpeState.COMPLETED, AirNpeState.SKIPPED):
            get_ui_hider().reveal_everything()
            GetSceneManager().SwitchFromRestrictedCameraOnReset()
            uthread2.call_after_wallclocktime_delay(get_ui_hider().reveal_everything, 2)
        send_metric(new_state_id)

    def OnGlobalConfigChanged(self, *args, **kwargs):
        self._is_air_npe_enabled = self.remote_air_npe_controller.is_air_npe_enabled()
        if not self._is_air_npe_enabled:
            self.skip_air_npe(confirmation_dialog=False)

    def _get_air_npe_state(self):
        if session.charid in self.cached_air_npe_state_by_character:
            return self.cached_air_npe_state_by_character[session.charid]
        state_id = self.remote_air_npe_controller.get_air_npe_state()
        self.cached_air_npe_state_by_character[session.charid] = state_id
        return state_id

    def _is_at_air_npe_state(self, state_id):
        if not session.charid:
            return False
        return self._get_air_npe_state() == state_id

    def _is_at_any_air_npe_state(self, state_ids):
        if not session.charid:
            return False
        return self._get_air_npe_state() in state_ids

    def is_air_npe_active(self):
        return self._is_at_air_npe_state(AirNpeState.ACTIVE)

    def is_air_npe_completed(self):
        return self._is_at_any_air_npe_state([AirNpeState.COMPLETED, AirNpeState.SKIPPED])

    def skip_air_npe(self, confirmation_dialog):
        if not self.is_air_npe_active():
            return True
        if not confirmation_dialog or eve.Message(confirmation_dialog, buttons=uiconst.YESNO) == uiconst.ID_YES:
            try:
                self.remote_air_npe_controller.skip_air_npe()
            except Exception as exc:
                logger.exception('Failed to skip tutorial: %s', exc)

            return True
        return False
