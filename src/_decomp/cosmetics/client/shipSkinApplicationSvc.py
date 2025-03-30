#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\shipSkinApplicationSvc.py
import logging
import uthread2
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.client.ships.ship_skin_signals import on_skin_state_reapplied
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eveexceptions import UserError
logger = logging.getLogger(__name__)
_BUFFER_DURATION = 1
_instance = None

def get_ship_skin_application_svc():
    global _instance
    if _instance is None:
        _instance = _ShipSkinApplicationController()
    return _instance


class _ShipSkinApplicationController(object):
    __notifyevents__ = ['OnSessionChanged', 'OnSkinLicenseRemoved']

    def __init__(self):
        self._buffered_skin_changes = {}
        sm.RegisterNotify(self)

    def OnSessionChanged(self, _isRemote, _sess, change):
        if 'charid' in change:
            for ship_id in self._buffered_skin_changes.iterkeys():
                self._cancel_buffered_skin_change(ship_id)

    def OnSkinLicenseRemoved(self, _skin_id, ship_id, type_id):
        self.apply_first_party_skin(ship_id, type_id, None)

    def apply_first_party_skin(self, ship_id, hull_type_id, skin):
        self._buffer_skin_change(ship_id, ShipSkinType.FIRST_PARTY_SKIN, [hull_type_id, skin], apply_skin=skin is not None)

    def apply_third_party_skin(self, ship_id, license_id, apply_license, activate_license = False):
        if apply_license and activate_license:
            get_ship_skin_license_svc().activate_license(license_id)
        self._buffer_skin_change(ship_id, ShipSkinType.THIRD_PARTY_SKIN, license_id, apply_license)

    def _buffer_skin_change(self, ship_id, skin_type, skin_data, apply_skin):
        self._cancel_buffered_skin_change(ship_id)
        if skin_type == ShipSkinType.FIRST_PARTY_SKIN:
            skin_id = skin_data[1].skinID if len(skin_data) == 2 and skin_data[1] is not None else None
            logger.info('SKIN APPLICATION - buffering 1P skin change for ship id %s, skin id %s' % (ship_id, skin_id))
        elif skin_type == ShipSkinType.THIRD_PARTY_SKIN:
            skin_id = skin_data
            logger.info('SKIN APPLICATION - buffering 3P skin change for ship id %s, license id %s' % (ship_id, skin_id))
        self._buffered_skin_changes[ship_id] = uthread2.StartTasklet(self._perform_skin_change, ship_id, skin_type, skin_data, apply_skin)

    def _cancel_buffered_skin_change(self, ship_id):
        current_change = self._buffered_skin_changes.get(ship_id, None)
        if current_change is not None:
            try:
                current_change.kill()
                logger.info('SKIN APPLICATION - cancelled buffered skin change for ship id %s' % ship_id)
            except Exception as e:
                logger.exception('SKIN APPLICATION - error when cancelling buffered skin change: %s' % e)
            finally:
                if ship_id in self._buffered_skin_changes:
                    self._buffered_skin_changes.pop(ship_id)

    def _perform_skin_change(self, ship_id, skin_type, skin_data, apply_skin):
        try:
            uthread2.SleepSim(_BUFFER_DURATION)
            if skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                ship_type_id = skin_data[0]
                skin = skin_data[1]
                skin_id = skin.skinID if skin else None
                logger.info('SKIN APPLICATION - applying buffered 1P SKIN change for ship id %s, skin id %s' % (ship_id, skin_id))
                sm.GetService('cosmeticsSvc').InternalApplySkin(ship_id, ship_type_id, skin if apply_skin else None)
            elif skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                license_id = skin_data
                logger.info('SKIN APPLICATION - applying buffered 3P SKIN change for ship id %s, license id %s' % (ship_id, license_id))
                get_ship_skin_license_svc().apply_internal(license_id, ship_id, apply_skin)
        except UserError as e:
            if e.msg == 'SkinAlreadyApplied':
                on_skin_state_reapplied(ship_id)
            else:
                raise e
        except Exception as e:
            logger.exception('SKIN APPLICATION - Error when performing buffered skin change: %s' % e)
            raise e
        finally:
            if ship_id in self._buffered_skin_changes:
                self._buffered_skin_changes.pop(ship_id)
