#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\payment\code\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.fulfillment.offer import offer_pb2 as eve_dot_fulfillment_dot_offer_dot_offer__pb2
from eveProto.generated.eve.payment.code import code_pb2 as eve_dot_payment_dot_code_dot_code__pb2
from eveProto.generated.eve.payment.customer import customer_pb2 as eve_dot_payment_dot_customer_dot_customer__pb2
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
from eveProto.generated.eve.store.offer import offer_pb2 as eve_dot_store_dot_offer_dot_offer__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/payment/code/api.proto', package='eve.payment.code.api', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/payment/code/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/payment/code/api.proto\x12\x14eve.payment.code.api\x1a!eve/fulfillment/offer/offer.proto\x1a\x1beve/payment/code/code.proto\x1a#eve/payment/customer/customer.proto\x1a\x19eve/payment/payment.proto\x1a\x1beve/store/offer/offer.proto\x1a\x13eve/user/user.proto"\x8c\x03\n\x08Redeemed\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x122\n\x08customer\x18\x02 \x01(\x0b2 .eve.payment.customer.Identifier\x124\n\x05offer\x18\x03 \x01(\x0b2!.eve.fulfillment.offer.IdentifierB\x02\x18\x01\x12(\n\x07payment\x18\x04 \x01(\x0b2\x17.eve.payment.Identifier\x123\n\x12payment_attributes\x18\x05 \x01(\x0b2\x17.eve.payment.Attributes\x12*\n\x04code\x18\x06 \x01(\x0b2\x1c.eve.payment.code.Identifier\x125\n\x0fcode_attributes\x18\x07 \x01(\x0b2\x1c.eve.payment.code.Attributes\x120\n\x0bstore_offer\x18\x08 \x01(\x0b2\x1b.eve.store.offer.Identifier"_\n\rRedeemRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12*\n\x04code\x18\x02 \x01(\x0b2\x1c.eve.payment.code.Identifier"<\n\x0eRedeemResponse\x12*\n\x05offer\x18\x01 \x01(\x0b2\x1b.eve.store.offer.IdentifierBAZ?github.com/ccpgames/eve-proto-go/generated/eve/payment/code/apib\x06proto3', dependencies=[eve_dot_fulfillment_dot_offer_dot_offer__pb2.DESCRIPTOR,
 eve_dot_payment_dot_code_dot_code__pb2.DESCRIPTOR,
 eve_dot_payment_dot_customer_dot_customer__pb2.DESCRIPTOR,
 eve_dot_payment_dot_payment__pb2.DESCRIPTOR,
 eve_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR])
_REDEEMED = _descriptor.Descriptor(name='Redeemed', full_name='eve.payment.code.api.Redeemed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.payment.code.api.Redeemed.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='customer', full_name='eve.payment.code.api.Redeemed.customer', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve.payment.code.api.Redeemed.offer', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment', full_name='eve.payment.code.api.Redeemed.payment', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_attributes', full_name='eve.payment.code.api.Redeemed.payment_attributes', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='code', full_name='eve.payment.code.api.Redeemed.code', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='code_attributes', full_name='eve.payment.code.api.Redeemed.code_attributes', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='store_offer', full_name='eve.payment.code.api.Redeemed.store_offer', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=231, serialized_end=627)
_REDEEMREQUEST = _descriptor.Descriptor(name='RedeemRequest', full_name='eve.payment.code.api.RedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.payment.code.api.RedeemRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='code', full_name='eve.payment.code.api.RedeemRequest.code', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=629, serialized_end=724)
_REDEEMRESPONSE = _descriptor.Descriptor(name='RedeemResponse', full_name='eve.payment.code.api.RedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='offer', full_name='eve.payment.code.api.RedeemResponse.offer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=726, serialized_end=786)
_REDEEMED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_REDEEMED.fields_by_name['customer'].message_type = eve_dot_payment_dot_customer_dot_customer__pb2._IDENTIFIER
_REDEEMED.fields_by_name['offer'].message_type = eve_dot_fulfillment_dot_offer_dot_offer__pb2._IDENTIFIER
_REDEEMED.fields_by_name['payment'].message_type = eve_dot_payment_dot_payment__pb2._IDENTIFIER
_REDEEMED.fields_by_name['payment_attributes'].message_type = eve_dot_payment_dot_payment__pb2._ATTRIBUTES
_REDEEMED.fields_by_name['code'].message_type = eve_dot_payment_dot_code_dot_code__pb2._IDENTIFIER
_REDEEMED.fields_by_name['code_attributes'].message_type = eve_dot_payment_dot_code_dot_code__pb2._ATTRIBUTES
_REDEEMED.fields_by_name['store_offer'].message_type = eve_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_REDEEMREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_REDEEMREQUEST.fields_by_name['code'].message_type = eve_dot_payment_dot_code_dot_code__pb2._IDENTIFIER
_REDEEMRESPONSE.fields_by_name['offer'].message_type = eve_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Redeemed'] = _REDEEMED
DESCRIPTOR.message_types_by_name['RedeemRequest'] = _REDEEMREQUEST
DESCRIPTOR.message_types_by_name['RedeemResponse'] = _REDEEMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Redeemed = _reflection.GeneratedProtocolMessageType('Redeemed', (_message.Message,), {'DESCRIPTOR': _REDEEMED,
 '__module__': 'eve.payment.code.api_pb2'})
_sym_db.RegisterMessage(Redeemed)
RedeemRequest = _reflection.GeneratedProtocolMessageType('RedeemRequest', (_message.Message,), {'DESCRIPTOR': _REDEEMREQUEST,
 '__module__': 'eve.payment.code.api_pb2'})
_sym_db.RegisterMessage(RedeemRequest)
RedeemResponse = _reflection.GeneratedProtocolMessageType('RedeemResponse', (_message.Message,), {'DESCRIPTOR': _REDEEMRESPONSE,
 '__module__': 'eve.payment.code.api_pb2'})
_sym_db.RegisterMessage(RedeemResponse)
DESCRIPTOR._options = None
_REDEEMED.fields_by_name['offer']._options = None
