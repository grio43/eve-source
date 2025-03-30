#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\nes_intro.py
import carbonui.const as uiconst
import launchdarkly
import logging
from nodegraph.client.metrics import publish_datapoint_event
from storylines.common.nes_intro_constants import NesIntroState, NES_INTRO_NODE_GRAPH_ID
logger = logging.getLogger(__name__)

def is_nes_intro_active():
    return get_nes_intro_controller().is_nes_intro_active()


def is_nes_intro_completed():
    return get_nes_intro_controller().is_nes_intro_completed()


def skip_nes_intro(confirmation_dialog = 'SkipTutorialOffer'):
    return get_nes_intro_controller().skip_nes_intro(confirmation_dialog)


def is_nes_intro_enabled():
    return get_nes_intro_controller().is_nes_intro_enabled()


nes_intro_controller = None

def get_nes_intro_controller():
    global nes_intro_controller
    if nes_intro_controller is None:
        nes_intro_controller = NesIntroController()
    return nes_intro_controller


class NesIntroController(object):
    __notifyevents__ = ['OnNesIntroStateChanged']

    def __init__(self):
        self.cached_nes_intro_state_by_character = {}
        self.remote_nes_intro_controller = sm.RemoteSvc('nes_intro')
        self._is_nes_intro_enabled = None
        self._is_nes_intro_enabled_for_user = None
        sm.RegisterNotify(self)

    def is_nes_intro_enabled(self):
        if self._is_nes_intro_enabled is None:
            launchdarkly.get_client().notify_flag(flag_key='is-new-eden-store-intro-enabled', flag_fallback=True, callback=self._refresh_nes_intro_enabled)
        if self._is_nes_intro_enabled_for_user is None:
            launchdarkly.get_client().notify_flag(flag_key='new-eden-store-intro-enabled-for-user', flag_fallback=True, callback=self._refresh_nes_intro_enabled_for_user)
        return self._is_nes_intro_enabled and self._is_nes_intro_enabled_for_user

    def _refresh_nes_intro_enabled(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self._is_nes_intro_enabled = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)

    def _refresh_nes_intro_enabled_for_user(self, ld_client, flag_key, flag_fallback, flag_deleted):
        self._is_nes_intro_enabled_for_user = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)

    def OnNesIntroStateChanged(self, character_id, new_state_id):
        self.cached_nes_intro_state_by_character[character_id] = new_state_id

    def _get_nes_intro_state(self):
        if session.charid in self.cached_nes_intro_state_by_character:
            return self.cached_nes_intro_state_by_character[session.charid]
        state_id = self.remote_nes_intro_controller.get_nes_intro_state()
        self.cached_nes_intro_state_by_character[session.charid] = state_id
        return state_id

    def _is_at_nes_intro_state(self, state_id):
        return self._get_nes_intro_state() == state_id

    def _is_at_any_nes_intro_state(self, state_ids):
        return self._get_nes_intro_state() in state_ids

    def is_nes_intro_active(self):
        return self._is_at_nes_intro_state(NesIntroState.ACTIVE)

    def is_nes_intro_completed(self):
        return self._is_at_any_nes_intro_state([NesIntroState.COMPLETED, NesIntroState.SKIPPED])

    def skip_nes_intro(self, confirmation_dialog):
        if not self.is_nes_intro_active():
            return True
        if not confirmation_dialog or eve.Message(confirmation_dialog, buttons=uiconst.YESNO) == uiconst.ID_YES:
            try:
                is_skipped = self.remote_nes_intro_controller.skip_nes_intro()
                if is_skipped:
                    publish_datapoint_event('nes_intro_skipped_by_player', NES_INTRO_NODE_GRAPH_ID)
            except Exception as exc:
                logger.exception('Failed to skip tutorial: %s', exc)
                return False

        return True
