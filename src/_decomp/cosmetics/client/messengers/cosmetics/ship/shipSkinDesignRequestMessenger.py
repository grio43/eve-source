#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\messengers\cosmetics\ship\shipSkinDesignRequestMessenger.py
import logging
import uuid
from cosmetics.client.ships.skins.errors import SkinDesignManagementError, GenericError, SkinDesignSharingError
from cosmetics.client.ships.skins.live_data.slot_layout import SlotLayout
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
from cosmetics.client.ships.skins.live_data.skin_design import SkinDesign
from eveProto.generated.eve_public.character.character_pb2 import Identifier as CharacterIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.draft.draft_pb2 import Identifier as DraftIdentifier
from eveProto.generated.eve_public.cosmetic.ship.skin.thirdparty.draft.api.requests_pb2 import GetRequest, GetResponse, GetSharedRequest, GetSharedResponse, GetAllSavedRequest, GetAllSavedResponse, GetSaveCapacityRequest, GetSaveCapacityResponse, SaveRequest, SaveResponse, DeleteRequest, DeleteResponse, UpdateRequest, UpdateResponse
_TIMEOUT_SECONDS = 3
logger = logging.getLogger(__name__)

class PublicShipSkinDesignRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_design_request(self, design_id):
        request = GetRequest(draft=DraftIdentifier(uuid=design_id.bytes))
        info_log = 'SKIN DESIGN MANAGEMENT - Get design {design_id} requested. '.format(design_id=design_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetResponse)
            if response_payload is None:
                info_log += 'Response: no design found'
                return
            design_hex = response_payload.draft.skin.hex
            info_log += 'Response: design fetched (design_id={design_id})'.format(design_id=design_id)
            return design_hex
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get design %s: %s', design_id, exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get design %s: %s', design_id, exc)
            raise
        finally:
            logger.info(info_log)

    def get_shared_design_request(self, design_id, character_id):
        request = GetSharedRequest(character=CharacterIdentifier(sequential=character_id), draft=DraftIdentifier(uuid=design_id.bytes))
        info_log = 'SKIN DESIGN MANAGEMENT - Get shared design {design_id} from {char_id} requested. '.format(design_id=design_id, char_id=character_id)
        try:
            response_primitive, response_payload = self._blocking_request(request, GetSharedResponse)
            if response_payload is None:
                info_log += 'Response: no design found'
                return (None, None)
            design_hex = response_payload.draft.skin.hex
            info_log += 'Response: design fetched (design_id={design_id})'.format(design_id=design_id)
            return (design_hex, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            if status_code == 404:
                return (None, SkinDesignSharingError.DESIGN_NOT_FOUND)
            logger.exception('Unexpected exception when requesting to get shared design %s (from char_id %s): %s', design_id, character_id, exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get shared design %s (from char_id %s): %s', design_id, character_id, exc)
            raise
        finally:
            logger.info(info_log)

    def get_all_saved_designs_request(self):
        request = GetAllSavedRequest()
        info_log = 'SKIN DESIGN MANAGEMENT - Get all saved designs requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetAllSavedResponse)
            if response_payload is None:
                info_log += 'Response: no saved designs found'
                return
            designs = response_payload.drafts
            info_log += 'Response: {amount} saved designs found'.format(amount=len(designs) if designs else 0)
            return {uuid.UUID(bytes=x.id.uuid):x.attributes.skin.hex for x in designs}
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to get saved designs: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to get saved designs: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def save_design_request(self, design):
        info_log = 'SKIN DESIGN MANAGEMENT - Save design requested:\n{design}. '.format(design=str(design))
        if not design.validate_layout():
            logger.info(info_log)
            return (None, None, SkinDesignManagementError.INVALID_DESIGN)
        request = SaveRequest(name=design.name, line_name=design.line_name, layout=SlotLayout.build_proto_from_layout(design.ship_type_id, design.slot_layout))
        logger.info('SKIN DESIGN MANAGEMENT: full proto %s' % request)
        logger.info('SKIN DESIGN MANAGEMENT: save request proto name: %s' % request.name)
        logger.info('SKIN DESIGN MANAGEMENT: save request proto line_name: %s' % request.line_name)
        logger.info('SKIN DESIGN MANAGEMENT: save request proto ship type: %s' % request.layout.ship_type.sequential)
        logger.info('SKIN DESIGN MANAGEMENT: save request proto nb filled slots: %s' % len(request.layout.slots))
        logger.info('SKIN DESIGN MANAGEMENT: save request proto slots: %s' % request.layout.slots)
        try:
            response_primitive, response_payload = self._blocking_request(request, SaveResponse)
            design_id = uuid.UUID(bytes=response_payload.id.uuid)
            design_hex = response_payload.attributes.skin.hex
            info_log += 'Response: design {design_id} saved. '.format(design_id=design_id)
            return (design_id, design_hex, None)
        except GenericException as exc:
            if exc.response_primitive.status_code == 403:
                info_log += 'MAX SAVED DESIGNS LIMIT REACHED'
                return (None, None, SkinDesignManagementError.MAX_SAVED_DESIGNS_LIMIT_REACHED)
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to save design: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to save design: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def update_design_request(self, design, design_id):
        info_log = 'SKIN DESIGN MANAGEMENT - Update design requested: {design_id}. '.format(design_id=design_id)
        if not design.validate_layout():
            return (None, SkinDesignManagementError.INVALID_DESIGN)
        if not design.name:
            return (None, SkinDesignManagementError.SKIN_NAME_MISSING)
        request = UpdateRequest(id=DraftIdentifier(uuid=design_id.bytes), name=design.name, line_name=design.line_name, layout=SlotLayout.build_proto_from_layout(design.ship_type_id, design.slot_layout))
        try:
            response_primitive, response_payload = self._blocking_request(request, UpdateResponse)
            info_log += 'Response: design {design_id} updated. '.format(design_id=design_id)
            return (response_payload.attributes.skin.hex, None)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to update design: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to update design: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def delete_design_request(self, design_id):
        request = DeleteRequest(id=DraftIdentifier(uuid=design_id.bytes))
        info_log = 'SKIN DESIGN MANAGEMENT - Delete design requested: {design_id}. '.format(design_id=design_id)
        try:
            self._blocking_request(request, DeleteResponse)
            info_log += 'Response: design {design_id} deleted. '.format(design_id=design_id)
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting to delete design: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to delete design: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def get_saved_designs_capacity_request(self):
        request = GetSaveCapacityRequest()
        info_log = 'SKIN DESIGN MANAGEMENT - Get design save capacity requested. '
        try:
            response_primitive, response_payload = self._blocking_request(request, GetSaveCapacityResponse)
            capacity = response_payload.capacity
            info_log += 'Response: save capacity fetched: {capacity}'.format(capacity=capacity)
            return capacity
        except GenericException as exc:
            status_code = exc.response_primitive.status_code
            info_log += 'ERROR (status_code={status_code})'.format(status_code=status_code)
            logger.exception('Unexpected exception when requesting design save capacity: %s', exc)
            raise
        except TimeoutException as exc:
            info_log += 'TIMED OUT'
            logger.exception('Timed out when requesting to save design capacity: %s', exc)
            raise
        finally:
            logger.info(info_log)

    def _blocking_request(self, request, response_class):
        request_primitive, response_channel = self.public_gateway.send_character_request(request, response_class, _TIMEOUT_SECONDS)
        response_primitive, payload = response_channel.receive()
        if response_primitive.status_code != 200:
            raise GenericException(request_primitive, response_primitive)
        return (response_primitive, payload)
