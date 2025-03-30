#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\gateLockMessenger.py
from datetime import datetime
import httplib
import logging
from eveProto.generated.eve_public.stargate.lock.api.notices_pb2 import RestrictedSystemsNotice, ActivatedNotice, DeactivatedNotice
from eveProto.generated.eve_public.stargate.lock.api.requests_pb2 import GetRequest, GetResponse, GetRestrictedSystemsRequest, GetRestrictedSystemsResponse
from stargate.common.lock_details import LockDetails
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)
TIMEOUT = 5

class ClientGateLockMessenger(object):

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self._restricted_systems_notice_callback = None
        self._activated_notice_callback = None
        self._deactivated_notice_callback = None

    def subscribe_to_restricted_systems_notice(self, callback):
        self._restricted_systems_notice_callback = callback
        self.public_gateway.subscribe_to_notice(RestrictedSystemsNotice, self._on_restricted_systems_notice)

    def _on_restricted_systems_notice(self, payload, primitive):
        solar_system_ids = [ entry.sequential for entry in payload.solarsystems ]
        self._restricted_systems_notice_callback(solar_system_ids)

    def subscribe_to_activated_lock_notice(self, callback):
        self._activated_notice_callback = callback
        self.public_gateway.subscribe_to_notice(ActivatedNotice, self._on_activated_notice)

    def _on_activated_notice(self, payload, primitive):
        lock_details = LockDetails(payload.solarsystem.sequential, payload.gate.sequential, payload.expiry.ToDatetime())
        self._activated_notice_callback(lock_details)

    def subscribe_to_deactivated_lock_notice(self, callback):
        self._deactivated_notice_callback = callback
        self.public_gateway.subscribe_to_notice(DeactivatedNotice, self._on_deactivated_notice)

    def _on_deactivated_notice(self, payload, primitive):
        lock_details = LockDetails(payload.solarsystem.sequential, payload.gate.sequential, datetime.now())
        self._deactivated_notice_callback(lock_details)

    def get_restricted_systems_request(self):
        request = GetRestrictedSystemsRequest()
        try:
            logger.info('Emanation Lock - get_restricted_systems_request:\nRequest: {request}'.format(request=request))
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetRestrictedSystemsResponse, TIMEOUT)
            response_primitive, payload = response_channel.receive()
            logger.info('Emanation Lock - get_restricted_systems_request returned: {status_code} - {payload}'.format(status_code=response_primitive.status_code, payload=payload))
            if response_primitive.status_code == httplib.NOT_FOUND:
                return []
            solar_systems = [ entry.sequential for entry in payload.solarsystems ]
            return solar_systems
        except TimeoutException:
            logger.error('Emanation Lock - get_restricted_systems_request timed out {request}'.format(request=request))
            return []
        except Exception as exception:
            logger.error('Emanation Lock - Error in get_restricted_systems_request {request} - {exception}'.format(request=request, exception=exception))
            return []

    def get_request(self):
        request = GetRequest()
        try:
            logger.info('Emanation Lock - get_request:\nRequest: {request}'.format(request=request))
            request_primitive, response_channel = self.public_gateway.send_character_request(request, GetResponse, TIMEOUT)
            response_primitive, payload = response_channel.receive()
            logger.info('Emanation Lock - get_request returned: {status_code} - {payload}'.format(status_code=response_primitive.status_code, payload=payload))
            if response_primitive.status_code == httplib.NOT_FOUND:
                return None
            return LockDetails(session.solarsystemid2, payload.gate.sequential, payload.expiry.ToDatetime())
        except TimeoutException:
            logger.error('Emanation Lock - get_request timed out {request}'.format(request=request))
            return None
        except Exception as exception:
            logger.error('Emanation Lock - Error in get_request {request} - {exception}'.format(request=request, exception=exception))
            return None
