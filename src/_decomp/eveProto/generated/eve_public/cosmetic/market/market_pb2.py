#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\market\market_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.isk import isk_pb2 as eve__public_dot_isk_dot_isk__pb2
from eveProto.generated.eve_public.loyaltypoints import loyaltypoints_pb2 as eve__public_dot_loyaltypoints_dot_loyaltypoints__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/market/market.proto', package='eve_public.cosmetic.market', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/market', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve_public/cosmetic/market/market.proto\x12\x1aeve_public.cosmetic.market\x1a\x18eve_public/isk/isk.proto\x1a,eve_public/loyaltypoints/loyaltypoints.proto\x1a\x1egoogle/protobuf/duration.proto"c\n\tBrokerFee\x12/\n\x08duration\x18\x01 \x01(\x0b2\x19.google.protobuf.DurationB\x02\x18\x01\x12%\n\x03fee\x18\x02 \x01(\x0b2\x18.eve_public.isk.Currency"\'\n\x07TaxRate\x12\r\n\x05units\x18\x01 \x01(\x12\x12\r\n\x05nanos\x18\x02 \x01(\x11"F\n\x08BuyerFee\x12:\n\x0eloyalty_points\x18\x01 \x01(\x0b2".eve_public.loyaltypoints.CurrencyBGZEgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/marketb\x06proto3', dependencies=[eve__public_dot_isk_dot_isk__pb2.DESCRIPTOR, eve__public_dot_loyaltypoints_dot_loyaltypoints__pb2.DESCRIPTOR, google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_BROKERFEE = _descriptor.Descriptor(name='BrokerFee', full_name='eve_public.cosmetic.market.BrokerFee', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='duration', full_name='eve_public.cosmetic.market.BrokerFee.duration', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='fee', full_name='eve_public.cosmetic.market.BrokerFee.fee', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=175, serialized_end=274)
_TAXRATE = _descriptor.Descriptor(name='TaxRate', full_name='eve_public.cosmetic.market.TaxRate', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='units', full_name='eve_public.cosmetic.market.TaxRate.units', index=0, number=1, type=18, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve_public.cosmetic.market.TaxRate.nanos', index=1, number=2, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=276, serialized_end=315)
_BUYERFEE = _descriptor.Descriptor(name='BuyerFee', full_name='eve_public.cosmetic.market.BuyerFee', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='loyalty_points', full_name='eve_public.cosmetic.market.BuyerFee.loyalty_points', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=317, serialized_end=387)
_BROKERFEE.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_BROKERFEE.fields_by_name['fee'].message_type = eve__public_dot_isk_dot_isk__pb2._CURRENCY
_BUYERFEE.fields_by_name['loyalty_points'].message_type = eve__public_dot_loyaltypoints_dot_loyaltypoints__pb2._CURRENCY
DESCRIPTOR.message_types_by_name['BrokerFee'] = _BROKERFEE
DESCRIPTOR.message_types_by_name['TaxRate'] = _TAXRATE
DESCRIPTOR.message_types_by_name['BuyerFee'] = _BUYERFEE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
BrokerFee = _reflection.GeneratedProtocolMessageType('BrokerFee', (_message.Message,), {'DESCRIPTOR': _BROKERFEE,
 '__module__': 'eve_public.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(BrokerFee)
TaxRate = _reflection.GeneratedProtocolMessageType('TaxRate', (_message.Message,), {'DESCRIPTOR': _TAXRATE,
 '__module__': 'eve_public.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(TaxRate)
BuyerFee = _reflection.GeneratedProtocolMessageType('BuyerFee', (_message.Message,), {'DESCRIPTOR': _BUYERFEE,
 '__module__': 'eve_public.cosmetic.market.market_pb2'})
_sym_db.RegisterMessage(BuyerFee)
DESCRIPTOR._options = None
_BROKERFEE.fields_by_name['duration']._options = None
