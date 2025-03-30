#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\twofactor\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/twofactor/api/admin/requests.proto', package='eve.user.twofactor.api.admin', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/user/twofactor/api.admin', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/user/twofactor/api/admin/requests.proto\x12\x1ceve.user.twofactor.api.admin\x1a\x13eve/user/user.proto"A\n\x1bDisableAuthenticatorRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"\x1e\n\x1cDisableAuthenticatorResponseBIZGgithub.com/ccpgames/eve-proto-go/generated/eve/user/twofactor/api.adminb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_DISABLEAUTHENTICATORREQUEST = _descriptor.Descriptor(name='DisableAuthenticatorRequest', full_name='eve.user.twofactor.api.admin.DisableAuthenticatorRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.twofactor.api.admin.DisableAuthenticatorRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=98, serialized_end=163)
_DISABLEAUTHENTICATORRESPONSE = _descriptor.Descriptor(name='DisableAuthenticatorResponse', full_name='eve.user.twofactor.api.admin.DisableAuthenticatorResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=165, serialized_end=195)
_DISABLEAUTHENTICATORREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['DisableAuthenticatorRequest'] = _DISABLEAUTHENTICATORREQUEST
DESCRIPTOR.message_types_by_name['DisableAuthenticatorResponse'] = _DISABLEAUTHENTICATORRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DisableAuthenticatorRequest = _reflection.GeneratedProtocolMessageType('DisableAuthenticatorRequest', (_message.Message,), {'DESCRIPTOR': _DISABLEAUTHENTICATORREQUEST,
 '__module__': 'eve.user.twofactor.api.admin.requests_pb2'})
_sym_db.RegisterMessage(DisableAuthenticatorRequest)
DisableAuthenticatorResponse = _reflection.GeneratedProtocolMessageType('DisableAuthenticatorResponse', (_message.Message,), {'DESCRIPTOR': _DISABLEAUTHENTICATORRESPONSE,
 '__module__': 'eve.user.twofactor.api.admin.requests_pb2'})
_sym_db.RegisterMessage(DisableAuthenticatorResponse)
DESCRIPTOR._options = None
