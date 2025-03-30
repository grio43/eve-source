#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\client\local_chat\messenger.py
import uthread2
from chat.common.const import MemberClassification
from stackless_response_router.exceptions import TimeoutException
from signals import Signal
import logging
from eveProto.generated.eve_public.chat.local.api.requests_pb2 import BroadcastMessageRequest, BroadcastMessageResponse, GetMembershipListRequest, GetMembershipListResponse
from eveProto.generated.eve_public.chat.local.api.notices_pb2 import MembershipListNotice, MembershipRefreshedNotice, JoinNotice, LeaveNotice, MessageBroadcastNotice
from eveProto.generated.eve_public.chat.local.local_pb2 import Classification
CLASSIFICATION_RESOLVER = {Classification.CLASSIFICATION_UNSPECIFIED: MemberClassification.UNSPECIFIED,
 Classification.CLASSIFICATION_INVISIBLE: MemberClassification.INVISIBLE,
 Classification.CLASSIFICATION_DEVELOPER: MemberClassification.DEVELOPER,
 Classification.CLASSIFICATION_ADMINISTRATOR: MemberClassification.ADMINISTRATOR,
 Classification.CLASSIFICATION_GAMEMASTER: MemberClassification.GAME_MASTER,
 Classification.CLASSIFICATION_VOLUNTEER: MemberClassification.VOLUNTEER,
 Classification.CLASSIFICATION_NPC: MemberClassification.NPC}
from eveProto.generated.eve_public.chat.local.api.admin.requests_pb2 import MuteRequest, MuteResponse
on_message_broadcast_notice = Signal('local_chat.on_message_broadcast_notice')
on_exit_notice = Signal('local_chat.on_exit_notice')
on_membership_list_notice = Signal('local_chat.on_membership_list_notice')
on_membership_refreshed_notice = Signal('local_chat.on_membership_refreshed_notice')
on_join_notice = Signal('local_chat.on_join_notice')
logger = logging.getLogger('chat')

class LocalChatMessenger(object):
    _instance = None
    public_gateway_svc = None

    @classmethod
    def get_instance(cls, public_gateway):
        if not cls._instance:
            cls._instance = LocalChatMessenger(public_gateway)
        return cls._instance

    def __init__(self, public_gateway):
        self.public_gateway_svc = public_gateway
        self.public_gateway_svc.subscribe_to_notice(MessageBroadcastNotice, self.on_message_broadcast_notice)
        self.public_gateway_svc.subscribe_to_notice(LeaveNotice, self.on_exit_notice)
        self.public_gateway_svc.subscribe_to_notice(MembershipListNotice, self.on_membership_list_notice)
        self.public_gateway_svc.subscribe_to_notice(MembershipRefreshedNotice, self.on_membership_refreshed_notice)
        self.public_gateway_svc.subscribe_to_notice(JoinNotice, self.on_join_notice)

    def on_join_notice(self, payload, _primitive):
        on_join_notice(payload.solar_system.sequential, payload.member.character.sequential, self._format_member_data(payload.member))

    def on_exit_notice(self, payload, _primitive):
        on_exit_notice(payload.solar_system.sequential, payload.character.sequential)

    def on_message_broadcast_notice(self, payload, _primitive):
        on_message_broadcast_notice(payload.solar_system.sequential, payload.author.sequential, payload.message)

    def on_membership_list_notice(self, payload, _primitive):
        solar_system_id = payload.solar_system.sequential
        members = self.parse_members_from_payload(payload)
        on_membership_list_notice(solar_system_id, members)

    def on_membership_refreshed_notice(self, payload, _primitive):
        solar_system_id = payload.solar_system.sequential
        member_id = payload.member.character.sequential
        member_data = self._format_member_data(payload.member)
        on_membership_refreshed_notice(solar_system_id, member_id, member_data)

    def broadcast_message(self, message_content, response_callback, timeout_callback):
        request = BroadcastMessageRequest()
        request.message = message_content
        uthread2.StartTasklet(self.process_async_request, request, BroadcastMessageResponse, response_callback, timeout_callback)

    def request_solar_system_membership(self, response_callback, timeout_callback):
        request = GetMembershipListRequest()
        uthread2.StartTasklet(self.process_async_request, request, GetMembershipListResponse, response_callback, timeout_callback)

    def process_async_request(self, request, response_class, response_callback, timeout_callback):
        request_primitive = None
        try:
            request_primitive, response_channel = self.public_gateway_svc.send_character_request(request, response_class)
            response_primitive, payload = response_channel.receive()
            response_callback(payload, response_primitive)
        except TimeoutException as e:
            timeout_callback(e, request_primitive)
        except Exception as e:
            logger.exception(e)
            response_callback(None, None)

    def parse_members_from_payload(self, payload):
        return {member.character.sequential:self._format_member_data(member) for member in payload.members}

    def _format_member_data(self, member):
        return {'corporation_id': member.corporation.sequential,
         'alliance_id': member.alliance.sequential if member.HasField('alliance') else None,
         'war_faction_id': member.faction.sequential if member.HasField('faction') else None,
         'classification': CLASSIFICATION_RESOLVER[member.classification]}

    def mute_player(self, character_id, duration, reason, response_callback, timeout_callback):
        request = MuteRequest()
        request.character.sequential = character_id
        request.duration.seconds = duration
        request.reason = reason
        uthread2.StartTasklet(self.process_async_request, request, MuteResponse, response_callback, timeout_callback)
