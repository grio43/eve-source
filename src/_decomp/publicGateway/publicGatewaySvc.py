#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\publicGatewaySvc.py
import logging
import uuid
import jwt
import monolithconfig
from carbon.common.script.sys.service import Service
from clientRefreshToken.refresher import Refresher
from eve.client.script.sys.qaToolsForPublicGateway import PublicGatewayRequestHijacker
from eveProto import get_grpc_module
from monolithsentry import set_public_gateway_service_reference as set_monolithconfig_public_gateway_reference
from publicGateway.gateway import PublicGateway
from publicGateway.grpc.connectionConfig import ConnectionConfig
from publicGateway.grpc.eventPublisher import EventPublisher
from publicGateway.grpc.noticeConsumer import NoticeConsumer
from publicGateway.grpc.requestBroker import RequestBroker
from publicGateway.notice.notice_routing_cache import NoticeRoutingCache
from publicGateway.notice.signal_registry import NoticeSignalRegistry
logger = logging.getLogger('PublicGatewaySvc')

class PublicGatewaySvc(Service):
    __guid__ = 'svc.publicGatewaySvc'
    __displayname__ = 'Public Gateway Service'
    __notifyevents__ = ['OnSessionChanged']
    publicGateway = None
    eventPublishingDisabled = False
    refresher = None
    application_instance_uuid = uuid.uuid4()
    user_token_payload = None
    tenant = None

    def Run(self, mem_stream = None):
        self.tenant = monolithconfig.get_client_tenant()
        self.user_token_payload = monolithconfig.get_user_token()
        user_jwt = monolithconfig.get_user_jwt()
        try:
            self._initialize_public_gateway()
            if user_jwt:
                self.publicGateway.set_auth_token(user_jwt)
                self.publicGateway.connect()
            self._configure_refresher(self.user_token_payload, monolithconfig.get_refresh_token())
            monolithconfig.add_global_config_callback(self._refresh_config)
            set_monolithconfig_public_gateway_reference(self)
        except ImportError:
            self.LogError('Failed to initialize PublicGateway instance.')
            return

        self._qa_hijacker = PublicGatewayRequestHijacker(self)

    def _initialize_public_gateway(self):
        tier = monolithconfig.get_client_tier()
        build = monolithconfig.get_value('build', 'boot')
        codename = monolithconfig.get_value('codename', 'boot')
        origin = 'eve-desktop-client/{} {}'.format(str(build), str(codename))
        logger.debug('external_origin set to {}'.format(origin))
        grpc_module = get_grpc_module()
        connection_config = ConnectionConfig(logger, grpc_module, tier)
        connection = connection_config.connection
        grpc_module.set_application_instance_uuid(str(self.application_instance_uuid))
        sanitized_tenant = self.tenant.replace('.', '_').lower()
        event_publisher = EventPublisher(connection, sanitized_tenant, origin, self.application_instance_uuid.bytes)
        notice_signal_registry = NoticeSignalRegistry()
        notice_cache = NoticeRoutingCache()
        notice_consumer = NoticeConsumer(connection, notice_signal_registry, notice_cache, self.application_instance_uuid, session)
        requests_broker = RequestBroker(connection, sanitized_tenant, origin, self.application_instance_uuid)
        self.publicGateway = PublicGateway(grpc_module, connection_config, event_publisher, notice_signal_registry, notice_consumer, requests_broker)

    def _configure_refresher(self, user_token_payload, refresh_token):
        if not refresh_token:
            logger.warning("refresher hasn't been started because refresh token is not provided")
            return
        self.refresher = Refresher(user_token_payload, refresh_token)
        self.refresher.add_callback(self.publicGateway.set_auth_token)

    def _refresh_config(self):
        self.eventPublishingDisabled = monolithconfig.enabled('public_gateway_event_publishing_disabled')
        logger.info('Event Publishing Disabled: %s', self.eventPublishingDisabled)

    def get_gateway_uptime_ms(self):
        if self.publicGateway is None:
            return
        return self.publicGateway.get_uptime_ms()

    def get_notice_consumer_details(self):
        if self.publicGateway is None:
            return
        return self.publicGateway.get_notice_consumer_details()

    def get_event_publisher_rtt(self):
        if self.publicGateway is None:
            return -1
        return self.publicGateway.get_event_publisher_rtt()

    def get_event_publisher_details(self):
        if self.publicGateway is None:
            return
        return self.publicGateway.get_event_publisher_details()

    def publish_event(self, event_payload, journey_id = None):
        if self.publicGateway is None:
            return
        if self.eventPublishingDisabled:
            return
        self.publicGateway.publish_event(event_payload, journey_id=journey_id)

    def publish_event_payload(self, event_payload, journey_id = None):
        if self.publicGateway is None:
            return
        if self.eventPublishingDisabled:
            return
        self.publicGateway.publish_event_payload(event_payload, journey_id=journey_id)

    def get_request_broker_rtt(self):
        if self.publicGateway is None:
            return -1
        return self.publicGateway.get_request_broker_rtt()

    def get_request_broker_details(self):
        if self.publicGateway is None:
            return
        return self.publicGateway.get_request_broker_details()

    def send_character_request(self, request_payload, expected_response_class, timeout_seconds = None):
        if self.publicGateway is None:
            return
        request_primitive, response_channel = self.publicGateway.send_character_request(request_payload, expected_response_class, timeout_seconds)
        return (request_primitive, response_channel)

    def send_user_request(self, request_payload, expected_response_class, timeout_seconds = None):
        if self.publicGateway is None:
            return
        request_primitive, response_channel = self.publicGateway.send_user_request(request_payload, expected_response_class, timeout_seconds)
        return (request_primitive, response_channel)

    def send_blocking_user_request_and_receive_response(self, request_payload, expected_response_class, timeout_seconds, max_attempts, retry_delay_in_seconds):
        if self.publicGateway is None:
            return
        response_primitive, response_payload = self.publicGateway.send_blocking_user_request_and_receive_response(request_payload=request_payload, expected_response_class=expected_response_class, timeout_seconds=timeout_seconds, max_attempts=max_attempts, retry_delay_in_seconds=retry_delay_in_seconds)
        return (response_primitive, response_payload)

    def send_blocking_character_request_and_receive_response(self, request_payload, expected_response_class, timeout_seconds, max_attempts, retry_delay_in_seconds):
        if self.publicGateway is None:
            return
        response_primitive, response_payload = self.publicGateway.send_blocking_character_request_and_receive_response(request_payload=request_payload, expected_response_class=expected_response_class, timeout_seconds=timeout_seconds, max_attempts=max_attempts, retry_delay_in_seconds=retry_delay_in_seconds)
        return (response_primitive, response_payload)

    def update_active_identity(self, isRemote, session, change):
        if self.publicGateway is None:
            return
        if 'charid' in change:
            old, new = change['charid']
            self.publicGateway.set_active_character_id(session.charid)
            sm.ScatterEvent('OnActiveCharacterIdentitySet', old, new)
        if 'userid' in change:
            old, new = change['userid']
            self.publicGateway.set_authenticated_user_id(session.userid)
            if self.user_token_payload is None:
                logger.debug('user changed and there is no token, fabricating one')
                self.setup_local_dev_token(session.userid)
            try:
                self._qa_hijacker.load_data()
            except Exception as exc:
                logger.warning('Failed to load data for QA Hijacker: %s', exc)

            sm.ScatterEvent('OnAuthenticatedUserIdentitySet', old, new)
        self.publicGateway.session_changed(change)

    def setup_local_dev_token(self, user_id):
        token = jwt.fabricate_local_dev_user_token(self.tenant, user_id)
        self.publicGateway.set_auth_token(token)
        self.publicGateway.connect()

    def get_application_instance_uuid(self):
        return self.application_instance_uuid

    def subscribe_to_notice(self, notice, callback):
        if self.publicGateway is None:
            return
        self.publicGateway.subscribe_to_notice(notice, callback)

    def is_available(self):
        return self.publicGateway is not None

    def qa_enable_hijack_mode(self, error, latency):
        self._qa_hijacker.enable(error, latency)

    def qa_disable_hijack_mode(self):
        self._qa_hijacker.disable()

    def qa_get_hijack_mode_data(self):
        return self._qa_hijacker.get_data()

    OnSessionChanged = update_active_identity
