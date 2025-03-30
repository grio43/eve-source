#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\hub\workforce\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.sovereignty.hub import hub_pb2 as eve_dot_sovereignty_dot_hub_dot_hub__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/hub/workforce/api/requests.proto', package='eve.sovereignty.hub.workforce.api', syntax='proto3', serialized_options='ZLgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/workforce/api', create_key=_descriptor._internal_create_key, serialized_pb='\n0eve/sovereignty/hub/workforce/api/requests.proto\x12!eve.sovereignty.hub.workforce.api\x1a\x1deve/character/character.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1deve/sovereignty/hub/hub.proto"\xa4\x01\n\x13IsAuthorizedRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12,\n\x03hub\x18\x02 \x01(\x0b2\x1f.eve.sovereignty.hub.Identifier\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier"\x16\n\x14IsAuthorizedResponseBNZLgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/workforce/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR, eve_dot_sovereignty_dot_hub_dot_hub__pb2.DESCRIPTOR])
_ISAUTHORIZEDREQUEST = _descriptor.Descriptor(name='IsAuthorizedRequest', full_name='eve.sovereignty.hub.workforce.api.IsAuthorizedRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.sovereignty.hub.workforce.api.IsAuthorizedRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='hub', full_name='eve.sovereignty.hub.workforce.api.IsAuthorizedRequest.hub', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.sovereignty.hub.workforce.api.IsAuthorizedRequest.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=185, serialized_end=349)
_ISAUTHORIZEDRESPONSE = _descriptor.Descriptor(name='IsAuthorizedResponse', full_name='eve.sovereignty.hub.workforce.api.IsAuthorizedResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=351, serialized_end=373)
_ISAUTHORIZEDREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ISAUTHORIZEDREQUEST.fields_by_name['hub'].message_type = eve_dot_sovereignty_dot_hub_dot_hub__pb2._IDENTIFIER
_ISAUTHORIZEDREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['IsAuthorizedRequest'] = _ISAUTHORIZEDREQUEST
DESCRIPTOR.message_types_by_name['IsAuthorizedResponse'] = _ISAUTHORIZEDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
IsAuthorizedRequest = _reflection.GeneratedProtocolMessageType('IsAuthorizedRequest', (_message.Message,), {'DESCRIPTOR': _ISAUTHORIZEDREQUEST,
 '__module__': 'eve.sovereignty.hub.workforce.api.requests_pb2'})
_sym_db.RegisterMessage(IsAuthorizedRequest)
IsAuthorizedResponse = _reflection.GeneratedProtocolMessageType('IsAuthorizedResponse', (_message.Message,), {'DESCRIPTOR': _ISAUTHORIZEDRESPONSE,
 '__module__': 'eve.sovereignty.hub.workforce.api.requests_pb2'})
_sym_db.RegisterMessage(IsAuthorizedResponse)
DESCRIPTOR._options = None
