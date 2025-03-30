#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\structureCosmeticStatesController.py
import launchdarkly
import uthread2
import log
from cosmetics.client.structures.fittingSignals import on_structure_cosmetic_state_changed
from cosmetics.common.structures.const import FLAG_PAINTWORK_SKINR_KILLSWITCH, FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT
from cosmetics.common.structures.fitting import StructurePaintwork
from cosmetics.client.messengers.cosmetics.structures.noticeMessenger import NoticeMessenger
from cosmetics.client.messengers.cosmetics.structures.requestMessenger import PublicRequestsMessenger
UPDATE_TIMEOUT_SECONDS = 1

class StructureCosmeticStatesController(object):

    def __init__(self, public_gateway):
        self._paintwork_cache = {}
        self._license_id_cache = {}
        self._update_thread = None
        self._last_solar_system_update_received = None
        self._notice_messenger = NoticeMessenger(public_gateway.publicGateway)
        self._notice_messenger.on_structure_cosmetic_state_changed_internal.connect(self._on_structure_cosmetic_state_changed)
        self._notice_messenger.on_structure_cosmetic_state_solar_system_update_internal.connect(self._on_solar_system_update)
        self._request_messenger = PublicRequestsMessenger(public_gateway.publicGateway)
        ld_client = launchdarkly.get_client()
        self._killswitch = FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT
        ld_client.notify_flag(FLAG_PAINTWORK_SKINR_KILLSWITCH, FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT, self._on_killswitch_changed)

    def shutdown(self):
        self._cancel_update()
        self._notice_messenger.on_structure_cosmetic_state_changed_internal.disconnect(self._on_structure_cosmetic_state_changed)
        self._notice_messenger.on_structure_cosmetic_state_solar_system_update_internal.disconnect(self._on_solar_system_update)

    def _flush_cache(self, structure_id = None):
        if structure_id:
            if structure_id in self._paintwork_cache:
                self._paintwork_cache.pop(structure_id)
            if structure_id in self._license_id_cache:
                self._license_id_cache.pop(structure_id)
        else:
            self._paintwork_cache = {}
            self._license_id_cache = {}

    def get_cached_cosmetic_state(self, structure_id):
        return self._paintwork_cache.get(structure_id, None)

    def get_cosmetic_state(self, structure_id, solar_system_id, force_refresh = False):
        if self._killswitch:
            return None
        else:
            if force_refresh or structure_id not in self._paintwork_cache:
                license_id, paintwork = self._request_messenger.get_request(structure_id, solar_system_id)
                if paintwork:
                    self._paintwork_cache[structure_id] = paintwork
                self._license_id_cache[structure_id] = license_id
            if structure_id in self._paintwork_cache:
                return self._paintwork_cache[structure_id]
            return None

    def get_cosmetic_license_id(self, structure_id, solar_system_id, force_refresh = False):
        if self._killswitch:
            return None
        if force_refresh or structure_id not in self._license_id_cache:
            license_id, _ = self._request_messenger.get_request(structure_id, solar_system_id)
            self._license_id_cache[structure_id] = license_id
        return self._license_id_cache[structure_id]

    def _get_all_in_solar_system(self):
        if self._killswitch:
            return None
        log.LogInfo('Structure Cosmetic States: manually fetching all structure cosmetic states in solar system %s' % session.solarsystemid2)
        paintworks = self._request_messenger.get_all_in_solar_system_request()
        if paintworks:
            for structure_id, paintwork in paintworks.iteritems():
                self._cache_cosmetic_state(structure_id, paintwork)

    def _on_structure_cosmetic_state_changed(self, structure_id, paintwork):
        if self._killswitch:
            return
        self._cache_cosmetic_state(structure_id, paintwork)

    def _on_solar_system_update(self, paintworks, solar_system_id):
        if self._killswitch:
            return
        log.LogInfo('Structure Cosmetic States: solar system %s update received, cancelling manual update thread' % session.solarsystemid2)
        self._last_solar_system_update_received = solar_system_id
        self._cancel_update()
        for structure_id, paintwork in paintworks.iteritems():
            self._cache_cosmetic_state(structure_id, paintwork)

    def _cache_cosmetic_state(self, structure_id, paintwork):
        self._paintwork_cache[structure_id] = paintwork
        on_structure_cosmetic_state_changed(structure_id, paintwork)

    def _on_killswitch_changed(self, ld_client, feature_key, fallback, _flagDeleted):
        self._killswitch = ld_client.get_bool_variation(feature_key=feature_key, fallback=fallback)
        for structure_id in self._paintwork_cache.iterkeys():
            on_structure_cosmetic_state_changed(structure_id, StructurePaintwork())

        self._flush_cache()

    def start_update(self, solar_system_id):
        self._cancel_update()
        if solar_system_id != self._last_solar_system_update_received:
            self._last_solar_system_update_received = None
            log.LogInfo('Structure Cosmetic States: beginning countdown for manual update for %s' % session.solarsystemid2)
            self._update_thread = uthread2.StartTasklet(self._structure_cosmetic_state_update_func)
        else:
            log.LogInfo('Structure Cosmetic States: skipping manual update for %s, notice was already received' % session.solarsystemid2)

    def _cancel_update(self):
        if self._update_thread:
            self._update_thread.kill()
            self._update_thread = None

    def _structure_cosmetic_state_update_func(self):
        uthread2.SleepSim(UPDATE_TIMEOUT_SECONDS)
        self._get_all_in_solar_system()
