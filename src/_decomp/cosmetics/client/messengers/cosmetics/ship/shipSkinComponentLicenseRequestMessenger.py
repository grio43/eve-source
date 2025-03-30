#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinComponentLicenseRequestMessenger.py
import logging
from cosmetics.client.ships.skins.live_data.component_license import ComponentLicense
from cosmetics.client.ships.skins.errors import ConsumeComponentItemFailed, ConsumeComponentItemConflict
from cosmetics.common.ships.skins.live_data.component_license_type import ComponentLicenseType
from publicGateway.grpc.exceptions import GenericException, RequestException
from stackless_response_router.exceptions import TimeoutException
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.api.requests_pb2 import GetOwnedRequest, GetOwnedResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.item.api.requests_pb2 import ConsumeRequest, ConsumeResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.requests_pb2 import GetRequest as GetFiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.requests_pb2 import GetResponse as GetFiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.admin.admin_pb2 import GrantRequest as GrantFiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.admin.admin_pb2 import GrantResponse as GrantFiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.admin.admin_pb2 import RevokeRequest as RevokeFiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.api.admin.admin_pb2 import RevokeResponse as RevokeFiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.requests_pb2 import GetRequest as GetInfiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.requests_pb2 import GetResponse as GetInfiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.admin.admin_pb2 import GrantRequest as GrantInfiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.admin.admin_pb2 import GrantResponse as GrantInfiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.admin.admin_pb2 import RevokeRequest as RevokeInfiniteRequest
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.api.admin.admin_pb2 import RevokeResponse as RevokeInfiniteResponse
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.finite.finite_pb2 import Identifier as FiniteLicenseIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.infinite.infinite_pb2 import Identifier as InfiniteLicenseIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.component.license.item.item_pb2 import Identifier as ItemIdentifier
from eveProto.generated.eve_public.inventory.generic_item_pb2 import Identifier as InventoryItemIdentifier
from httplib import CONFLICT
_TIMEOUT_SECONDS = 15
logger = logging.getLogger(__name__)

class PublicShipComponentLicenseRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_owned_licenses_request(self):
        request = GetOwnedRequest()
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - Get all owned component licenses requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetOwnedResponse)
            if response_payload is None:
                info_log += 'Response: no owned licenses found'
                return
            component_ids = {ComponentLicenseType.LIMITED: [ ComponentLicense.get_component_id_from_proto(x.component) for x in response_payload.finite ],
             ComponentLicenseType.UNLIMITED: [ ComponentLicense.get_component_id_from_proto(x.component) for x in response_payload.infinite ]}
            info_log += 'Response: {amount} owned licenses found'.format(amount=len(component_ids[ComponentLicenseType.LIMITED]) + len(component_ids[ComponentLicenseType.UNLIMITED]))
            return component_ids
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get owned component licenses: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get owned component licenses: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_finite_license_request(self, character_id, component_id, component_type):
        request = GetFiniteRequest(license=FiniteLicenseIdentifier(character=CharacterIdentifier(sequential=character_id), component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type)))
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - Get bound license requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetFiniteResponse)
            if response_payload is None:
                info_log += 'Response: no bound license found for component {component_id}'.format(component_id=component_id)
                return
            license = ComponentLicense.build_from_finite_proto(character_id, component_id, response_payload.license)
            info_log += 'Response: bound license found for component {component_id}'.format(component_id=component_id)
            return license
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            if status_code == 404:
                info_log += 'Bound license for component id {component_id} not found '.format(component_id=component_id)
                return
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get bound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get bound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_infinite_license_request(self, character_id, component_id, component_type):
        request = GetInfiniteRequest(license=InfiniteLicenseIdentifier(character=CharacterIdentifier(sequential=character_id), component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type)))
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - Get unbound license requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetInfiniteResponse)
            if response_payload is None:
                info_log += 'Response: no unbound license found for component {component_id}'.format(component_id=component_id)
                return
            license = ComponentLicense.build_from_infinite_proto(character_id, component_id, response_payload.license)
            info_log += 'Response: unbound license found for component {component_id}'.format(component_id=component_id)
            return license
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            if status_code == 404:
                info_log += 'Unbound license for component id {component_id} not found '.format(component_id=component_id)
                return
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get unbound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get unbound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def consume_request(self, item_id, quantity):
        request = ConsumeRequest(item=ItemIdentifier(item=InventoryItemIdentifier(sequential=item_id)), quantity=quantity)
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - Consume Item requested: {quantity} x item {item_id}. '.format(item_id=item_id, quantity=quantity)
        try:
            self._blocking_request(request, ConsumeResponse)
            info_log += 'Response: {quantity} x item {item_id} consumed successfully'.format(item_id=item_id, quantity=quantity)
            return
        except (GenericException, RequestException) as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            error_text = 'Failed to consume item (error:{status_code}): {exc}'.format(status_code=status_code, exc=exc)
            if status_code == CONFLICT:
                raise ConsumeComponentItemConflict(error_text)
            logger.exception('Unexpected exception when requesting to consume item: %s', exc)
            raise ConsumeComponentItemFailed(error_text)
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            error_text = 'Timed out when attempting to consume item: {exc}'.format(exc=exc)
            logger.exception(error_text)
            raise ConsumeComponentItemFailed(error_text)
        finally:
            logger.info(info_log)

    def admin_grant_finite_request(self, component_id, component_type, license_count):
        request = GrantFiniteRequest(component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type), capacity=license_count)
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - ADMIN - Grant x{count} bound license requested for component {id} '.format(count=license_count, id=component_id)
        try:
            self._blocking_request(request, GrantFiniteResponse)
            info_log += 'Response: bound license granted for component {component_id}'.format(component_id=component_id)
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to grant admin bound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to grant admin bound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_grant_infinite_request(self, component_id, component_type):
        request = GrantInfiniteRequest(component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type))
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - ADMIN - Grant unbound license requested for component {id} '.format(id=component_id)
        try:
            self._blocking_request(request, GrantInfiniteResponse)
            info_log += 'Response: unbound license granted for component {component_id}'.format(component_id=component_id)
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to grant admin unbound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to grant admin unbound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_revoke_finite_request(self, character_id, component_id, component_type):
        request = RevokeFiniteRequest(license=FiniteLicenseIdentifier(character=CharacterIdentifier(sequential=character_id), component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type)))
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - ADMIN - Revoke bound license requested for component {id} '.format(id=component_id)
        try:
            self._blocking_request(request, RevokeFiniteResponse)
            info_log += 'Response: bound license revoked for component {component_id}'.format(component_id=component_id)
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to revoke admin bound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to grant revoke bound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def admin_revoke_infinite_request(self, character_id, component_id, component_type):
        request = RevokeInfiniteRequest(license=InfiniteLicenseIdentifier(character=CharacterIdentifier(sequential=character_id), component=ComponentLicense.build_component_id_proto_from_component_id(component_id, component_type)))
        info_log = 'SKIN COMPONENT LICENSES MANAGEMENT - ADMIN - Revoke unbound license requested for component {id} '.format(id=component_id)
        try:
            self._blocking_request(request, RevokeInfiniteResponse)
            info_log += 'Response: unbound license revoked for component {component_id}'.format(component_id=component_id)
            return
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to revoke admin unbound license: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to grant revoke unbound license: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
