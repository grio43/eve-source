#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\payment\token\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.payment.token import token_pb2 as eve_dot_payment_dot_token_dot_token__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/payment/token/api.proto', package='eve.payment.token.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/payment/token/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/payment/token/api.proto\x12\x15eve.payment.token.api\x1a\x1deve/payment/token/token.proto\x1a\x13eve/user/user.proto":\n\nGetRequest\x12,\n\x05token\x18\x01 \x01(\x0b2\x1d.eve.payment.token.Identifier";\n\x0bGetResponse\x12,\n\x05token\x18\x01 \x01(\x0b2\x1d.eve.payment.token.Attributes"?\n\x19GetQuickPayForUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"K\n\x1aGetQuickPayForUserResponse\x12-\n\x06tokens\x18\x01 \x03(\x0b2\x1d.eve.payment.token.Identifier":\n\x14GetAllForUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"F\n\x15GetAllForUserResponse\x12-\n\x06tokens\x18\x01 \x03(\x0b2\x1d.eve.payment.token.Identifier">\n\x18DisableAllForUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"\x1b\n\x19DisableAllForUserResponseBBZ@github.com/ccpgames/eve-proto-go/generated/eve/payment/token/apib\x06proto3', dependencies=[eve_dot_payment_dot_token_dot_token__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.payment.token.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='token', full_name='eve.payment.token.api.GetRequest.token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=106, serialized_end=164)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.payment.token.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='token', full_name='eve.payment.token.api.GetResponse.token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=166, serialized_end=225)
_GETQUICKPAYFORUSERREQUEST = _descriptor.Descriptor(name='GetQuickPayForUserRequest', full_name='eve.payment.token.api.GetQuickPayForUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.payment.token.api.GetQuickPayForUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=227, serialized_end=290)
_GETQUICKPAYFORUSERRESPONSE = _descriptor.Descriptor(name='GetQuickPayForUserResponse', full_name='eve.payment.token.api.GetQuickPayForUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='tokens', full_name='eve.payment.token.api.GetQuickPayForUserResponse.tokens', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=292, serialized_end=367)
_GETALLFORUSERREQUEST = _descriptor.Descriptor(name='GetAllForUserRequest', full_name='eve.payment.token.api.GetAllForUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.payment.token.api.GetAllForUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=369, serialized_end=427)
_GETALLFORUSERRESPONSE = _descriptor.Descriptor(name='GetAllForUserResponse', full_name='eve.payment.token.api.GetAllForUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='tokens', full_name='eve.payment.token.api.GetAllForUserResponse.tokens', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=429, serialized_end=499)
_DISABLEALLFORUSERREQUEST = _descriptor.Descriptor(name='DisableAllForUserRequest', full_name='eve.payment.token.api.DisableAllForUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.payment.token.api.DisableAllForUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=501, serialized_end=563)
_DISABLEALLFORUSERRESPONSE = _descriptor.Descriptor(name='DisableAllForUserResponse', full_name='eve.payment.token.api.DisableAllForUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=565, serialized_end=592)
_GETREQUEST.fields_by_name['token'].message_type = eve_dot_payment_dot_token_dot_token__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['token'].message_type = eve_dot_payment_dot_token_dot_token__pb2._ATTRIBUTES
_GETQUICKPAYFORUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETQUICKPAYFORUSERRESPONSE.fields_by_name['tokens'].message_type = eve_dot_payment_dot_token_dot_token__pb2._IDENTIFIER
_GETALLFORUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETALLFORUSERRESPONSE.fields_by_name['tokens'].message_type = eve_dot_payment_dot_token_dot_token__pb2._IDENTIFIER
_DISABLEALLFORUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetQuickPayForUserRequest'] = _GETQUICKPAYFORUSERREQUEST
DESCRIPTOR.message_types_by_name['GetQuickPayForUserResponse'] = _GETQUICKPAYFORUSERRESPONSE
DESCRIPTOR.message_types_by_name['GetAllForUserRequest'] = _GETALLFORUSERREQUEST
DESCRIPTOR.message_types_by_name['GetAllForUserResponse'] = _GETALLFORUSERRESPONSE
DESCRIPTOR.message_types_by_name['DisableAllForUserRequest'] = _DISABLEALLFORUSERREQUEST
DESCRIPTOR.message_types_by_name['DisableAllForUserResponse'] = _DISABLEALLFORUSERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetQuickPayForUserRequest = _reflection.GeneratedProtocolMessageType('GetQuickPayForUserRequest', (_message.Message,), {'DESCRIPTOR': _GETQUICKPAYFORUSERREQUEST,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetQuickPayForUserRequest)
GetQuickPayForUserResponse = _reflection.GeneratedProtocolMessageType('GetQuickPayForUserResponse', (_message.Message,), {'DESCRIPTOR': _GETQUICKPAYFORUSERRESPONSE,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetQuickPayForUserResponse)
GetAllForUserRequest = _reflection.GeneratedProtocolMessageType('GetAllForUserRequest', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERREQUEST,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetAllForUserRequest)
GetAllForUserResponse = _reflection.GeneratedProtocolMessageType('GetAllForUserResponse', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERRESPONSE,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(GetAllForUserResponse)
DisableAllForUserRequest = _reflection.GeneratedProtocolMessageType('DisableAllForUserRequest', (_message.Message,), {'DESCRIPTOR': _DISABLEALLFORUSERREQUEST,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(DisableAllForUserRequest)
DisableAllForUserResponse = _reflection.GeneratedProtocolMessageType('DisableAllForUserResponse', (_message.Message,), {'DESCRIPTOR': _DISABLEALLFORUSERRESPONSE,
 '__module__': 'eve.payment.token.api_pb2'})
_sym_db.RegisterMessage(DisableAllForUserResponse)
DESCRIPTOR._options = None
