#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\bookmark\bookmark_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/bookmark/bookmark.proto', package='eve.bookmark', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/bookmark', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/bookmark/bookmark.proto\x12\x0ceve.bookmark\x1a\x1deve/character/character.proto\x1a eve/inventory/generic_item.proto\x1a%eve/inventory/generic_item_type.proto\x1a\x15eve/math/vector.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\x82\x02\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12$\n\x06target\x18\x03 \x01(\x0b2\x14.eve.bookmark.Target\x12\x13\n\tno_expiry\x18\x04 \x01(\x08H\x00\x120\n\nexpires_at\x18\x05 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12.\n\ncreated_at\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12*\n\x07creator\x18\x07 \x01(\x0b2\x19.eve.character.IdentifierB\x08\n\x06expiry"\x88\x03\n\x06Target\x12)\n\x04item\x18\x01 \x01(\x0b2\x19.eve.bookmark.Target.ItemH\x00\x127\n\x0bcoordinates\x18\x02 \x01(\x0b2 .eve.bookmark.Target.CoordinatesH\x00\x1a\xab\x01\n\x04Item\x121\n\x02id\x18\x01 \x01(\x0b2%.eve.inventory.genericitem.Identifier\x127\n\x04type\x18\x02 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x127\n\x08location\x18\x03 \x01(\x0b2%.eve.inventory.genericitem.Identifier\x1ab\n\x0bCoordinates\x120\n\x0bsolarsystem\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12!\n\x06vector\x18\x02 \x01(\x0b2\x11.eve.math.Vector3B\x08\n\x06targetB9Z7github.com/ccpgames/eve-proto-go/generated/eve/bookmarkb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR,
 eve_dot_math_dot_vector__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.bookmark.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.bookmark.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=240, serialized_end=272)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.bookmark.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.bookmark.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.bookmark.Attributes.description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='target', full_name='eve.bookmark.Attributes.target', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_expiry', full_name='eve.bookmark.Attributes.no_expiry', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expires_at', full_name='eve.bookmark.Attributes.expires_at', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='created_at', full_name='eve.bookmark.Attributes.created_at', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='creator', full_name='eve.bookmark.Attributes.creator', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='expiry', full_name='eve.bookmark.Attributes.expiry', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=275, serialized_end=533)
_TARGET_ITEM = _descriptor.Descriptor(name='Item', full_name='eve.bookmark.Target.Item', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.bookmark.Target.Item.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='type', full_name='eve.bookmark.Target.Item.type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='location', full_name='eve.bookmark.Target.Item.location', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=647, serialized_end=818)
_TARGET_COORDINATES = _descriptor.Descriptor(name='Coordinates', full_name='eve.bookmark.Target.Coordinates', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystem', full_name='eve.bookmark.Target.Coordinates.solarsystem', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='vector', full_name='eve.bookmark.Target.Coordinates.vector', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=820, serialized_end=918)
_TARGET = _descriptor.Descriptor(name='Target', full_name='eve.bookmark.Target', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.bookmark.Target.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='coordinates', full_name='eve.bookmark.Target.coordinates', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_TARGET_ITEM, _TARGET_COORDINATES], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='target', full_name='eve.bookmark.Target.target', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=536, serialized_end=928)
_ATTRIBUTES.fields_by_name['target'].message_type = _TARGET
_ATTRIBUTES.fields_by_name['expires_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['created_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['creator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.oneofs_by_name['expiry'].fields.append(_ATTRIBUTES.fields_by_name['no_expiry'])
_ATTRIBUTES.fields_by_name['no_expiry'].containing_oneof = _ATTRIBUTES.oneofs_by_name['expiry']
_ATTRIBUTES.oneofs_by_name['expiry'].fields.append(_ATTRIBUTES.fields_by_name['expires_at'])
_ATTRIBUTES.fields_by_name['expires_at'].containing_oneof = _ATTRIBUTES.oneofs_by_name['expiry']
_TARGET_ITEM.fields_by_name['id'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_TARGET_ITEM.fields_by_name['type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_TARGET_ITEM.fields_by_name['location'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_TARGET_ITEM.containing_type = _TARGET
_TARGET_COORDINATES.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_TARGET_COORDINATES.fields_by_name['vector'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_TARGET_COORDINATES.containing_type = _TARGET
_TARGET.fields_by_name['item'].message_type = _TARGET_ITEM
_TARGET.fields_by_name['coordinates'].message_type = _TARGET_COORDINATES
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['item'])
_TARGET.fields_by_name['item'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['coordinates'])
_TARGET.fields_by_name['coordinates'].containing_oneof = _TARGET.oneofs_by_name['target']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Target'] = _TARGET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.bookmark.bookmark_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.bookmark.bookmark_pb2'})
_sym_db.RegisterMessage(Attributes)
Target = _reflection.GeneratedProtocolMessageType('Target', (_message.Message,), {'Item': _reflection.GeneratedProtocolMessageType('Item', (_message.Message,), {'DESCRIPTOR': _TARGET_ITEM,
          '__module__': 'eve.bookmark.bookmark_pb2'}),
 'Coordinates': _reflection.GeneratedProtocolMessageType('Coordinates', (_message.Message,), {'DESCRIPTOR': _TARGET_COORDINATES,
                 '__module__': 'eve.bookmark.bookmark_pb2'}),
 'DESCRIPTOR': _TARGET,
 '__module__': 'eve.bookmark.bookmark_pb2'})
_sym_db.RegisterMessage(Target)
_sym_db.RegisterMessage(Target.Item)
_sym_db.RegisterMessage(Target.Coordinates)
DESCRIPTOR._options = None
