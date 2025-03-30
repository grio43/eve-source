#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\fleet\fleet_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/fleet/fleet.proto', package='eve.fleet', syntax='proto3', serialized_options='Z4github.com/ccpgames/eve-proto-go/generated/eve/fleet', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/fleet/fleet.proto\x12\teve.fleet\x1a\x1deve/character/character.proto"8\n\nAttributes\x12*\n\x07creator\x18\x01 \x01(\x0b2\x19.eve.character.Identifier" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"R\n\x07Created\x12!\n\x02id\x18\x01 \x01(\x0b2\x15.eve.fleet.Identifier\x12$\n\x05fleet\x18\x02 \x01(\x0b2\x15.eve.fleet.AttributesB6Z4github.com/ccpgames/eve-proto-go/generated/eve/fleetb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.fleet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='creator', full_name='eve.fleet.Attributes.creator', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=67, serialized_end=123)
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.fleet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.fleet.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=125, serialized_end=157)
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve.fleet.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.fleet.Created.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='fleet', full_name='eve.fleet.Created.fleet', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=159, serialized_end=241)
_ATTRIBUTES.fields_by_name['creator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CREATED.fields_by_name['id'].message_type = _IDENTIFIER
_CREATED.fields_by_name['fleet'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.fleet.fleet_pb2'})
_sym_db.RegisterMessage(Attributes)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.fleet.fleet_pb2'})
_sym_db.RegisterMessage(Identifier)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve.fleet.fleet_pb2'})
_sym_db.RegisterMessage(Created)
DESCRIPTOR._options = None
