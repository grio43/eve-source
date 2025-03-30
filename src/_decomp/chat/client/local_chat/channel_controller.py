#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\local_chat\channel_controller.py
import datetime
from carbon.common.script.sys.serviceConst import ROLE_CHTINVISIBLE
import sentry_sdk
from collections import deque
import httplib
import gametime
import logging
import localization
import uthread2
import uuid
from inventorycommon.const import ownerSystem
from eve.common.script.sys.idCheckers import IsEvePlayerCharacter
from eveprefs import prefs
from chat.common.util import is_local_chat_suppressed, is_local_chat_delayed
from chat.client.channel_controller import BaseChatChannelController
from chat.client.const import IDLE_MEMBER_REMOVAL_TIME
from .messenger import LocalChatMessenger, on_exit_notice, on_message_broadcast_notice, on_membership_list_notice, on_membership_refreshed_notice, on_join_notice
from ..hide_messages import open_hide_message_settings
from ..util import should_hide_message
WAIT_ON_MEMBERSHIP_NOTICE_SECONDS = 4
ENSURE_MEMBERS_MAX_DELAY = 60
logger = logging.getLogger('chat')

class LocalChatChannelController(BaseChatChannelController):
    __notifyevents__ = ['OnSessionChanged', 'ProcessSessionReset']

    def __init__(self, *args, **kwargs):
        self._character_id = None
        self._solar_system_id = None
        self._detailed_channel_id = None
        self._is_suppressed = True
        self._is_delayed = False
        self._initial_members_received = False
        self._member_request_tasklet = None
        self._member_activity_timestamp = {}
        self._member_activity_queue = deque()
        self._member_activity_tasklet = None
        self._ensure_membership_retry_count = 0
        self._ensure_membership_retry_start_time = None
        self._pending_member_data = {}
        self._pending_member_data_timestamp = None
        self._messenger = LocalChatMessenger.get_instance(sm.GetService('publicGatewaySvc'))
        super(LocalChatChannelController, self).__init__(*args, **kwargs)
        if session.charid:
            uthread2.start_tasklet(self._update_character_and_system, True)

    def close(self):
        super(LocalChatChannelController, self).close()
        self._messenger = None
        self._initial_members_received = True
        self._kill_member_request_tasklet()

    def _register(self):
        super(LocalChatChannelController, self)._register()
        on_message_broadcast_notice.connect(self._on_message_broadcast_notice)
        on_exit_notice.connect(self._on_exit_notice)
        on_membership_list_notice.connect(self._on_membership_list_notice)
        on_membership_refreshed_notice.connect(self._on_membership_refreshed_notice)
        on_join_notice.connect(self._on_join_notice)

    def _unregister(self):
        super(LocalChatChannelController, self)._unregister()
        on_message_broadcast_notice.disconnect(self._on_message_broadcast_notice)
        on_exit_notice.disconnect(self._on_exit_notice)
        on_membership_list_notice.disconnect(self._on_membership_list_notice)
        on_membership_refreshed_notice.disconnect(self._on_membership_refreshed_notice)
        on_join_notice.disconnect(self._on_join_notice)

    def ProcessSessionReset(self):
        if self._is_closing:
            return
        uthread2.start_tasklet(self._update_character_and_system, False)

    def OnSessionChanged(self, is_remote, session, change):
        if self._is_closing:
            return
        if 'charid' in change:
            if self._character_id != session.charid:
                self._update_character_id(ensure_members=True)
            else:
                self.chat_service.open_channel_window(self.channel_id)
        if 'solarsystemid2' in change:
            self._update_system_id(ensure_members='charid' not in change)

    def _update_character_and_system(self, ensure_members):
        self._update_character_id(ensure_members=ensure_members)
        self._update_system_id(ensure_members=False)

    def _update_character_id(self, ensure_members):
        if self._character_id == session.charid:
            return
        self._character_id = session.charid
        self._kill_member_request_tasklet()
        self._clear_members()
        self.clear_messages()
        self._close_logfile()
        if self._character_id:
            self._setup_log_file()
            if ensure_members:
                self._ensure_members_for_new_solar_system(wait_time=1)
                self.chat_service.open_channel_window(self.channel_id)

    def _update_system_id(self, ensure_members):
        if self._solar_system_id == session.solarsystemid2:
            return
        self._clear_member_activity()
        self._solar_system_id = session.solarsystemid2
        self._detailed_channel_id = '{}_{}'.format(self._channel_id, self._solar_system_id)
        self._is_suppressed = self._solar_system_id is None or is_local_chat_suppressed(self._solar_system_id)
        self._is_delayed = self._solar_system_id is not None and is_local_chat_delayed(self._solar_system_id)
        if not self._solar_system_id:
            return
        if self._is_delayed:
            self._member_activity_tasklet = uthread2.start_tasklet(self._remove_inactive_members_routine)
        self._clear_members()
        self._add_system_changed_message()
        self._add_invisible_role_message()
        added_pending = self._process_pending_member_data()
        if ensure_members and not added_pending:
            self._ensure_members_for_new_solar_system()

    @property
    def window_display_name(self):
        return localization.GetByLabel('UI/Chat/Local')

    @property
    def member_count(self):
        if self._is_suppressed or self._is_delayed:
            return 0
        return super(LocalChatChannelController, self).member_count

    @property
    def detailed_channel_id(self):
        return self._detailed_channel_id

    def set_members(self, members):
        if self._is_suppressed:
            return
        super(LocalChatChannelController, self).set_members(members)

    def add_member(self, character_id, character_info = None):
        if self._is_suppressed:
            return
        super(LocalChatChannelController, self).add_member(character_id, character_info)

    def send_chat_message(self, text):
        if self._is_suppressed:
            return None
        message_id = gametime.GetWallclockTime()
        self._add_to_messages(session.charid, text)
        self._add_pending_message(message_id)

        def _response_handler(payload, response):
            if response is None:
                self._remove_pending_message(message_id, was_delivered=False)
            elif response.status_code != httplib.OK:
                logger.error('LocalChat BroadcastMessageResponse returned with statusCode {}, statusMessage: {}'.format(response.status_code, response.status_message))
                self._remove_pending_message(message_id, was_delivered=False)
            else:
                self._remove_pending_message(message_id, was_delivered=True)

        def _timeout_handler(*args, **kwargs):
            self._remove_pending_message(message_id, was_delivered=False)

        self._messenger.broadcast_message(text, _response_handler, _timeout_handler)
        return message_id

    def should_hide_message(self, text):
        return should_hide_message(self.detailed_channel_id, self.category_id, text)

    def open_hide_message_settings(self):
        open_hide_message_settings(category_id=self.category_id, channel_id=self.detailed_channel_id, channel_name=self.channel_id)

    def _on_message_broadcast_notice(self, solar_system_id, sender_id, message_content):
        if self._is_closing or self._is_suppressed:
            return
        if solar_system_id != session.solarsystemid2:
            logger.warn('LocalChat on_message_broadcast_notice got bad solar_system_id=%d', solar_system_id)
            return
        if self._character_id != session.charid or session.charid is None:
            return
        self._update_member_activity(sender_id)
        if sender_id != session.charid:
            self.message_received(sender_id, message_content)

    def _on_membership_list_notice(self, solar_system_id, members):
        if self._is_closing:
            return
        if solar_system_id != session.solarsystemid2:
            logger.warn('LocalChat _on_membership_notice received bad solar_system_id=%d', solar_system_id)
            self._pending_member_data[solar_system_id] = members
            self._pending_member_data_timestamp = gametime.GetWallclockTime()
            return
        self._update_member_list(members)

    def _update_member_list(self, members):
        if self._is_closing:
            return
        chars_missing_corp_id = []
        for member_id, member_data in members.iteritems():
            if member_data['corporation_id'] == 0:
                chars_missing_corp_id.append(member_id)

        if len(chars_missing_corp_id) > 0:
            charSvc = sm.RemoteSvc('charMgr')
            fallback_data = charSvc.GetOrganizationInfoForCharacters(chars_missing_corp_id)
            for char_id, data in fallback_data.iteritems():
                members[char_id]['corporation_id'] = data.corporationID
                members[char_id]['alliance_id'] = data.allianceID
                members[char_id]['war_faction_id'] = data.warFactionID

            with sentry_sdk.configure_scope() as scope:
                scope.set_tag('solar_system_id', session.solarsystemid2)
                logger.exception('LocalChat _update_member_list received members with missing corporation_id. Requesting fallback data.', extra={'character_ids': chars_missing_corp_id,
                 'fallback_data': fallback_data})
                scope.remove_tag('solar_system_id')
        self._update_character_id(ensure_members=False)
        self._update_system_id(ensure_members=False)
        if session.charid is None:
            return
        self._initial_members_received = True
        self.set_members(members)

    def _on_membership_refreshed_notice(self, solar_system_id, member_id, member_data):
        if self._is_closing:
            return
        if solar_system_id != session.solarsystemid2:
            logger.warn('LocalChat _on_membership_refreshed_notice received bad solar_system_id=%d', solar_system_id)
            if solar_system_id in self._pending_member_data and member_id in self._pending_member_data[solar_system_id]:
                self._pending_member_data[solar_system_id][member_id] = member_data
            return
        if not self._is_delayed and member_id not in self._member_ids:
            return
        self.chat_service.update_members_info({member_id: member_data}, signal=True)

    def _on_join_notice(self, solar_system_id, character_id, character_info):
        if self._is_closing:
            return
        if solar_system_id != session.solarsystemid2:
            logger.warn('LocalChat _on_join_notice got bad solar_system_id=%d', solar_system_id)
            if solar_system_id in self._pending_member_data:
                self._pending_member_data[solar_system_id][character_id] = character_info
            return
        if self._character_id != session.charid or session.charid is None:
            return
        self.add_member(character_id, character_info)

    def _on_exit_notice(self, solar_system_id, character_id):
        if self._is_closing:
            return
        if solar_system_id != session.solarsystemid2:
            logger.warn('LocalChat _on_exit_notice got bad solar_system_id=%d', solar_system_id)
            if solar_system_id in self._pending_member_data:
                self._pending_member_data[solar_system_id].pop(character_id, None)
            return
        if self._character_id != session.charid or session.charid is None:
            return
        self.remove_member(character_id)

    def _process_pending_member_data(self):
        added = False
        if self._solar_system_id in self._pending_member_data and gametime.GetSecondsSinceWallclockTime(self._pending_member_data_timestamp) < 5:
            added = True
            self._update_member_list(self._pending_member_data[self._solar_system_id])
        self._pending_member_data.clear()
        self._pending_member_data_timestamp = None
        return added

    def _ensure_members_for_new_solar_system(self, wait_time = None):
        self._initial_members_received = False
        self._kill_member_request_tasklet()
        self._member_request_tasklet = uthread2.StartTasklet(self._ensure_members_for_new_solar_system_tasklet, WAIT_ON_MEMBERSHIP_NOTICE_SECONDS if wait_time is None else wait_time)

    def _ensure_members_for_new_solar_system_tasklet(self, wait_time = None):
        if wait_time:
            uthread2.sleep(wait_time)
        if self._is_closing or session.charid is None or self._initial_members_received:
            return
        logger.info('LocalChat timeout waiting on membership notice for solar_system_id=%d', session.solarsystemid2)
        self._messenger.request_solar_system_membership(self._ensure_members_membership_response_callback, self._ensure_membership_timeout_callback)

    def _ensure_members_membership_response_callback(self, payload, response):
        if self._is_closing or self._initial_members_received or response is None:
            return
        if response.status_code != 200:
            logger.error('LocalChat error in response for solar system membership request', extra={'status_code': response.status_code,
             'status_message': response.status_message})
            return
        self._ensure_membership_retry_count = 0
        self._ensure_membership_retry_start_time = None
        solar_system_id = payload.solar_system.sequential
        members = self._messenger.parse_members_from_payload(payload)
        self._on_membership_list_notice(solar_system_id, members)

    def _ensure_membership_timeout_callback(self, error, request_primitive):
        if self._is_closing or self._initial_members_received:
            return
        public_gateway_service = sm.GetService('publicGatewaySvc')
        logger.error('LocalChat request for membership list timed out', extra={'error': error,
         'request_broker_details': public_gateway_service.get_request_broker_details(),
         'notice_consumer_details': public_gateway_service.get_notice_consumer_details(),
         'public_gateway_svc_uptime_ms': public_gateway_service.get_gateway_uptime_ms(),
         'request_correlation_uuid': str(uuid.UUID(bytes=request_primitive.correlation_uuid)) if request_primitive else ''})
        if self._ensure_membership_retry_start_time is None:
            self._ensure_membership_retry_start_time = datetime.datetime.now()

        def get_wait_time(retry_count):
            if retry_count <= 1:
                return WAIT_ON_MEMBERSHIP_NOTICE_SECONDS
            return min(ENSURE_MEMBERS_MAX_DELAY, get_wait_time(retry_count - 1) * 2)

        if datetime.datetime.now() - self._ensure_membership_retry_start_time < datetime.timedelta(minutes=5):
            self._ensure_membership_retry_count += 1
            self._ensure_members_for_new_solar_system(wait_time=get_wait_time(self._ensure_membership_retry_count))
        else:
            logger.error('LocalChat failed to get membership list after {} retries'.format(self._ensure_membership_retry_count))
            self._ensure_membership_retry_start_time = None
            self._ensure_membership_retry_count = 0

    def _add_system_changed_message(self):
        if self._is_suppressed:
            system_name = localization.GetByLabel('UI/Chat/Unknown')
        else:
            system_name = cfg.evelocations.Get(session.solarsystemid2).name
        channel_name = localization.GetByLabel('UI/Chat/FeatureChannelName', featureType=localization.GetByLabel('UI/Chat/Local'), featureName=system_name)
        self.add_game_message(localization.GetByLabel('UI/Chat/ChannelWindow/ChannelChangedToChannelName', channelName=channel_name), sender_id=ownerSystem)

    def _add_invisible_role_message(self):
        if session.role & ROLE_CHTINVISIBLE == ROLE_CHTINVISIBLE:
            self.add_game_message(localization.GetByLabel('UI/Chat/InvisibleWarning', color='#ffffff00'), sender_id=ownerSystem)

    def _update_member_activity(self, member_id):
        if not IsEvePlayerCharacter(member_id):
            return
        self.add_member(member_id)
        if self._is_delayed:
            timestamp = gametime.GetWallclockTime()
            self._member_activity_timestamp[member_id] = timestamp
            self._member_activity_queue.append((timestamp, member_id))

    def _remove_inactive_members_routine(self):
        while self._is_delayed:
            now = gametime.GetWallclockTime()
            inactive_member_ids = []
            max_activity_seconds = prefs.GetValue('chat_idle_character_removal_period', IDLE_MEMBER_REMOVAL_TIME)
            sleep_duration = max_activity_seconds
            while len(self._member_activity_queue) > 0:
                activity_timestamp, member_id = self._member_activity_queue[0]
                if self._member_activity_timestamp[member_id] != activity_timestamp:
                    self._member_activity_queue.popleft()
                    continue
                time_since_activity = gametime.GetTimeDiff(activity_timestamp, now) / gametime.SEC
                if time_since_activity > max_activity_seconds:
                    self._member_activity_queue.popleft()
                    inactive_member_ids.append(member_id)
                else:
                    sleep_duration = max_activity_seconds - time_since_activity + 1
                    break

            for character_id in inactive_member_ids:
                self.remove_member(character_id)

            uthread2.sleep(sleep_duration)

    def _kill_member_request_tasklet(self):
        if self._member_request_tasklet:
            self._member_request_tasklet.kill()
            self._member_request_tasklet = None

    def _clear_member_activity(self):
        if self._member_activity_tasklet:
            self._member_activity_tasklet.kill()
            self._member_activity_tasklet = None
        self._member_activity_timestamp.clear()
        self._member_activity_queue.clear()

    def mute_player(self, character_id, duration, reason):
        self._messenger.mute_player(character_id, duration, reason, self._mute_player_response_callback, self._mute_player_timeout_callback)

    def _mute_player_response_callback(self, payload, response):
        if response is None:
            return
        if response.status_code != httplib.OK:
            logger.error('LocalChat MuteResponse returned with statusCode {}, statusMessage: {}'.format(response.status_code, response.status_message))

    def _mute_player_timeout_callback(self, error, request_primitive):
        public_gateway_service = sm.GetService('publicGatewaySvc')
        logger.error('LocalChat request to mute player timed out', extra={'error': error,
         'request_broker_details': public_gateway_service.get_request_broker_details(),
         'notice_consumer_details': public_gateway_service.get_notice_consumer_details(),
         'public_gateway_svc_uptime_ms': public_gateway_service.get_gateway_uptime_ms(),
         'request_correlation_uuid': str(uuid.UUID(bytes=request_primitive.correlation_uuid)) if request_primitive else ''})
