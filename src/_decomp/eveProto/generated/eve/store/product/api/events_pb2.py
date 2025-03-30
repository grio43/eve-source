#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\store\product\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
from eveProto.generated.eve.store.sale import sale_pb2 as eve_dot_store_dot_sale_dot_sale__pb2
from eveProto.generated.eve.user.license import license_pb2 as eve_dot_user_dot_license_dot_license__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/store/product/api/events.proto', package='eve.store.product.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/store/product/api', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/store/product/api/events.proto\x12\x15eve.store.product.api\x1a\x13eve/plex/plex.proto\x1a\x19eve/store/sale/sale.proto\x1a\x1eeve/user/license/license.proto\x1a\x13eve/user/user.proto\x1a\x1egoogle/protobuf/duration.proto"\xa6\x01\n\rPlexPurchased\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12(\n\x04sale\x18\x02 \x01(\x0b2\x1a.eve.store.sale.Identifier\x12"\n\x06amount\x18\x03 \x01(\x0b2\x12.eve.plex.Currency\x12#\n\x07balance\x18\x04 \x01(\x0b2\x12.eve.plex.Currency"\x98\x01\n\x10LicensePurchased\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.Identifier\x12+\n\x08duration\x18\x02 \x01(\x0b2\x19.google.protobuf.Duration\x12(\n\x04sale\x18\x03 \x01(\x0b2\x1a.eve.store.sale.IdentifierBBZ@github.com/ccpgames/eve-proto-go/generated/eve/store/product/apib\x06proto3', dependencies=[eve_dot_plex_dot_plex__pb2.DESCRIPTOR,
 eve_dot_store_dot_sale_dot_sale__pb2.DESCRIPTOR,
 eve_dot_user_dot_license_dot_license__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_PLEXPURCHASED = _descriptor.Descriptor(name='PlexPurchased', full_name='eve.store.product.api.PlexPurchased', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.store.product.api.PlexPurchased.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sale', full_name='eve.store.product.api.PlexPurchased.sale', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.store.product.api.PlexPurchased.amount', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='balance', full_name='eve.store.product.api.PlexPurchased.balance', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=195, serialized_end=361)
_LICENSEPURCHASED = _descriptor.Descriptor(name='LicensePurchased', full_name='eve.store.product.api.LicensePurchased', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.store.product.api.LicensePurchased.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='duration', full_name='eve.store.product.api.LicensePurchased.duration', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='sale', full_name='eve.store.product.api.LicensePurchased.sale', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=364, serialized_end=516)
_PLEXPURCHASED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_PLEXPURCHASED.fields_by_name['sale'].message_type = eve_dot_store_dot_sale_dot_sale__pb2._IDENTIFIER
_PLEXPURCHASED.fields_by_name['amount'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_PLEXPURCHASED.fields_by_name['balance'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_LICENSEPURCHASED.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
_LICENSEPURCHASED.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_LICENSEPURCHASED.fields_by_name['sale'].message_type = eve_dot_store_dot_sale_dot_sale__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['PlexPurchased'] = _PLEXPURCHASED
DESCRIPTOR.message_types_by_name['LicensePurchased'] = _LICENSEPURCHASED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
PlexPurchased = _reflection.GeneratedProtocolMessageType('PlexPurchased', (_message.Message,), {'DESCRIPTOR': _PLEXPURCHASED,
 '__module__': 'eve.store.product.api.events_pb2'})
_sym_db.RegisterMessage(PlexPurchased)
LicensePurchased = _reflection.GeneratedProtocolMessageType('LicensePurchased', (_message.Message,), {'DESCRIPTOR': _LICENSEPURCHASED,
 '__module__': 'eve.store.product.api.events_pb2'})
_sym_db.RegisterMessage(LicensePurchased)
DESCRIPTOR._options = None
