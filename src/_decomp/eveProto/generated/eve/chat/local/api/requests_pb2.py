#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\chat\local\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.chat.local import local_pb2 as eve_dot_chat_dot_local_dot_local__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/chat/local/api/requests.proto', package='eve.chat.local.api', syntax='proto3', serialized_options='Z=github.com/ccpgames/eve-proto-go/generated/eve/chat/local/api', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/chat/local/api/requests.proto\x12\x12eve.chat.local.api\x1a\x1deve/character/character.proto\x1a\x1aeve/chat/local/local.proto\x1a!eve/solarsystem/solarsystem.proto"C\n\x0eGetModeRequest\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier"5\n\x0fGetModeResponse\x12"\n\x04mode\x18\x01 \x01(\x0e2\x14.eve.chat.local.Mode"H\n\x18GetClassificationRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"S\n\x19GetClassificationResponse\x126\n\x0eclassification\x18\x01 \x01(\x0e2\x1e.eve.chat.local.ClassificationB?Z=github.com/ccpgames/eve-proto-go/generated/eve/chat/local/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_chat_dot_local_dot_local__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_GETMODEREQUEST = _descriptor.Descriptor(name='GetModeRequest', full_name='eve.chat.local.api.GetModeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.chat.local.api.GetModeRequest.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=151, serialized_end=218)
_GETMODERESPONSE = _descriptor.Descriptor(name='GetModeResponse', full_name='eve.chat.local.api.GetModeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='mode', full_name='eve.chat.local.api.GetModeResponse.mode', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=220, serialized_end=273)
_GETCLASSIFICATIONREQUEST = _descriptor.Descriptor(name='GetClassificationRequest', full_name='eve.chat.local.api.GetClassificationRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.chat.local.api.GetClassificationRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=275, serialized_end=347)
_GETCLASSIFICATIONRESPONSE = _descriptor.Descriptor(name='GetClassificationResponse', full_name='eve.chat.local.api.GetClassificationResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='classification', full_name='eve.chat.local.api.GetClassificationResponse.classification', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=349, serialized_end=432)
_GETMODEREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETMODERESPONSE.fields_by_name['mode'].enum_type = eve_dot_chat_dot_local_dot_local__pb2._MODE
_GETCLASSIFICATIONREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETCLASSIFICATIONRESPONSE.fields_by_name['classification'].enum_type = eve_dot_chat_dot_local_dot_local__pb2._CLASSIFICATION
DESCRIPTOR.message_types_by_name['GetModeRequest'] = _GETMODEREQUEST
DESCRIPTOR.message_types_by_name['GetModeResponse'] = _GETMODERESPONSE
DESCRIPTOR.message_types_by_name['GetClassificationRequest'] = _GETCLASSIFICATIONREQUEST
DESCRIPTOR.message_types_by_name['GetClassificationResponse'] = _GETCLASSIFICATIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetModeRequest = _reflection.GeneratedProtocolMessageType('GetModeRequest', (_message.Message,), {'DESCRIPTOR': _GETMODEREQUEST,
 '__module__': 'eve.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetModeRequest)
GetModeResponse = _reflection.GeneratedProtocolMessageType('GetModeResponse', (_message.Message,), {'DESCRIPTOR': _GETMODERESPONSE,
 '__module__': 'eve.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetModeResponse)
GetClassificationRequest = _reflection.GeneratedProtocolMessageType('GetClassificationRequest', (_message.Message,), {'DESCRIPTOR': _GETCLASSIFICATIONREQUEST,
 '__module__': 'eve.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetClassificationRequest)
GetClassificationResponse = _reflection.GeneratedProtocolMessageType('GetClassificationResponse', (_message.Message,), {'DESCRIPTOR': _GETCLASSIFICATIONRESPONSE,
 '__module__': 'eve.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetClassificationResponse)
DESCRIPTOR._options = None
