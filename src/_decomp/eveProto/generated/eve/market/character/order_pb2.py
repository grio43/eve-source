#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\market\character\order_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/market/character/order.proto', package='eve.market.character.order', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/market/character/order', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/market/character/order.proto\x12\x1aeve.market.character.order\x1a\x1deve/character/character.proto"9\n\tCancelled\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"8\n\x08Modified\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"6\n\x06Placed\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"@\n\x10MultiOrderPlaced\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/market/character/orderb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_CANCELLED = _descriptor.Descriptor(name='Cancelled', full_name='eve.market.character.order.Cancelled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.market.character.order.Cancelled.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=95, serialized_end=152)
_MODIFIED = _descriptor.Descriptor(name='Modified', full_name='eve.market.character.order.Modified', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.market.character.order.Modified.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=154, serialized_end=210)
_PLACED = _descriptor.Descriptor(name='Placed', full_name='eve.market.character.order.Placed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.market.character.order.Placed.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=212, serialized_end=266)
_MULTIORDERPLACED = _descriptor.Descriptor(name='MultiOrderPlaced', full_name='eve.market.character.order.MultiOrderPlaced', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.market.character.order.MultiOrderPlaced.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=268, serialized_end=332)
_CANCELLED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MODIFIED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PLACED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MULTIORDERPLACED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Cancelled'] = _CANCELLED
DESCRIPTOR.message_types_by_name['Modified'] = _MODIFIED
DESCRIPTOR.message_types_by_name['Placed'] = _PLACED
DESCRIPTOR.message_types_by_name['MultiOrderPlaced'] = _MULTIORDERPLACED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Cancelled = _reflection.GeneratedProtocolMessageType('Cancelled', (_message.Message,), {'DESCRIPTOR': _CANCELLED,
 '__module__': 'eve.market.character.order_pb2'})
_sym_db.RegisterMessage(Cancelled)
Modified = _reflection.GeneratedProtocolMessageType('Modified', (_message.Message,), {'DESCRIPTOR': _MODIFIED,
 '__module__': 'eve.market.character.order_pb2'})
_sym_db.RegisterMessage(Modified)
Placed = _reflection.GeneratedProtocolMessageType('Placed', (_message.Message,), {'DESCRIPTOR': _PLACED,
 '__module__': 'eve.market.character.order_pb2'})
_sym_db.RegisterMessage(Placed)
MultiOrderPlaced = _reflection.GeneratedProtocolMessageType('MultiOrderPlaced', (_message.Message,), {'DESCRIPTOR': _MULTIORDERPLACED,
 '__module__': 'eve.market.character.order_pb2'})
_sym_db.RegisterMessage(MultiOrderPlaced)
DESCRIPTOR._options = None
