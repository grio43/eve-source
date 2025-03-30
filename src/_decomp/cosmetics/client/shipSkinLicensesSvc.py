#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinLicensesSvc.py
import uthread
import logging
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from cosmetics.client.messengers.cosmetics.ship.shipSkinLicenseNoticeMessenger import PublicShipSkinLicenseNoticeMessenger
from cosmetics.client.messengers.cosmetics.ship.shipSkinLicenseRequestMessenger import PublicShipSkinLicenseRequestMessenger
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships import ship_skin_svc_signals
from cosmetics.client.ships.skins.errors import GetSkinLicensesFailed
from cosmetics.client.ships.skins.live_data.skin_license import SkinLicense
logger = logging.getLogger(__name__)
_instance = None

def get_ship_skin_license_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinLicensesController()
    return _instance


class _ShipSkinLicensesController(object):
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self):
        self._cache = {}
        self._owned_license_ids = []
        self._my_licenses_fetched_already = False
        self._licenses_flagged_as_new = set()
        public_gateway = sm.GetService('publicGatewaySvc')
        self._request_messenger = PublicShipSkinLicenseRequestMessenger(public_gateway)
        self._notice_messenger = PublicShipSkinLicenseNoticeMessenger(public_gateway)
        sm.RegisterNotify(self)
        ship_skin_svc_signals.on_skin_license_added_internal.connect(self._on_license_added)
        ship_skin_svc_signals.on_skin_license_updated_internal.connect(self._on_license_updated)
        ship_skin_svc_signals.on_skin_license_deleted_internal.connect(self._on_license_deleted)

    def __del__(self):
        ship_skin_svc_signals.on_skin_license_added_internal.disconnect(self._on_license_added)
        ship_skin_svc_signals.on_skin_license_updated_internal.disconnect(self._on_license_updated)
        ship_skin_svc_signals.on_skin_license_deleted_internal.disconnect(self._on_license_deleted)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            self._clear_cache()

    def _clear_cache(self):
        self._cache = {}
        self._owned_license_ids = []
        self._my_licenses_fetched_already = False
        self._licenses_flagged_as_new.clear()

    def get_my_licenses(self, force_refresh = False):
        owner_character_id = session.charid
        if force_refresh or not self._my_licenses_fetched_already:
            self._owned_license_ids = self._request_messenger.get_owned_request()
            exc = self._get_licenses_parallel(self._owned_license_ids, owner_character_id)
            if exc is None:
                self._my_licenses_fetched_already = True
            else:
                logger.exception(exc)
        return self._cache.get(owner_character_id, {})

    def get_my_activated_licenses(self, ship_type_id = None):
        licenses = self.get_my_licenses().values()
        if ship_type_id:
            return [ l for l in licenses if l.activated and l.skin_design.ship_type_id == ship_type_id ]
        return [ l for l in licenses if l.activated ]

    def get_my_unactivated_licenses(self):
        licenses = self.get_my_licenses().values()
        return [ l for l in licenses if l.nb_unactivated > 0 ]

    def get_my_licenses_that_are_available_to_use_or_sell(self):
        licenses = self.get_my_licenses().values()
        return [ l for l in licenses if l.nb_unactivated > 0 or l.activated ]

    def get_license(self, license_id, owner_character_id, force_refresh = False):
        if license_id not in self._cache.get(owner_character_id, {}) or force_refresh:
            license = self._request_messenger.get_request(license_id, owner_character_id)
            self._load_license_skin_data(license)
            if owner_character_id not in self._cache:
                self._cache[owner_character_id] = {}
            self._cache[owner_character_id][license_id] = license
        return self._cache.get(owner_character_id, {}).get(license_id, None)

    def activate_license(self, license_id):
        owner_character_id = session.charid
        self._request_messenger.activate_request(license_id, owner_character_id)
        if owner_character_id in self._cache and license_id in self._cache[owner_character_id]:
            self._cache[owner_character_id][license_id].activated = True
        ship_skin_signals.on_skin_license_activated(license_id)

    def admin_grant_license(self, skin_hex, nb_licenses):
        if session and session.role & ROLE_PROGRAMMER:
            self._request_messenger.admin_grant_request(skin_hex, nb_licenses)

    def admin_revoke_license(self, skin_hex):
        if session and session.role & ROLE_PROGRAMMER:
            self._request_messenger.admin_revoke_request(skin_hex, session.charid)

    def set_license_is_new_flag(self, license_id, is_new):
        if is_new:
            self._licenses_flagged_as_new.add(license_id)
        else:
            self._licenses_flagged_as_new.discard(license_id)

    def is_license_new(self, license_id):
        return license_id in self._licenses_flagged_as_new

    def apply_internal(self, license_id, ship_id, apply_license = True):
        if apply_license:
            self._request_messenger.apply_request(license_id, ship_id, session.charid)
        else:
            self._request_messenger.unapply_request(license_id, ship_id, session.charid)

    def _get_licenses_parallel(self, license_ids, owner_character_id, force_refresh = False):
        parallel_calls = []
        for license_id in license_ids:
            parallel_calls.append((self._get_license_no_exc, (license_id, owner_character_id, force_refresh)))

        results = uthread.parallel(parallel_calls)
        failed_licenses = [ (license_id, err_msg) for license_id, err_msg in results if err_msg is not None ] if results else []
        if len(failed_licenses) > 0:
            return GetSkinLicensesFailed(failed_licenses)

    def _get_license_no_exc(self, license_id, owner_character_id, force_refresh = False):
        try:
            self.get_license(license_id, owner_character_id, force_refresh)
            return (license_id, None)
        except Exception as e:
            return (license_id, e.message)

    def _load_license_skin_data(self, license):
        if license:
            license.load_skin_design()

    def _on_license_added(self, license_id, license_data):
        if license_data.owner_character_id not in self._cache:
            self._cache[license_data.owner_character_id] = {}
        self._cache[license_data.owner_character_id][license_id] = license_data
        self._load_license_skin_data(license_data)
        if license_data.owner_character_id == session.charid:
            self._owned_license_ids.append(license_id)
            self.set_license_is_new_flag(license_id, is_new=True)
        logger.info('SKIN LICENSES - License %s added, license data is %s' % (license_id, license_data))
        ship_skin_signals.on_skin_license_added(license_id, license_data)

    def _on_license_updated(self, license_id, license_data, previous_license_data):
        if license_data.owner_character_id not in self._cache:
            self._cache[license_data.owner_character_id] = {}
        self._load_license_skin_data(license_data)
        if license_id in self._cache[license_data.owner_character_id]:
            self._cache[license_data.owner_character_id][license_id].copy_from_other(license_data)
        else:
            self._cache[license_data.owner_character_id][license_id] = license_data
        if license_data.owner_character_id == session.charid:
            self._owned_license_ids.append(license_id)
            self._set_license_is_new_flag(license_id, license_data, previous_license_data)
        logger.info('SKIN LICENSES - License %s updated to %s' % (license_id, license_data))
        ship_skin_signals.on_skin_license_updated(license_id, license_data)

    def _set_license_is_new_flag(self, license_id, license_data, previous_license_data):
        did_aquire_unactivated_license = license_data.nb_unactivated > previous_license_data.nb_unactivated
        if did_aquire_unactivated_license:
            self.set_license_is_new_flag(license_id, is_new=True)

    def _on_license_deleted(self, license_id, owner_character_id):
        if owner_character_id in self._cache and license_id in self._cache[owner_character_id]:
            self._cache[owner_character_id].pop(license_id)
        if license_id in self._owned_license_ids:
            self._owned_license_ids.remove(license_id)
        logger.info('SKIN LICENSES - License %s deleted' % license_id)
        ship_skin_signals.on_skin_license_deleted(license_id)
