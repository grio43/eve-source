#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\npc\ship\ship_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/npc/ship/ship.proto', package='eve.npc.ship', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/npc/ship', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/npc/ship/ship.proto\x12\x0ceve.npc.ship\x1a\x19eve/faction/faction.proto\x1a\x18eve/ship/ship_type.proto"9\n\nIdentifier\x12+\n\tship_type\x18\x01 \x01(\x0b2\x18.eve.shiptype.Identifier"6\n\nAttributes\x12(\n\x07faction\x18\x01 \x01(\x0b2\x17.eve.faction.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/npc/shipb\x06proto3', dependencies=[eve_dot_faction_dot_faction__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.npc.ship.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship_type', full_name='eve.npc.ship.Identifier.ship_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=94, serialized_end=151)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.npc.ship.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction', full_name='eve.npc.ship.Attributes.faction', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=153, serialized_end=207)
_IDENTIFIER.fields_by_name['ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.npc.ship.ship_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.npc.ship.ship_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
