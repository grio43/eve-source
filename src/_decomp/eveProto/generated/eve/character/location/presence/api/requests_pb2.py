#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\location\presence\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.location import presence_pb2 as eve_dot_character_dot_location_dot_presence__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/location/presence/api/requests.proto', package='eve.character.location.presence.api', syntax='proto3', serialized_options='ZNgithub.com/ccpgames/eve-proto-go/generated/eve/character/location/presence/api', create_key=_descriptor._internal_create_key, serialized_pb='\n2eve/character/location/presence/api/requests.proto\x12#eve.character.location.presence.api\x1a\x1deve/character/character.proto\x1a%eve/character/location/presence.proto"?\n\x0fGetStateRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"I\n\x10GetStateResponse\x125\n\x05state\x18\x01 \x01(\x0b2&.eve.character.location.presence.StateBPZNgithub.com/ccpgames/eve-proto-go/generated/eve/character/location/presence/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_character_dot_location_dot_presence__pb2.DESCRIPTOR])
_GETSTATEREQUEST = _descriptor.Descriptor(name='GetStateRequest', full_name='eve.character.location.presence.api.GetStateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.location.presence.api.GetStateRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=161, serialized_end=224)
_GETSTATERESPONSE = _descriptor.Descriptor(name='GetStateResponse', full_name='eve.character.location.presence.api.GetStateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='state', full_name='eve.character.location.presence.api.GetStateResponse.state', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=226, serialized_end=299)
_GETSTATEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETSTATERESPONSE.fields_by_name['state'].message_type = eve_dot_character_dot_location_dot_presence__pb2._STATE
DESCRIPTOR.message_types_by_name['GetStateRequest'] = _GETSTATEREQUEST
DESCRIPTOR.message_types_by_name['GetStateResponse'] = _GETSTATERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetStateRequest = _reflection.GeneratedProtocolMessageType('GetStateRequest', (_message.Message,), {'DESCRIPTOR': _GETSTATEREQUEST,
 '__module__': 'eve.character.location.presence.api.requests_pb2'})
_sym_db.RegisterMessage(GetStateRequest)
GetStateResponse = _reflection.GeneratedProtocolMessageType('GetStateResponse', (_message.Message,), {'DESCRIPTOR': _GETSTATERESPONSE,
 '__module__': 'eve.character.location.presence.api.requests_pb2'})
_sym_db.RegisterMessage(GetStateResponse)
DESCRIPTOR._options = None
