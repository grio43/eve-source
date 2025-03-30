#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\solarsystem\characters_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/solarsystem/characters.proto', package='eve.solarsystem.characters', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/solarsystem/characters', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/solarsystem/characters.proto\x12\x1aeve.solarsystem.characters\x1a\x1deve/character/character.proto\x1a!eve/solarsystem/solarsystem.proto"E\n\x10GetOnlineRequest\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier"B\n\x11GetOnlineResponse\x12-\n\ncharacters\x18\x01 \x03(\x0b2\x19.eve.character.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/solarsystem/charactersb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_GETONLINEREQUEST = _descriptor.Descriptor(name='GetOnlineRequest', full_name='eve.solarsystem.characters.GetOnlineRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.solarsystem.characters.GetOnlineRequest.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=130, serialized_end=199)
_GETONLINERESPONSE = _descriptor.Descriptor(name='GetOnlineResponse', full_name='eve.solarsystem.characters.GetOnlineResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='characters', full_name='eve.solarsystem.characters.GetOnlineResponse.characters', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=201, serialized_end=267)
_GETONLINEREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETONLINERESPONSE.fields_by_name['characters'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetOnlineRequest'] = _GETONLINEREQUEST
DESCRIPTOR.message_types_by_name['GetOnlineResponse'] = _GETONLINERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetOnlineRequest = _reflection.GeneratedProtocolMessageType('GetOnlineRequest', (_message.Message,), {'DESCRIPTOR': _GETONLINEREQUEST,
 '__module__': 'eve.solarsystem.characters_pb2'})
_sym_db.RegisterMessage(GetOnlineRequest)
GetOnlineResponse = _reflection.GeneratedProtocolMessageType('GetOnlineResponse', (_message.Message,), {'DESCRIPTOR': _GETONLINERESPONSE,
 '__module__': 'eve.solarsystem.characters_pb2'})
_sym_db.RegisterMessage(GetOnlineResponse)
DESCRIPTOR._options = None
