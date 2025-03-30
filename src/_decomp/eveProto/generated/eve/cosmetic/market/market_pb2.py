#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\market\market_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.loyaltypoints import loyaltypoints_pb2 as eve_dot_loyaltypoints_dot_loyaltypoints__pb2
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/market/market.proto', package='eve.cosmetic.market', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/cosmetic/market/market.proto\x12\x13eve.cosmetic.market\x1a\x11eve/isk/isk.proto\x1a%eve/loyaltypoints/loyaltypoints.proto\x1a\x13eve/plex/plex.proto"Q\n\tBrokerFee\x12\x10\n\x06no_fee\x18\x02 \x01(\x08H\x00\x12 \n\x03isk\x18\x03 \x01(\x0b2\x11.eve.isk.CurrencyH\x00B\n\n\x08fee_kindJ\x04\x08\x01\x10\x02"j\n\tTaxAmount\x12 \n\x03isk\x18\x01 \x01(\x0b2\x11.eve.isk.CurrencyH\x00\x12"\n\x04plex\x18\x02 \x01(\x0b2\x12.eve.plex.CurrencyH\x00\x12\x10\n\x06no_tax\x18\x03 \x01(\x08H\x00B\x05\n\x03tax"_\n\x08BuyerFee\x125\n\x0eloyalty_points\x18\x01 \x01(\x0b2\x1b.eve.loyaltypoints.CurrencyH\x00\x12\x10\n\x06no_fee\x18\x02 \x01(\x08H\x00B\n\n\x08fee_kindB@Z>github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/marketb\x06proto3', dependencies=[eve_dot_isk_dot_isk__pb2.DESCRIPTOR, eve_dot_loyaltypoints_dot_loyaltypoints__pb2.DESCRIPTOR, eve_dot_plex_dot_plex__pb2.DESCRIPTOR])
_BROKERFEE = _descriptor.Descriptor(name='BrokerFee', full_name='eve.cosmetic.market.BrokerFee', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='no_fee', full_name='eve.cosmetic.market.BrokerFee.no_fee', index=0, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='isk', full_name='eve.cosmetic.market.BrokerFee.isk', index=1, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='fee_kind', full_name='eve.cosmetic.market.BrokerFee.fee_kind', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=136, serialized_end=217)
_TAXAMOUNT = _descriptor.Descriptor(name='TaxAmount', full_name='eve.cosmetic.market.TaxAmount', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='isk', full_name='eve.cosmetic.market.TaxAmount.isk', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='plex', full_name='eve.cosmetic.market.TaxAmount.plex', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='no_tax', full_name='eve.cosmetic.market.TaxAmount.no_tax', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='tax', full_name='eve.cosmetic.market.TaxAmount.tax', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=219, serialized_end=325)
_BUYERFEE = _descriptor.Descriptor(name='BuyerFee', full_name='eve.cosmetic.market.BuyerFee', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='loyalty_points', full_name='eve.cosmetic.market.BuyerFee.loyalty_points', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='no_fee', full_name='eve.cosmetic.market.BuyerFee.no_fee', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='fee_kind', full_name='eve.cosmetic.market.BuyerFee.fee_kind', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=327, serialized_end=422)
_BROKERFEE.fields_by_name['isk'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_BROKERFEE.oneofs_by_name['fee_kind'].fields.append(_BROKERFEE.fields_by_name['no_fee'])
_BROKERFEE.fields_by_name['no_fee'].containing_oneof = _BROKERFEE.oneofs_by_name['fee_kind']
_BROKERFEE.oneofs_by_name['fee_kind'].fields.append(_BROKERFEE.fields_by_name['isk'])
_BROKERFEE.fields_by_name['isk'].containing_oneof = _BROKERFEE.oneofs_by_name['fee_kind']
_TAXAMOUNT.fields_by_name['isk'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_TAXAMOUNT.fields_by_name['plex'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_TAXAMOUNT.oneofs_by_name['tax'].fields.append(_TAXAMOUNT.fields_by_name['isk'])
_TAXAMOUNT.fields_by_name['isk'].containing_oneof = _TAXAMOUNT.oneofs_by_name['tax']
_TAXAMOUNT.oneofs_by_name['tax'].fields.append(_TAXAMOUNT.fields_by_name['plex'])
_TAXAMOUNT.fields_by_name['plex'].containing_oneof = _TAXAMOUNT.oneofs_by_name['tax']
_TAXAMOUNT.oneofs_by_name['tax'].fields.append(_TAXAMOUNT.fields_by_name['no_tax'])
_TAXAMOUNT.fields_by_name['no_tax'].containing_oneof = _TAXAMOUNT.oneofs_by_name['tax']
_BUYERFEE.fields_by_name['loyalty_points'].message_type = eve_dot_loyaltypoints_dot_loyaltypoints__pb2._CURRENCY
_BUYERFEE.oneofs_by_name['fee_kind'].fields.append(_BUYERFEE.fields_by_name['loyalty_points'])
_BUYERFEE.fields_by_name['loyalty_points'].containing_oneof = _BUYERFEE.oneofs_by_name['fee_kind']
_BUYERFEE.oneofs_by_name['fee_kind'].fields.append(_BUYERFEE.fields_by_name['no_fee'])
_BUYERFEE.fields_by_name['no_fee'].containing_oneof = _BUYERFEE.oneofs_by_name['fee_kind']
DESCRIPTOR.message_types_by_name['BrokerFee'] = _BROKERFEE
DESCRIPTOR.message_types_by_name['TaxAmount'] = _TAXAMOUNT
DESCRIPTOR.message_types_by_name['BuyerFee'] = _BUYERFEE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
BrokerFee = _reflection.GeneratedProtocolMessageType('BrokerFee', (_message.Message,), {'DESCRIPTOR': _BROKERFEE,
 '__module__': 'eve.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(BrokerFee)
TaxAmount = _reflection.GeneratedProtocolMessageType('TaxAmount', (_message.Message,), {'DESCRIPTOR': _TAXAMOUNT,
 '__module__': 'eve.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(TaxAmount)
BuyerFee = _reflection.GeneratedProtocolMessageType('BuyerFee', (_message.Message,), {'DESCRIPTOR': _BUYERFEE,
 '__module__': 'eve.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(BuyerFee)
DESCRIPTOR._options = None
