#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\store\store_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.plex import plex_pb2 as eve__public_dot_plex_dot_plex__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/store/store.proto', package='eve_public.store', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve_public/store', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve_public/store/store.proto\x12\x10eve_public.store\x1a\x1aeve_public/plex/plex.proto"\xb2\x02\n\x05Price\x12\x14\n\x08currency\x18\x01 \x01(\tB\x02\x18\x01\x12\x1b\n\x0famount_in_cents\x18\x02 \x01(\x03B\x02\x18\x01\x12\x1b\n\x11no_currency_price\x18\x03 \x01(\x08H\x00\x12:\n\x0ecurrency_price\x18\x04 \x01(\x0b2 .eve_public.store.Price.CurrencyH\x00\x12\x17\n\rno_plex_price\x18\x05 \x01(\x08H\x01\x12/\n\nplex_price\x18\x06 \x01(\x0b2\x19.eve_public.plex.CurrencyH\x01\x1a1\n\x08Currency\x12\x0c\n\x04code\x18\x01 \x01(\t\x12\x17\n\x0famount_in_cents\x18\x02 \x01(\x03B\x11\n\x0fcurrency_optionB\r\n\x0bplex_option*\xc7\x01\n\x07Catalog\x12\x17\n\x13CATALOG_UNSPECIFIED\x10\x00\x12\x0f\n\x0bCATALOG_NES\x10\x01\x12\x16\n\x12CATALOG_REAL_MONEY\x10\x02\x12\x17\n\x13CATALOG_ENTITLEMENT\x10\x03\x12\x1f\n\x1bCATALOG_VANGUARD_REAL_MONEY\x10\x04\x12 \n\x1cCATALOG_VANGUARD_ENTITLEMENT\x10\x05\x12\x1e\n\x1aCATALOG_EVE_MIXED_CURRENCY\x10\x06B=Z;github.com/ccpgames/eve-proto-go/generated/eve_public/storeb\x06proto3', dependencies=[eve__public_dot_plex_dot_plex__pb2.DESCRIPTOR])
_CATALOG = _descriptor.EnumDescriptor(name='Catalog', full_name='eve_public.store.Catalog', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='CATALOG_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_NES', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_REAL_MONEY', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_ENTITLEMENT', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_VANGUARD_REAL_MONEY', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_VANGUARD_ENTITLEMENT', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CATALOG_EVE_MIXED_CURRENCY', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=388, serialized_end=587)
_sym_db.RegisterEnumDescriptor(_CATALOG)
Catalog = enum_type_wrapper.EnumTypeWrapper(_CATALOG)
CATALOG_UNSPECIFIED = 0
CATALOG_NES = 1
CATALOG_REAL_MONEY = 2
CATALOG_ENTITLEMENT = 3
CATALOG_VANGUARD_REAL_MONEY = 4
CATALOG_VANGUARD_ENTITLEMENT = 5
CATALOG_EVE_MIXED_CURRENCY = 6
_PRICE_CURRENCY = _descriptor.Descriptor(name='Currency', full_name='eve_public.store.Price.Currency', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='code', full_name='eve_public.store.Price.Currency.code', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='amount_in_cents', full_name='eve_public.store.Price.Currency.amount_in_cents', index=1, number=2, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=302, serialized_end=351)
_PRICE = _descriptor.Descriptor(name='Price', full_name='eve_public.store.Price', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='currency', full_name='eve_public.store.Price.currency', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount_in_cents', full_name='eve_public.store.Price.amount_in_cents', index=1, number=2, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_currency_price', full_name='eve_public.store.Price.no_currency_price', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='currency_price', full_name='eve_public.store.Price.currency_price', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_plex_price', full_name='eve_public.store.Price.no_plex_price', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='plex_price', full_name='eve_public.store.Price.plex_price', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_PRICE_CURRENCY], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='currency_option', full_name='eve_public.store.Price.currency_option', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='plex_option', full_name='eve_public.store.Price.plex_option', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=79, serialized_end=385)
_PRICE_CURRENCY.containing_type = _PRICE
_PRICE.fields_by_name['currency_price'].message_type = _PRICE_CURRENCY
_PRICE.fields_by_name['plex_price'].message_type = eve__public_dot_plex_dot_plex__pb2._CURRENCY
_PRICE.oneofs_by_name['currency_option'].fields.append(_PRICE.fields_by_name['no_currency_price'])
_PRICE.fields_by_name['no_currency_price'].containing_oneof = _PRICE.oneofs_by_name['currency_option']
_PRICE.oneofs_by_name['currency_option'].fields.append(_PRICE.fields_by_name['currency_price'])
_PRICE.fields_by_name['currency_price'].containing_oneof = _PRICE.oneofs_by_name['currency_option']
_PRICE.oneofs_by_name['plex_option'].fields.append(_PRICE.fields_by_name['no_plex_price'])
_PRICE.fields_by_name['no_plex_price'].containing_oneof = _PRICE.oneofs_by_name['plex_option']
_PRICE.oneofs_by_name['plex_option'].fields.append(_PRICE.fields_by_name['plex_price'])
_PRICE.fields_by_name['plex_price'].containing_oneof = _PRICE.oneofs_by_name['plex_option']
DESCRIPTOR.message_types_by_name['Price'] = _PRICE
DESCRIPTOR.enum_types_by_name['Catalog'] = _CATALOG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Price = _reflection.GeneratedProtocolMessageType('Price', (_message.Message,), {'Currency': _reflection.GeneratedProtocolMessageType('Currency', (_message.Message,), {'DESCRIPTOR': _PRICE_CURRENCY,
              '__module__': 'eve_public.store.store_pb2'}),
 'DESCRIPTOR': _PRICE,
 '__module__': 'eve_public.store.store_pb2'})
_sym_db.RegisterMessage(Price)
_sym_db.RegisterMessage(Price.Currency)
DESCRIPTOR._options = None
_PRICE.fields_by_name['currency']._options = None
_PRICE.fields_by_name['amount_in_cents']._options = None
