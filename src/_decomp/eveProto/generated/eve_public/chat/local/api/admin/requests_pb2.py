#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\chat\local\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.character import character_pb2 as eve__public_dot_character_dot_character__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/chat/local/api/admin/requests.proto', package='eve_public.chat.local.api.admin', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/chat/local/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n.eve_public/chat/local/api/admin/requests.proto\x12\x1feve_public.chat.local.api.admin\x1a$eve_public/character/character.proto\x1a\x1egoogle/protobuf/duration.proto"\x7f\n\x0bMuteRequest\x123\n\tcharacter\x18\x01 \x01(\x0b2 .eve_public.character.Identifier\x12+\n\x08duration\x18\x02 \x01(\x0b2\x19.google.protobuf.Duration\x12\x0e\n\x06reason\x18\x03 \x01(\t"\x0e\n\x0cMuteResponseBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/chat/local/api/adminb\x06proto3', dependencies=[eve__public_dot_character_dot_character__pb2.DESCRIPTOR, google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_MUTEREQUEST = _descriptor.Descriptor(name='MuteRequest', full_name='eve_public.chat.local.api.admin.MuteRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve_public.chat.local.api.admin.MuteRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='duration', full_name='eve_public.chat.local.api.admin.MuteRequest.duration', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='reason', full_name='eve_public.chat.local.api.admin.MuteRequest.reason', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=153, serialized_end=280)
_MUTERESPONSE = _descriptor.Descriptor(name='MuteResponse', full_name='eve_public.chat.local.api.admin.MuteResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=282, serialized_end=296)
_MUTEREQUEST.fields_by_name['character'].message_type = eve__public_dot_character_dot_character__pb2._IDENTIFIER
_MUTEREQUEST.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
DESCRIPTOR.message_types_by_name['MuteRequest'] = _MUTEREQUEST
DESCRIPTOR.message_types_by_name['MuteResponse'] = _MUTERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
MuteRequest = _reflection.GeneratedProtocolMessageType('MuteRequest', (_message.Message,), {'DESCRIPTOR': _MUTEREQUEST,
 '__module__': 'eve_public.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(MuteRequest)
MuteResponse = _reflection.GeneratedProtocolMessageType('MuteResponse', (_message.Message,), {'DESCRIPTOR': _MUTERESPONSE,
 '__module__': 'eve_public.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(MuteResponse)
DESCRIPTOR._options = None
