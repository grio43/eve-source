#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\chat\local\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.chat.local import local_pb2 as eve_dot_chat_dot_local_dot_local__pb2
from eveProto.generated.eve.quasar.admin import admin_pb2 as eve_dot_quasar_dot_admin_dot_admin__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/chat/local/api/admin/requests.proto', package='eve.chat.local.api.admin', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/chat/local/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/chat/local/api/admin/requests.proto\x12\x18eve.chat.local.api.admin\x1a\x1deve/character/character.proto\x1a\x1aeve/chat/local/local.proto\x1a\x1ceve/quasar/admin/admin.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1egoogle/protobuf/duration.proto"\xa4\x01\n\x0bMuteRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12+\n\x08duration\x18\x02 \x01(\x0b2\x19.google.protobuf.Duration\x12\x0e\n\x06reason\x18\x03 \x01(\t\x12*\n\x07context\x18\x04 \x01(\x0b2\x19.eve.quasar.admin.Context"\x0e\n\x0cMuteResponse"\x93\x01\n\x0eSetModeRequest\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12"\n\x04mode\x18\x02 \x01(\x0e2\x14.eve.chat.local.Mode\x12*\n\x07context\x18\x03 \x01(\x0b2\x19.eve.quasar.admin.Context"\x11\n\x0fSetModeResponseBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/chat/local/api/adminb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_chat_dot_local_dot_local__pb2.DESCRIPTOR,
 eve_dot_quasar_dot_admin_dot_admin__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_MUTEREQUEST = _descriptor.Descriptor(name='MuteRequest', full_name='eve.chat.local.api.admin.MuteRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.chat.local.api.admin.MuteRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='duration', full_name='eve.chat.local.api.admin.MuteRequest.duration', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reason', full_name='eve.chat.local.api.admin.MuteRequest.reason', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.chat.local.api.admin.MuteRequest.context', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=226, serialized_end=390)
_MUTERESPONSE = _descriptor.Descriptor(name='MuteResponse', full_name='eve.chat.local.api.admin.MuteResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=392, serialized_end=406)
_SETMODEREQUEST = _descriptor.Descriptor(name='SetModeRequest', full_name='eve.chat.local.api.admin.SetModeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.chat.local.api.admin.SetModeRequest.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='mode', full_name='eve.chat.local.api.admin.SetModeRequest.mode', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='context', full_name='eve.chat.local.api.admin.SetModeRequest.context', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=409, serialized_end=556)
_SETMODERESPONSE = _descriptor.Descriptor(name='SetModeResponse', full_name='eve.chat.local.api.admin.SetModeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=558, serialized_end=575)
_MUTEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MUTEREQUEST.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_MUTEREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
_SETMODEREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_SETMODEREQUEST.fields_by_name['mode'].enum_type = eve_dot_chat_dot_local_dot_local__pb2._MODE
_SETMODEREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['MuteRequest'] = _MUTEREQUEST
DESCRIPTOR.message_types_by_name['MuteResponse'] = _MUTERESPONSE
DESCRIPTOR.message_types_by_name['SetModeRequest'] = _SETMODEREQUEST
DESCRIPTOR.message_types_by_name['SetModeResponse'] = _SETMODERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
MuteRequest = _reflection.GeneratedProtocolMessageType('MuteRequest', (_message.Message,), {'DESCRIPTOR': _MUTEREQUEST,
 '__module__': 'eve.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(MuteRequest)
MuteResponse = _reflection.GeneratedProtocolMessageType('MuteResponse', (_message.Message,), {'DESCRIPTOR': _MUTERESPONSE,
 '__module__': 'eve.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(MuteResponse)
SetModeRequest = _reflection.GeneratedProtocolMessageType('SetModeRequest', (_message.Message,), {'DESCRIPTOR': _SETMODEREQUEST,
 '__module__': 'eve.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(SetModeRequest)
SetModeResponse = _reflection.GeneratedProtocolMessageType('SetModeResponse', (_message.Message,), {'DESCRIPTOR': _SETMODERESPONSE,
 '__module__': 'eve.chat.local.api.admin.requests_pb2'})
_sym_db.RegisterMessage(SetModeResponse)
DESCRIPTOR._options = None
