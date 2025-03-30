#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\ledger_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/ledger.proto', package='eve.industry.ledger', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/industry/ledger', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/industry/ledger.proto\x12\x13eve.industry.ledger\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a eve/inventory/generic_item.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\x84\x02\n\nAttributes\x123\n\x04item\x18\x01 \x01(\x0b2%.eve.inventory.genericitem.Attributes\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x120\n\x0bcorporation\x18\x03 \x01(\x0b2\x1b.eve.corporation.Identifier\x121\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12.\n\ntime_mined\x18\x05 \x01(\x0b2\x1a.google.protobuf.TimestampB@Z>github.com/ccpgames/eve-proto-go/generated/eve/industry/ledgerb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.industry.ledger.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.industry.ledger.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=218, serialized_end=250)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.industry.ledger.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.industry.ledger.Attributes.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.industry.ledger.Attributes.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.industry.ledger.Attributes.corporation', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.industry.ledger.Attributes.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='time_mined', full_name='eve.industry.ledger.Attributes.time_mined', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=253, serialized_end=513)
_ATTRIBUTES.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
_ATTRIBUTES.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['time_mined'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.industry.ledger_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.industry.ledger_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
