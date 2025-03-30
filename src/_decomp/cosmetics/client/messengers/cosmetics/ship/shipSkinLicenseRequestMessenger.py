#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinLicenseRequestMessenger.py
import logging
from carbon.common.script.sys.sessions import ThrottlePerSecond
from cosmetics.client.ships.skins.live_data.skin_license import SkinLicense
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.api.requests_pb2 import GetOwnedRequest, GetOwnedResponse, GetRequest, GetResponse, ActivateRequest, ActivateResponse, ApplyRequest, ApplyResponse, UnapplyRequest, UnapplyResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.api.admin.admin_pb2 import GrantRequest, GrantResponse, RevokeRequest, RevokeResponse
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.ship.ship_pb2 import Identifier as ShipIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.thirdparty_pb2 import Identifier as SkinIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.license.license_pb2 import Identifier as LicenseIdentifier
_TIMEOUT_SECONDS = 10
logger = logging.getLogger(__name__)

class PublicShipSkinLicenseRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_owned_request(self):
        request = GetOwnedRequest()
        info_log = 'SKIN LICENSES MANAGEMENT - Get all owned skin licenses requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetOwnedResponse)
            if response_payload is None:
                info_log += 'Response: no owned licenses found'
                return
            license_ids = [ x.skin.hex for x in response_payload.licenses ]
            info_log += 'Response: {amount} owned licenses found'.format(amount=len(license_ids))
            return license_ids
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get owned skin licenses: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get owned skin licenses: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_request(self, license_id, character_id):
        request = GetRequest(license=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=license_id)))
        info_log = 'SKIN LICENSES MANAGEMENT - Get skin license {license_id} requested. '.format(license_id=license_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetResponse)
            if response_payload is None:
                info_log += 'Response: no license data found'
                return
            license = SkinLicense.build_from_proto(response_payload.license, license_id, character_id)
            info_log += 'Response: license found'
            return license
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def activate_request(self, license_id, character_id):
        request = ActivateRequest(license=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=license_id)))
        info_log = 'SKIN LICENSES MANAGEMENT - Activate skin license {license_id} requested. '.format(license_id=license_id)
        try:
            self._blocking_request(request, ActivateResponse)
            info_log += 'Response: license activated'
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to activate skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to activate skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def apply_request(self, license_id, ship_id, character_id):
        request = ApplyRequest(license=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=license_id)), ship=ShipIdentifier(sequential=ship_id))
        info_log = 'SKIN LICENSES MANAGEMENT - Apply skin license {license_id} to ship {ship_id} requested. '.format(license_id=license_id, ship_id=ship_id)
        try:
            self._blocking_request(request, ApplyResponse)
            info_log += 'Response: license applied'
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to apply skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to apply skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def unapply_request(self, license_id, ship_id, character_id):
        request = UnapplyRequest(license=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=license_id)), ship=ShipIdentifier(sequential=ship_id))
        info_log = 'SKIN LICENSES MANAGEMENT - Unapply skin license {license_id} from ship {ship_id} requested. '.format(license_id=license_id, ship_id=ship_id)
        try:
            self._blocking_request(request, UnapplyResponse)
            info_log += 'Response: license applied'
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to unapply skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to unapply skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_grant_request(self, skin_hex, nb_licenses):
        request = GrantRequest(skin=SkinIdentifier(hex=skin_hex), unactivated=nb_licenses)
        info_log = 'SKIN LICENSES MANAGEMENT - ADMIN - Grant {count} x skin license {skin_hex} requested. '.format(skin_hex=skin_hex, count=nb_licenses)
        try:
            response_primitive, response_payload = self._blocking_request(request, GrantResponse)
            info_log += 'Response: admin license granted'
            return response_payload.license.skin.hex
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to grant admin skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to grant admin skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_revoke_request(self, skin_hex, character_id):
        request = RevokeRequest(license=LicenseIdentifier(character=CharacterIdentifier(sequential=character_id), skin=SkinIdentifier(hex=skin_hex)))
        info_log = 'SKIN LICENSES MANAGEMENT - ADMIN - Revoke skin license {skin_hex} requested. '.format(skin_hex=skin_hex)
        try:
            self._blocking_request(request, RevokeResponse)
            info_log += 'Response: admin license revoked'
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to revoke admin skin license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to revoke admin skin license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
