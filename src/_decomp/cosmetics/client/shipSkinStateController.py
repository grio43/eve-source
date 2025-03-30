#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinStateController.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from cosmetics.client.messengers.cosmetics.ship.shipSkinStateNoticeMessenger import ShipSkinStateNoticeMessenger
from cosmetics.client.messengers.cosmetics.ship.shipSkinStateRequestMessenger import ShipSkinStateRequestsMessenger
from cosmetics.client.ships.skins.live_data.ship_skin_state import ShipSkinState
from cosmetics.common.ships.skins.static_data.component import ComponentsDataLoader
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from cosmetics.client.ships.ship_skin_signals import *
from cosmetics.client.ships.ship_skin_svc_signals import *
from logging import getLogger
logger = getLogger(__name__)
_UPDATE_TIMEOUT_SECONDS = 3

class ShipSkinStateController(object):

    def __init__(self, public_gateway):
        self._cache = {}
        self._cached_waiting_list = {}
        self._notice_messenger = ShipSkinStateNoticeMessenger(public_gateway)
        self._request_messenger = ShipSkinStateRequestsMessenger(public_gateway)
        on_skin_state_set_internal.connect(self._on_skin_state_set)
        on_skin_state_set_all_in_bubble_internal.connect(self._on_skin_state_set_all_in_bubble)

    def shutdown(self):
        on_skin_state_set_internal.disconnect(self._on_skin_state_set)
        on_skin_state_set_all_in_bubble_internal.disconnect(self._on_skin_state_set_all_in_bubble)

    def on_character_changed(self):
        self.flush_cache()
        ComponentsDataLoader.load_components_data()

    def flush_cache(self):
        self._cache = {}
        self._cached_waiting_list = {}

    def _cache_state(self, skin_state):
        ship_id = skin_state.ship_instance_id
        old_skin_state = self._cache.get(ship_id, None)
        if ship_id in self._cached_waiting_list:
            self._cancel_wait(ship_id)
        if old_skin_state != skin_state:
            self._cache[ship_id] = skin_state
            logger.info('SKIN STATES - caching skin state %s' % skin_state)
            self._notify_of_skin_change(ship_id, skin_state, old_skin_state)
        else:
            on_skin_state_reapplied(ship_id)

    def _notify_of_skin_change(self, ship_id, skin_state, old_skin_state):
        on_skin_state_set(ship_id, skin_state)
        current_ship_id = session.shipid
        if current_ship_id and current_ship_id == ship_id:
            if skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                skin_id = skin_state.skin_data.skin_id
            elif skin_state.skin_type == ShipSkinType.NO_SKIN:
                skin_id = 0
            elif skin_state.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                skin_id = 0
            else:
                skin_id = 0
            if old_skin_state is not None:
                PlaySound(uiconst.SOUND_ADD_OR_USE)
            sm.ScatterEvent('OnCurrentShipSkinChange', ship_id, skin_id)

    def get_cached_skin_state(self, ship_instance_id, character_id):
        cached_state = self._cache.get(ship_instance_id, None)
        logger.info('SKIN STATES - requested cached state for %s, got %s' % (ship_instance_id, cached_state))
        if not cached_state:
            self._wait_for_notice(ship_instance_id, character_id)
        return cached_state

    def get_skin_state(self, ship_instance_id, character_id, force_refresh = False):
        if ship_instance_id not in self._cache or force_refresh:
            skin_state = self._request_messenger.get_request(ship_instance_id)
            if skin_state is None:
                logger.error('Failed to get SKIN state for ship %s, character %s', ship_instance_id, character_id)
                return
            self._cache_state(skin_state)
        return self._cache[ship_instance_id]

    def get_all_skin_states_in_bubble(self):
        skin_states = self._request_messenger.get_all_in_bubble_request()
        result = {}
        for skin_state in skin_states:
            self._cache_state(skin_state)
            result[skin_state.ship_instance_id] = skin_state

        return result

    def _on_skin_state_set(self, skin_state):
        self._cache_state(skin_state)

    def _on_skin_state_set_all_in_bubble(self, skin_states):
        for skin_state in skin_states:
            self._cache_state(skin_state)

    def _wait_for_notice(self, ship_instance_id, character_id):
        if ship_instance_id in self._cached_waiting_list:
            char_id, _ = self._cached_waiting_list[ship_instance_id]
            if character_id != char_id:
                self._cancel_wait(ship_instance_id)
            else:
                return
        self._cached_waiting_list[ship_instance_id] = (character_id, uthread2.StartTasklet(self._wait_thread, ship_instance_id, character_id))

    def _wait_thread(self, ship_instance_id, character_id):
        logger.info('SKIN STATES - Starting wait for skin state for ship id %s' % ship_instance_id)
        uthread2.SleepSim(_UPDATE_TIMEOUT_SECONDS)
        logger.info('SKIN STATES - Waiting is over, forcing request for skin state for ship id %s' % ship_instance_id)
        self._end_wait(ship_instance_id)
        self.get_skin_state(ship_instance_id, character_id, force_refresh=True)

    def _cancel_wait(self, ship_instance_id):
        if ship_instance_id in self._cached_waiting_list:
            logger.info('SKIN STATES - Cancelled wait for skin state for ship id %s' % ship_instance_id)
            self._end_wait(ship_instance_id)

    def _end_wait(self, ship_instance_id):
        if ship_instance_id in self._cached_waiting_list:
            char_id, thread = self._cached_waiting_list[ship_instance_id]
            if thread is not None:
                thread.kill()
            self._cached_waiting_list.pop(ship_instance_id)
