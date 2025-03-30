#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\exchange\exchange_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.exchange import item_pb2 as eve_dot_character_dot_exchange_dot_item__pb2
from eveProto.generated.eve.character.location import location_pb2 as eve_dot_character_dot_location_dot_location__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/exchange/exchange.proto', package='eve.character.exchange', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/exchange', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/character/exchange/exchange.proto\x12\x16eve.character.exchange\x1a\x1deve/character/character.proto\x1a!eve/character/exchange/item.proto\x1a%eve/character/location/location.proto\x1a\x11eve/isk/isk.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\xda\x04\n\nAttributes\x12-\n\ninstigator\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12.\n\x0bparticipant\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12C\n\x13deprecated_location\x18\x03 \x01(\x0b2".eve.character.location.IdentifierB\x02\x18\x01\x12$\n\tisk_given\x18\x04 \x01(\x0b2\x11.eve.isk.Currency\x12<\n\x0bitems_given\x18\x05 \x03(\x0b2\'.eve.character.exchange.Attributes.Item\x12\'\n\x0cisk_received\x18\x06 \x01(\x0b2\x11.eve.isk.Currency\x12?\n\x0eitems_received\x18\x07 \x03(\x0b2\'.eve.character.exchange.Attributes.Item\x12*\n\x07station\x18\x08 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\t \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x1ar\n\x04Item\x123\n\x02id\x18\x01 \x01(\x0b2\'.eve.character.exchange.item.Identifier\x125\n\x04item\x18\x02 \x01(\x0b2\'.eve.character.exchange.item.AttributesB\n\n\x08location"q\n\tCompleted\x12.\n\x02id\x18\x01 \x01(\x0b2".eve.character.exchange.Identifier\x124\n\x08exchange\x18\x02 \x01(\x0b2".eve.character.exchange.AttributesBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/exchangeb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_character_dot_exchange_dot_item__pb2.DESCRIPTOR,
 eve_dot_character_dot_location_dot_location__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.exchange.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.exchange.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=247, serialized_end=279)
_ATTRIBUTES_ITEM = _descriptor.Descriptor(name='Item', full_name='eve.character.exchange.Attributes.Item', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.character.exchange.Attributes.Item.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='item', full_name='eve.character.exchange.Attributes.Item.item', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=758, serialized_end=872)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.exchange.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='instigator', full_name='eve.character.exchange.Attributes.instigator', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='participant', full_name='eve.character.exchange.Attributes.participant', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='deprecated_location', full_name='eve.character.exchange.Attributes.deprecated_location', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='isk_given', full_name='eve.character.exchange.Attributes.isk_given', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='items_given', full_name='eve.character.exchange.Attributes.items_given', index=4, number=5, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='isk_received', full_name='eve.character.exchange.Attributes.isk_received', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='items_received', full_name='eve.character.exchange.Attributes.items_received', index=6, number=7, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.character.exchange.Attributes.station', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.character.exchange.Attributes.structure', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ATTRIBUTES_ITEM], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='location', full_name='eve.character.exchange.Attributes.location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=282, serialized_end=884)
_COMPLETED = _descriptor.Descriptor(name='Completed', full_name='eve.character.exchange.Completed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.character.exchange.Completed.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='exchange', full_name='eve.character.exchange.Completed.exchange', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=886, serialized_end=999)
_ATTRIBUTES_ITEM.fields_by_name['id'].message_type = eve_dot_character_dot_exchange_dot_item__pb2._IDENTIFIER
_ATTRIBUTES_ITEM.fields_by_name['item'].message_type = eve_dot_character_dot_exchange_dot_item__pb2._ATTRIBUTES
_ATTRIBUTES_ITEM.containing_type = _ATTRIBUTES
_ATTRIBUTES.fields_by_name['instigator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['participant'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['deprecated_location'].message_type = eve_dot_character_dot_location_dot_location__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['isk_given'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_ATTRIBUTES.fields_by_name['items_given'].message_type = _ATTRIBUTES_ITEM
_ATTRIBUTES.fields_by_name['isk_received'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_ATTRIBUTES.fields_by_name['items_received'].message_type = _ATTRIBUTES_ITEM
_ATTRIBUTES.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_ATTRIBUTES.oneofs_by_name['location'].fields.append(_ATTRIBUTES.fields_by_name['station'])
_ATTRIBUTES.fields_by_name['station'].containing_oneof = _ATTRIBUTES.oneofs_by_name['location']
_ATTRIBUTES.oneofs_by_name['location'].fields.append(_ATTRIBUTES.fields_by_name['structure'])
_ATTRIBUTES.fields_by_name['structure'].containing_oneof = _ATTRIBUTES.oneofs_by_name['location']
_COMPLETED.fields_by_name['id'].message_type = _IDENTIFIER
_COMPLETED.fields_by_name['exchange'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Completed'] = _COMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.exchange.exchange_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'Item': _reflection.GeneratedProtocolMessageType('Item', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES_ITEM,
          '__module__': 'eve.character.exchange.exchange_pb2'}),
 'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.exchange.exchange_pb2'})
_sym_db.RegisterMessage(Attributes)
_sym_db.RegisterMessage(Attributes.Item)
Completed = _reflection.GeneratedProtocolMessageType('Completed', (_message.Message,), {'DESCRIPTOR': _COMPLETED,
 '__module__': 'eve.character.exchange.exchange_pb2'})
_sym_db.RegisterMessage(Completed)
DESCRIPTOR._options = None
_ATTRIBUTES.fields_by_name['deprecated_location']._options = None
