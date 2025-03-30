#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\market\component\listing\listing_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/market/component/listing/listing.proto', package='eve.cosmetic.market.component.listing', syntax='proto3', serialized_options='ZPgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/component/listing', create_key=_descriptor._internal_create_key, serialized_pb='\n3eve/cosmetic/market/component/listing/listing.proto\x12%eve.cosmetic.market.component.listing\x1a%eve/inventory/generic_item_type.proto\x1a\x11eve/isk/isk.proto\x1a\x13eve/plex/plex.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\x99\x02\n\nAttributes\x12.\n\nsale_start\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12,\n\x08sale_end\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12 \n\x03isk\x18\x04 \x01(\x0b2\x11.eve.isk.CurrencyH\x00\x12"\n\x04plex\x18\x05 \x01(\x0b2\x12.eve.plex.CurrencyH\x00\x12I\n\x16component_license_item\x18\x06 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12\x13\n\x0bbundle_size\x18\x07 \x01(\x04B\x07\n\x05price"\x8d\x01\n\x05Entry\x12=\n\x02id\x18\x01 \x01(\x0b21.eve.cosmetic.market.component.listing.Identifier\x12E\n\nattributes\x18\x02 \x01(\x0b21.eve.cosmetic.market.component.listing.AttributesBRZPgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/component/listingb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_plex_dot_plex__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.market.component.listing.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.cosmetic.market.component.listing.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=206, serialized_end=232)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.market.component.listing.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sale_start', full_name='eve.cosmetic.market.component.listing.Attributes.sale_start', index=0, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sale_end', full_name='eve.cosmetic.market.component.listing.Attributes.sale_end', index=1, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='isk', full_name='eve.cosmetic.market.component.listing.Attributes.isk', index=2, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='plex', full_name='eve.cosmetic.market.component.listing.Attributes.plex', index=3, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='component_license_item', full_name='eve.cosmetic.market.component.listing.Attributes.component_license_item', index=4, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='bundle_size', full_name='eve.cosmetic.market.component.listing.Attributes.bundle_size', index=5, number=7, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='price', full_name='eve.cosmetic.market.component.listing.Attributes.price', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=235, serialized_end=516)
_ENTRY = _descriptor.Descriptor(name='Entry', full_name='eve.cosmetic.market.component.listing.Entry', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.cosmetic.market.component.listing.Entry.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.market.component.listing.Entry.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=519, serialized_end=660)
_ATTRIBUTES.fields_by_name['sale_start'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['sale_end'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['isk'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_ATTRIBUTES.fields_by_name['plex'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_ATTRIBUTES.fields_by_name['component_license_item'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ATTRIBUTES.oneofs_by_name['price'].fields.append(_ATTRIBUTES.fields_by_name['isk'])
_ATTRIBUTES.fields_by_name['isk'].containing_oneof = _ATTRIBUTES.oneofs_by_name['price']
_ATTRIBUTES.oneofs_by_name['price'].fields.append(_ATTRIBUTES.fields_by_name['plex'])
_ATTRIBUTES.fields_by_name['plex'].containing_oneof = _ATTRIBUTES.oneofs_by_name['price']
_ENTRY.fields_by_name['id'].message_type = _IDENTIFIER
_ENTRY.fields_by_name['attributes'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Entry'] = _ENTRY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.market.component.listing.listing_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.market.component.listing.listing_pb2'})
_sym_db.RegisterMessage(Attributes)
Entry = _reflection.GeneratedProtocolMessageType('Entry', (_message.Message,), {'DESCRIPTOR': _ENTRY,
 '__module__': 'eve.cosmetic.market.component.listing.listing_pb2'})
_sym_db.RegisterMessage(Entry)
DESCRIPTOR._options = None
