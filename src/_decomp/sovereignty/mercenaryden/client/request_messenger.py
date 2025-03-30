#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\request_messenger.py
from eveProto.generated.eve_public.sovereignty.mercenaryden.api.requests_pb2 import GetAsOwnerRequest, GetAsOwnerResponse, GetAllOwnedRequest, GetAllOwnedResponse, GetMaximumForCharacterRequest, GetMaximumForCharacterResponse
from eveProto.generated.eve_public.sovereignty.mercenaryden.activity.api.requests_pb2 import GetAllRequest, GetAllResponse, GetForMercenaryDenRequest, GetForMercenaryDenResponse, StartRequest, StartResponse, GetCapacityRequest, GetCapacityResponse
from httplib import OK, NOT_FOUND, CONFLICT, FORBIDDEN
from logging import getLogger
from sovereignty.mercenaryden.client.data.activity import MercenaryDenActivity
from sovereignty.mercenaryden.client.data.mercenary_den import MercenaryDenInfo
from sovereignty.mercenaryden.common.errors import GenericError, ServiceUnavailable, UnknownMercenaryDen, UnknownActivity, ActivityAlreadyStarted, ActivityValidationFailed, GetMaximumDensInternalError
from stackless_response_router.exceptions import TimeoutException, UnpackException
logger = getLogger('mercenary_den')
TIMEOUT_SECONDS = 2
TIMEOUT_SECONDS_GET_ALL_MERCENARY_DENS = 5

class PublicMercenaryDenRequestMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_mercenary_den_request(self, item_id):
        request = GetAsOwnerRequest()
        request.id.sequential = item_id
        info_log = 'Request: Get Mercenary Den {item_id}: {request}\n'.format(item_id=item_id, request=request)
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetAsOwnerResponse, TIMEOUT_SECONDS)
            response_primitive, response = response_channel.receive()
        except (TimeoutException, UnpackException) as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception when requesting to get Mercenary Den %s: %s', item_id, exc)
            raise ServiceUnavailable('Service failed to respond request for Mercenary Den %s: %s', item_id, exc)

        status_code = response_primitive.status_code
        info_log += 'Response: Get Mercenary Den {item_id}: ({status_code}) {response}'.format(item_id=item_id, status_code=status_code, response=response)
        logger.info(info_log)
        if status_code == OK:
            return MercenaryDenInfo.create_from_proto(item_id, response.attributes, response.enabled, response.evolution, response.infomorphs, response.cargo_extraction_enabled, response.skyhook_owner)
        if status_code == NOT_FOUND:
            raise UnknownMercenaryDen('Mercenary Den does not exist or caller is not owner and therefore has no visibility')
        else:
            raise GenericError('Unspecified error when fetching data for Mercenary Den: {code}'.format(code=status_code))

    def get_all_activities_request_without_retries(self):
        return self._get_all_activities_request(timeout_seconds=2, max_attempts=1, retry_delay_in_seconds=1)

    def get_all_activities_request_with_retries(self):
        return self._get_all_activities_request(timeout_seconds=5, max_attempts=10, retry_delay_in_seconds=0.5)

    def _get_all_activities_request(self, timeout_seconds, max_attempts, retry_delay_in_seconds):
        request = GetAllRequest()
        info_log = 'Request: Get All Mercenary Den Activites for player: {request}\n'.format(request=request)
        try:
            response_primitive, response = self.public_gateway.send_blocking_character_request_and_receive_response(request_payload=request, expected_response_class=GetAllResponse, timeout_seconds=timeout_seconds, max_attempts=max_attempts, retry_delay_in_seconds=retry_delay_in_seconds)
        except TimeoutException as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            raise ServiceUnavailable('Service timed out before responding to request GetAllRequest: %s' % exc)
        except UnpackException as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception GetAllRequest: %s', exc)
            raise GenericError('Service returned unexpected response format for GetAllRequest: %s' % exc)

        status_code = response_primitive.status_code
        if status_code != OK:
            raise GenericError('Unspecified error when fetching data for GetAllRequest: {code}'.format(code=status_code))
        activities = []
        for activity in response.activities:
            activities.append(MercenaryDenActivity.create_from_proto(activity))

        return activities

    def get_all_activities_for_den_request(self, item_id):
        request = GetForMercenaryDenRequest()
        request.mercenary_den.sequential = item_id
        info_log = 'Request: Get All Mercenary Den Activities for Den {id}: {request}\n'.format(id=item_id, request=request)
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetForMercenaryDenResponse, TIMEOUT_SECONDS)
            response_primitive, response = response_channel.receive()
        except (TimeoutException, UnpackException) as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception GetForMercenaryDenRequest: %s', exc)
            raise ServiceUnavailable('Service failed to respond to request GetForMercenaryDenRequest: %s', exc)

        status_code = response_primitive.status_code
        if status_code == NOT_FOUND:
            raise UnknownMercenaryDen('Mercenary Den does not exist or caller is not owner and therefore has no visibility')
        if status_code != OK:
            raise GenericError('Unspecified error when fetching data for GetForMercenaryDenRequest: {code}'.format(code=status_code))
        info_log += 'Response: %s' % response
        logger.info(info_log)
        activities = []
        for activity in response.activities:
            activities.append(MercenaryDenActivity.create_from_proto(activity))

        next_generation = response.next_generation_at.ToDatetime()
        return (activities, next_generation)

    def start_activity_request(self, activity_id):
        request = StartRequest()
        request.id.uuid = activity_id.bytes
        info_log = 'Request: Start Activity {id}: {request}\n'.format(id=activity_id, request=request)
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, StartResponse, TIMEOUT_SECONDS)
            response_primitive, response = response_channel.receive()
        except (TimeoutException, UnpackException) as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception StartRequest: %s', exc)
            raise ServiceUnavailable('Service failed to respond to request StartRequest: %s', exc)

        status_code = response_primitive.status_code
        if status_code == NOT_FOUND:
            raise UnknownActivity('Activity or associated mercenary den does not exist')
        if status_code == CONFLICT:
            raise ActivityAlreadyStarted('Activity has already been started')
        if status_code == FORBIDDEN:
            raise ActivityValidationFailed('Validation of activity has failed')
        if status_code != OK:
            raise GenericError('Unspecified error when fetching data for StartRequest: {code}'.format(code=status_code))
        return MercenaryDenActivity.create_from_id_and_attributes_proto(activity_id, response.attributes)

    def get_activity_capacity_request(self):
        request = GetCapacityRequest()
        info_log = 'Request: Get Activity Capacity Request: {request}\n'.format(request=request)
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetCapacityResponse, TIMEOUT_SECONDS)
            response_primitive, response = response_channel.receive()
        except (TimeoutException, UnpackException) as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception GetCapacityRequest: %s', exc)
            raise ServiceUnavailable('Service failed to respond to request GetCapacityRequest: %s', exc)

        status_code = response_primitive.status_code
        if status_code != OK:
            raise GenericError('Unspecified error when fetching data for GetCapacityRequest: {code}'.format(code=status_code))
        return response.capacity

    def get_all_owned_mercenary_dens_request(self):
        request = GetAllOwnedRequest()
        info_log = 'Request: Get all my Mercenary Dens: {request}\n'.format(request=request)
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetAllOwnedResponse, TIMEOUT_SECONDS_GET_ALL_MERCENARY_DENS)
            response_primitive, response = response_channel.receive()
        except TimeoutException as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            raise ServiceUnavailable('Service failed to respond request for my Mercenary Dens: %s' % exc)
        except UnpackException as exc:
            info_log += 'ERROR: {exc}'.format(exc=exc.__class__.__name__)
            logger.info(info_log)
            logger.exception('Unexpected exception when requesting to get my Mercenary Dens:', exc)
            raise GenericError('Service returned unexpected response format: %s' % exc)

        status_code = response_primitive.status_code
        if status_code != OK:
            raise GenericError('Unspecified error when fetching my mercenary dens: {code}'.format(code=status_code))
        item_ids = [ x.sequential for x in response.id ]
        return item_ids

    def get_maximum_dens_info_dens_request(self):
        request = GetMaximumForCharacterRequest()
        try:
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetMaximumForCharacterResponse, TIMEOUT_SECONDS)
            response_primitive, response = response_channel.receive()
        except (TimeoutException, UnpackException) as exc:
            logger.exception('Unexpected exception when requesting to get my max Mercenary Dens:', exc)
            raise ServiceUnavailable('Service failed to respond request for my max Mercenary Dens:', exc)

        status_code = response_primitive.status_code
        if status_code != OK:
            raise GetMaximumDensInternalError()
        return (response.current_maximum, response.absolute_maximum)
