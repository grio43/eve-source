#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\events\event.py
import uuid
from datetime import datetime
from eveProto.generated.eve_public.public_pb2 import Event as EvePublicEventProto
from eveProto.monolith_converters.time import datetime_to_timestamp

class Event(object):

    def __init__(self):
        self.protobuf_message = EvePublicEventProto()
        datetime_to_timestamp(datetime.utcnow(), self.protobuf_message.occurred)
        self.protobuf_message.uuid = uuid.uuid4().bytes

    def set_tenant(self, tenant):
        if not tenant:
            return
        self.protobuf_message.authoritative_context.tenant = tenant

    def set_journey_id(self, uuid_bytes):
        if not uuid_bytes:
            return
        self.protobuf_message.journey = uuid_bytes

    def set_application_instance_uuid(self, uuid_bytes):
        if not uuid_bytes:
            return
        self.protobuf_message.application_instance_uuid = uuid_bytes

    def set_active_character(self, character_id):
        self.protobuf_message.authoritative_context.ClearField('identity')
        if not character_id:
            self.protobuf_message.authoritative_context.no_active_identity = True
            return
        self.protobuf_message.authoritative_context.identity.character.sequential = character_id

    def set_external_origin(self, origin):
        self.protobuf_message.external_origin = origin

    def set_authenticated_user(self, user_id):
        self.protobuf_message.authoritative_context.ClearField('user')
        if not user_id:
            self.protobuf_message.authoritative_context.no_authenticated_user = True
            return
        self.protobuf_message.authoritative_context.authenticated_user.sequential = user_id
