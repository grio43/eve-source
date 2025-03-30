#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\twofactor\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/twofactor/api/requests.proto', package='eve.user.twofactor.api', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/user/twofactor/api', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/user/twofactor/api/requests.proto\x12\x16eve.user.twofactor.api\x1a\x13eve/user/user.proto"D\n\x1eGetAuthenticatorEnabledRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"2\n\x1fGetAuthenticatorEnabledResponse\x12\x0f\n\x07enabled\x18\x01 \x01(\x08BCZAgithub.com/ccpgames/eve-proto-go/generated/eve/user/twofactor/apib\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETAUTHENTICATORENABLEDREQUEST = _descriptor.Descriptor(name='GetAuthenticatorEnabledRequest', full_name='eve.user.twofactor.api.GetAuthenticatorEnabledRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.twofactor.api.GetAuthenticatorEnabledRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=154)
_GETAUTHENTICATORENABLEDRESPONSE = _descriptor.Descriptor(name='GetAuthenticatorEnabledResponse', full_name='eve.user.twofactor.api.GetAuthenticatorEnabledResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='enabled', full_name='eve.user.twofactor.api.GetAuthenticatorEnabledResponse.enabled', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=156, serialized_end=206)
_GETAUTHENTICATORENABLEDREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetAuthenticatorEnabledRequest'] = _GETAUTHENTICATORENABLEDREQUEST
DESCRIPTOR.message_types_by_name['GetAuthenticatorEnabledResponse'] = _GETAUTHENTICATORENABLEDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAuthenticatorEnabledRequest = _reflection.GeneratedProtocolMessageType('GetAuthenticatorEnabledRequest', (_message.Message,), {'DESCRIPTOR': _GETAUTHENTICATORENABLEDREQUEST,
 '__module__': 'eve.user.twofactor.api.requests_pb2'})
_sym_db.RegisterMessage(GetAuthenticatorEnabledRequest)
GetAuthenticatorEnabledResponse = _reflection.GeneratedProtocolMessageType('GetAuthenticatorEnabledResponse', (_message.Message,), {'DESCRIPTOR': _GETAUTHENTICATORENABLEDRESPONSE,
 '__module__': 'eve.user.twofactor.api.requests_pb2'})
_sym_db.RegisterMessage(GetAuthenticatorEnabledResponse)
DESCRIPTOR._options = None
