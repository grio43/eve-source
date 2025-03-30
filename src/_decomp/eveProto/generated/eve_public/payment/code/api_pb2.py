#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\code\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.payment.code import code_pb2 as eve__public_dot_payment_dot_code_dot_code__pb2
from eveProto.generated.eve_public.store.offer import offer_pb2 as eve__public_dot_store_dot_offer_dot_offer__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/code/api.proto', package='eve_public.payment.code.api', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/code/api', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve_public/payment/code/api.proto\x12\x1beve_public.payment.code.api\x1a"eve_public/payment/code/code.proto\x1a"eve_public/store/offer/offer.proto"B\n\rRedeemRequest\x121\n\x04code\x18\x01 \x01(\x0b2#.eve_public.payment.code.Identifier"C\n\x0eRedeemResponse\x121\n\x05offer\x18\x01 \x01(\x0b2".eve_public.store.offer.IdentifierBHZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/code/apib\x06proto3', dependencies=[eve__public_dot_payment_dot_code_dot_code__pb2.DESCRIPTOR, eve__public_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR])
_REDEEMREQUEST = _descriptor.Descriptor(name='RedeemRequest', full_name='eve_public.payment.code.api.RedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='code', full_name='eve_public.payment.code.api.RedeemRequest.code', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=138, serialized_end=204)
_REDEEMRESPONSE = _descriptor.Descriptor(name='RedeemResponse', full_name='eve_public.payment.code.api.RedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='offer', full_name='eve_public.payment.code.api.RedeemResponse.offer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=206, serialized_end=273)
_REDEEMREQUEST.fields_by_name['code'].message_type = eve__public_dot_payment_dot_code_dot_code__pb2._IDENTIFIER
_REDEEMRESPONSE.fields_by_name['offer'].message_type = eve__public_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['RedeemRequest'] = _REDEEMREQUEST
DESCRIPTOR.message_types_by_name['RedeemResponse'] = _REDEEMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
RedeemRequest = _reflection.GeneratedProtocolMessageType('RedeemRequest', (_message.Message,), {'DESCRIPTOR': _REDEEMREQUEST,
 '__module__': 'eve_public.payment.code.api_pb2'})
_sym_db.RegisterMessage(RedeemRequest)
RedeemResponse = _reflection.GeneratedProtocolMessageType('RedeemResponse', (_message.Message,), {'DESCRIPTOR': _REDEEMRESPONSE,
 '__module__': 'eve_public.payment.code.api_pb2'})
_sym_db.RegisterMessage(RedeemResponse)
DESCRIPTOR._options = None
