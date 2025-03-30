#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\market\character\sellorder_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/market/character/sellorder.proto', package='eve.market.character.sellorder', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/market/character', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/market/character/sellorder.proto\x12\x1eeve.market.character.sellorder\x1a\x1deve/character/character.proto\x1a eve/inventory/generic_item.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"o\n\nAttributes\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x123\n\x04item\x18\x02 \x01(\x0b2%.eve.inventory.genericitem.Attributes"e\n\x12PartiallyFulfilled\x129\n\x05order\x18\x01 \x01(\x0b2*.eve.market.character.sellorder.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\x05:\x02\x18\x01"J\n\tFulfilled\x129\n\x05order\x18\x01 \x01(\x0b2*.eve.market.character.sellorder.Identifier:\x02\x18\x01"G\n\nGetRequest\x129\n\x05order\x18\x01 \x01(\x0b2*.eve.market.character.sellorder.Identifier"H\n\x0bGetResponse\x129\n\x05order\x18\x01 \x01(\x0b2*.eve.market.character.sellorder.AttributesBAZ?github.com/ccpgames/eve-proto-go/generated/eve/market/characterb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.market.character.sellorder.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.market.character.sellorder.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=137, serialized_end=169)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.market.character.sellorder.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.market.character.sellorder.Attributes.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='item', full_name='eve.market.character.sellorder.Attributes.item', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=171, serialized_end=282)
_PARTIALLYFULFILLED = _descriptor.Descriptor(name='PartiallyFulfilled', full_name='eve.market.character.sellorder.PartiallyFulfilled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='order', full_name='eve.market.character.sellorder.PartiallyFulfilled.order', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.market.character.sellorder.PartiallyFulfilled.quantity', index=1, number=2, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=284, serialized_end=385)
_FULFILLED = _descriptor.Descriptor(name='Fulfilled', full_name='eve.market.character.sellorder.Fulfilled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='order', full_name='eve.market.character.sellorder.Fulfilled.order', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=387, serialized_end=461)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.market.character.sellorder.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='order', full_name='eve.market.character.sellorder.GetRequest.order', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=463, serialized_end=534)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.market.character.sellorder.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='order', full_name='eve.market.character.sellorder.GetResponse.order', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=536, serialized_end=608)
_ATTRIBUTES.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
_PARTIALLYFULFILLED.fields_by_name['order'].message_type = _IDENTIFIER
_FULFILLED.fields_by_name['order'].message_type = _IDENTIFIER
_GETREQUEST.fields_by_name['order'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['order'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['PartiallyFulfilled'] = _PARTIALLYFULFILLED
DESCRIPTOR.message_types_by_name['Fulfilled'] = _FULFILLED
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(Attributes)
PartiallyFulfilled = _reflection.GeneratedProtocolMessageType('PartiallyFulfilled', (_message.Message,), {'DESCRIPTOR': _PARTIALLYFULFILLED,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(PartiallyFulfilled)
Fulfilled = _reflection.GeneratedProtocolMessageType('Fulfilled', (_message.Message,), {'DESCRIPTOR': _FULFILLED,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(Fulfilled)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.market.character.sellorder_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
_PARTIALLYFULFILLED._options = None
_FULFILLED._options = None
