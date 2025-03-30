#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\noticeConsumer.py
import logging
import uthread2
import uuid
from carbon.common.script.util.timerstuff import AutoTimer
from eveProto import get_grpc_module
from eveProto.module_states import channel_states, consumer_states
from launchdarkly.client.featureflag import create_integer_flag_check, create_boolean_flag_check
from publicGateway.grpc.streamLogger import StreamLogger
from publicGateway.notice.notice_routing_cache import UnhandledTargetGroupException, CacheOOMException
DEFAULT_AMOUNT_OF_NOTICES_AT_ONCE = 100
NOTICE_LOGGING_MSEC = 5000
NOTICE_CONSUMER_INFO_LOGGING_MSEC = 60000
NOTICE_CACHE_FLAG = 'eve_client_notice_consumer_validate_target_groups_cache_notices'

class NoticeConsumer(object):

    def __init__(self, connection, notice_registry, notice_cache, application_uuid, current_session):
        self.logger = logging.getLogger(__name__)
        self.native_consumer = self.get_native_consumer()
        self.native_consumer.set_connection(connection)
        self.stream_logger = StreamLogger(self.logger, self.native_consumer)
        self.notice_registry = notice_registry
        self.notice_cache = notice_cache
        self.application_uuid = application_uuid
        self.current_session = current_session
        self._notices_in_last_time_period = 0
        self._consume_calls_in_last_time_period = 0
        self._amount_of_notices_at_once = None
        self._amount_of_notices_at_once_getter = create_integer_flag_check(launchdarkly_key='client-notice-consumer-amount-of-notices-to-consume-at-once', fallback_value=DEFAULT_AMOUNT_OF_NOTICES_AT_ONCE, on_flag_changed_callback=self._on_amount_of_notices_at_once_changed)
        self._validate_and_cache_flag = create_boolean_flag_check(launchdarkly_key=NOTICE_CACHE_FLAG, fallback_value=False)
        uthread2.StartTasklet(self.consume_notices)
        self._log_notices_thread = AutoTimer(interval=NOTICE_LOGGING_MSEC, method=self.log_notices)
        self._log_notice_consumer_info_thread = AutoTimer(interval=NOTICE_CONSUMER_INFO_LOGGING_MSEC, method=self.log_notice_consumer_info)

    def get_native_consumer(self):
        grpc_module = get_grpc_module()
        if grpc_module is not None:
            self.logger.info('creating new notice consumer')
            return grpc_module.NoticeConsumer()

    def get_details(self):
        if self.native_consumer is None:
            return {'native_consumer': 'None'}
        last_status_code = -1
        last_status_code_stream_id = -1
        breadcrumbs = self.stream_logger.get_log_breadcrumbs()
        if len(breadcrumbs) > 0:
            last_status_code_stream_id = breadcrumbs[-1][0]
            last_status_code = breadcrumbs[-1][1]
        consumer_state_code = self.native_consumer.get_consumer_state()
        consumer_state_name = consumer_states.get(consumer_state_code, {'Name': 'undefined'})['Name']
        consumer_state_text = '{name} ({code})'.format(name=consumer_state_name, code=consumer_state_code)
        channel_state_code = self.native_consumer.get_channel_state()
        channel_state_name = channel_states.get(channel_state_code, {'Name': 'undefined'})['Name']
        channel_state_text = '{name} ({code})'.format(name=channel_state_name, code=channel_state_code)
        return {'consumer_state': consumer_state_text,
         'channel_state': channel_state_text,
         'connection_id': self.native_consumer.get_connection_id(),
         'stream_id': self.native_consumer.get_stream_id(),
         'stream_status_log_breadcrumbs': breadcrumbs,
         'last_status_code_stream_id': last_status_code_stream_id,
         'last_status_code': last_status_code}

    def consume_notices(self):
        while True:
            uthread2.sleep(0.001)
            if not self.native_consumer:
                return
            try:
                max_amount_of_messages_to_grab = self.amount_of_notices_at_once
                messages = self.native_consumer.get_messages(max_amount_of_messages_to_grab)
                for message in messages:
                    _, _, notice, _ = message
                    if self._validate_and_cache_flag():
                        uthread2.StartTasklet(self._validate_then_dispatch_or_cache, notice)
                    else:
                        uthread2.StartTasklet(self.notice_registry.invoke_signal_for_notice, notice)

                self._consume_calls_in_last_time_period += 1
                if messages:
                    self._notices_in_last_time_period += len(messages)
            except Exception as exc:
                self.logger.exception('Failed consuming notices: %s', exc)

    def _validate_then_dispatch_or_cache(self, notice):
        target_group, target_id = get_target_group_and_id(notice.target_group)
        valid, current_id = self._validate_target_group_against_session(target_group, target_id)
        if valid:
            uthread2.StartTasklet(self.notice_registry.invoke_signal_for_notice, notice)
        else:
            if target_group == 'application_instance_id':
                self.logger.error('NOTICE CONSUMER: Received a notice %s for application id %s when we are application id %s.', notice.payload.TypeName(), target_id, current_id)
            self.logger.info('NOTICE CONSUMER: Notice %s has an invalid target_group %s, id %s for its current id %s, caching to see if state changes shortly.', notice.payload.TypeName(), target_group, target_id, current_id)
            try:
                self.notice_cache.add_notice(notice, target_group, target_id)
            except UnhandledTargetGroupException:
                self.logger.warn('NOTICE CONSUMER: Got notice %s that has a target_group %s with id %s with current id %s that cannot be detected by the cache', notice.payload.TypeName(), target_group, target_id, current_id)
            except CacheOOMException:
                self.logger.warn('NOTICE CONSUMER: Notice Routing Cache is full and cannot evict to make room, discarding Notice %s that has a target_group %s with id %s', notice.payload.TypeName(), target_group, target_id)

    def log_notices(self):
        self.logger.info('NOTICE CONSUMER: Consumed %s notices (%s) from %s fetching calls to the consumer', 'some' if self._notices_in_last_time_period > 0 else 'no', self._notices_in_last_time_period, self._consume_calls_in_last_time_period)
        self._notices_in_last_time_period = 0
        self._consume_calls_in_last_time_period = 0

    def log_notice_consumer_info(self):
        self.logger.info('NOTICE CONSUMER: Details: %s', self.get_details())

    def connect(self):
        if self.connection_config:
            self.connection_config.connect()

    @property
    def amount_of_notices_at_once(self):
        if self._amount_of_notices_at_once is None:
            self._amount_of_notices_at_once = self._amount_of_notices_at_once_getter()
            self.logger.info('NOTICE CONSUMER: Retrieved config from LaunchDarkly. Amount of notices to consume at once: %s', self._amount_of_notices_at_once)
        return self._amount_of_notices_at_once

    def _on_amount_of_notices_at_once_changed(self, old_value, new_value):
        self._amount_of_notices_at_once = new_value
        self.logger.info('NOTICE CONSUMER: Updated config from LaunchDarkly. Amount of notices to consume at once: %s (was %s)', new_value, old_value)

    def _validate_target_group_against_session(self, target_group, target_id):
        current_id = None
        if target_group == 'application_instance_uuid':
            current_id = self.application_uuid
        elif target_group == 'solar_system':
            current_id = self.current_session.solarsystemid2
        elif target_group == 'user':
            current_id = self.current_session.userid
        elif target_group == 'character':
            current_id = self.current_session.charid
        elif target_group == 'corporation':
            current_id = self.current_session.corpid
        elif target_group == 'alliance':
            current_id = self.current_session.allianceid
        elif target_group == 'bubble_instance_uuid':
            return (True, target_id)
        return (target_id == current_id, current_id)

    def session_changed(self, change):
        notices = self.notice_cache.get_newly_valid_notices(change)
        for notice in notices:
            self.logger.info('NOTICE CONSUMER: Notice %s has become valid so dispatching it after caching.', notice.payload.TypeName())
            uthread2.StartTasklet(self.notice_registry.invoke_signal_for_notice, notice)


def get_target_group_and_id(target_group):
    target_group_name = target_group.WhichOneof('group')
    target_id = None
    if target_group_name == 'application_instance_uuid':
        target_id = uuid.UUID(bytes=target_group.application_instance_uuid)
    elif target_group_name == 'solar_system':
        target_id = target_group.solar_system
    elif target_group_name == 'user':
        target_id = target_group.user
    elif target_group_name == 'character':
        target_id = target_group.character
    elif target_group_name == 'corporation':
        target_id = target_group.corporation
    elif target_group_name == 'alliance':
        target_id = target_group.alliance
    elif target_group_name == 'bubble_instance_uuid':
        target_id = uuid.UUID(bytes=target_group.bubble_instance_uuid)
    return (target_group_name, target_id)
