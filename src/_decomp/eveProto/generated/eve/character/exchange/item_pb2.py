#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\exchange\item_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/exchange/item.proto', package='eve.character.exchange.item', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve/character/exchange/item', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/character/exchange/item.proto\x12\x1beve.character.exchange.item\x1a%eve/inventory/generic_item_type.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\\\n\nAttributes\x12<\n\titem_type\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\rBHZFgithub.com/ccpgames/eve-proto-go/generated/eve/character/exchange/itemb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.exchange.item.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.exchange.item.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=105, serialized_end=137)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.exchange.item.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item_type', full_name='eve.character.exchange.item.Attributes.item_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.character.exchange.item.Attributes.quantity', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=139, serialized_end=231)
_ATTRIBUTES.fields_by_name['item_type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.exchange.item_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.exchange.item_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
