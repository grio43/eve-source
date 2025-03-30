#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\module\charge_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/module/charge.proto', package='eve.ship.module.charge', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/ship/module/charge', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/ship/module/charge.proto\x12\x16eve.ship.module.charge\x1a%eve/inventory/generic_item_type.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"O\n\nAttributes\x12A\n\x0einventory_type\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.IdentifierBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/ship/module/chargeb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.ship.module.charge.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.ship.module.charge.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=95, serialized_end=127)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.ship.module.charge.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='inventory_type', full_name='eve.ship.module.charge.Attributes.inventory_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=129, serialized_end=208)
_ATTRIBUTES.fields_by_name['inventory_type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.ship.module.charge_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.ship.module.charge_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
