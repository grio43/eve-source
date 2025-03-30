#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\token\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.payment.token import token_pb2 as eve__public_dot_payment_dot_token_dot_token__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/token/api.proto', package='eve_public.payment.token.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/token/api', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve_public/payment/token/api.proto\x12\x1ceve_public.payment.token.api\x1a$eve_public/payment/token/token.proto"A\n\nGetRequest\x123\n\x05token\x18\x01 \x01(\x0b2$.eve_public.payment.token.Identifier"B\n\x0bGetResponse\x123\n\x05token\x18\x01 \x01(\x0b2$.eve_public.payment.token.Attributes"\x14\n\x12GetQuickPayRequest"K\n\x13GetQuickPayResponse\x124\n\x06tokens\x18\x01 \x03(\x0b2$.eve_public.payment.token.Identifier"\x13\n\x11DisableAllRequest"\x14\n\x12DisableAllResponseBIZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/token/apib\x06proto3', dependencies=[eve__public_dot_payment_dot_token_dot_token__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.payment.token.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='token', full_name='eve_public.payment.token.api.GetRequest.token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=106, serialized_end=171)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.payment.token.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='token', full_name='eve_public.payment.token.api.GetResponse.token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=173, serialized_end=239)
_GETQUICKPAYREQUEST = _descriptor.Descriptor(name='GetQuickPayRequest', full_name='eve_public.payment.token.api.GetQuickPayRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=241, serialized_end=261)
_GETQUICKPAYRESPONSE = _descriptor.Descriptor(name='GetQuickPayResponse', full_name='eve_public.payment.token.api.GetQuickPayResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='tokens', full_name='eve_public.payment.token.api.GetQuickPayResponse.tokens', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=263, serialized_end=338)
_DISABLEALLREQUEST = _descriptor.Descriptor(name='DisableAllRequest', full_name='eve_public.payment.token.api.DisableAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=340, serialized_end=359)
_DISABLEALLRESPONSE = _descriptor.Descriptor(name='DisableAllResponse', full_name='eve_public.payment.token.api.DisableAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=361, serialized_end=381)
_GETREQUEST.fields_by_name['token'].message_type = eve__public_dot_payment_dot_token_dot_token__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['token'].message_type = eve__public_dot_payment_dot_token_dot_token__pb2._ATTRIBUTES
_GETQUICKPAYRESPONSE.fields_by_name['tokens'].message_type = eve__public_dot_payment_dot_token_dot_token__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetQuickPayRequest'] = _GETQUICKPAYREQUEST
DESCRIPTOR.message_types_by_name['GetQuickPayResponse'] = _GETQUICKPAYRESPONSE
DESCRIPTOR.message_types_by_name['DisableAllRequest'] = _DISABLEALLREQUEST
DESCRIPTOR.message_types_by_name['DisableAllResponse'] = _DISABLEALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetQuickPayRequest = _reflection.GeneratedProtocolMessageType('GetQuickPayRequest', (_message.Message,), {'DESCRIPTOR': _GETQUICKPAYREQUEST,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetQuickPayRequest)
GetQuickPayResponse = _reflection.GeneratedProtocolMessageType('GetQuickPayResponse', (_message.Message,), {'DESCRIPTOR': _GETQUICKPAYRESPONSE,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetQuickPayResponse)
DisableAllRequest = _reflection.GeneratedProtocolMessageType('DisableAllRequest', (_message.Message,), {'DESCRIPTOR': _DISABLEALLREQUEST,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(DisableAllRequest)
DisableAllResponse = _reflection.GeneratedProtocolMessageType('DisableAllResponse', (_message.Message,), {'DESCRIPTOR': _DISABLEALLRESPONSE,
 '__module__': 'eve_public.payment.token.api_pb2'})
_sym_db.RegisterMessage(DisableAllResponse)
DESCRIPTOR._options = None
