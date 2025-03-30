#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\npc\barter_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/npc/barter.proto', package='eve.npc.barter', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/npc/barter', create_key=_descriptor._internal_create_key, serialized_pb='\n\x14eve/npc/barter.proto\x12\x0eeve.npc.barter\x1a\x1deve/character/character.proto\x1a eve/inventory/generic_item.proto"\xbf\x01\n\x0cItemBartered\x12+\n\x08customer\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12\x13\n\x0btrader_type\x18\x02 \x01(\r\x124\n\x05given\x18\x03 \x01(\x0b2%.eve.inventory.genericitem.Attributes\x127\n\x08received\x18\x04 \x01(\x0b2%.eve.inventory.genericitem.AttributesB;Z9github.com/ccpgames/eve-proto-go/generated/eve/npc/barterb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR])
_ITEMBARTERED = _descriptor.Descriptor(name='ItemBartered', full_name='eve.npc.barter.ItemBartered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='customer', full_name='eve.npc.barter.ItemBartered.customer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='trader_type', full_name='eve.npc.barter.ItemBartered.trader_type', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='given', full_name='eve.npc.barter.ItemBartered.given', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='received', full_name='eve.npc.barter.ItemBartered.received', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=106, serialized_end=297)
_ITEMBARTERED.fields_by_name['customer'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ITEMBARTERED.fields_by_name['given'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
_ITEMBARTERED.fields_by_name['received'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['ItemBartered'] = _ITEMBARTERED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ItemBartered = _reflection.GeneratedProtocolMessageType('ItemBartered', (_message.Message,), {'DESCRIPTOR': _ITEMBARTERED,
 '__module__': 'eve.npc.barter_pb2'})
_sym_db.RegisterMessage(ItemBartered)
DESCRIPTOR._options = None
