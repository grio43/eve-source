#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\fleet\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.fleet import fleet_pb2 as eve_dot_fleet_dot_fleet__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/fleet/api/events.proto', package='eve.fleet.api', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/fleet/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/fleet/api/events.proto\x12\reve.fleet.api\x1a\x1deve/character/character.proto\x1a\x15eve/fleet/fleet.proto\x1a!eve/solarsystem/solarsystem.proto"\x9f\x01\n\rAdvertCreated\x12\'\n\x08fleet_id\x18\x01 \x01(\x0b2\x15.eve.fleet.Identifier\x12/\n\x0ccharacter_id\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x124\n\x0fsolar_system_id\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB:Z8github.com/ccpgames/eve-proto-go/generated/eve/fleet/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_fleet_dot_fleet__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_ADVERTCREATED = _descriptor.Descriptor(name='AdvertCreated', full_name='eve.fleet.api.AdvertCreated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='fleet_id', full_name='eve.fleet.api.AdvertCreated.fleet_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character_id', full_name='eve.fleet.api.AdvertCreated.character_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system_id', full_name='eve.fleet.api.AdvertCreated.solar_system_id', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=135, serialized_end=294)
_ADVERTCREATED.fields_by_name['fleet_id'].message_type = eve_dot_fleet_dot_fleet__pb2._IDENTIFIER
_ADVERTCREATED.fields_by_name['character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ADVERTCREATED.fields_by_name['solar_system_id'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['AdvertCreated'] = _ADVERTCREATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
AdvertCreated = _reflection.GeneratedProtocolMessageType('AdvertCreated', (_message.Message,), {'DESCRIPTOR': _ADVERTCREATED,
 '__module__': 'eve.fleet.api.events_pb2'})
_sym_db.RegisterMessage(AdvertCreated)
DESCRIPTOR._options = None
