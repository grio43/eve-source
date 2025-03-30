#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\id\auth\auth_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/id/auth/auth.proto', package='eve.id.auth', syntax='proto3', serialized_options='Z6github.com/ccpgames/eve-proto-go/generated/eve/id/auth', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/id/auth/auth.proto\x12\x0beve.id.auth"\x18\n\x03JWT\x12\x11\n\tbase64url\x18\x01 \x01(\t",\n\x0bAccessToken\x12\x1d\n\x03jwt\x18\x01 \x01(\x0b2\x10.eve.id.auth.JWTB8Z6github.com/ccpgames/eve-proto-go/generated/eve/id/authb\x06proto3')
_JWT = _descriptor.Descriptor(name='JWT', full_name='eve.id.auth.JWT', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='base64url', full_name='eve.id.auth.JWT.base64url', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=39, serialized_end=63)
_ACCESSTOKEN = _descriptor.Descriptor(name='AccessToken', full_name='eve.id.auth.AccessToken', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='jwt', full_name='eve.id.auth.AccessToken.jwt', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=65, serialized_end=109)
_ACCESSTOKEN.fields_by_name['jwt'].message_type = _JWT
DESCRIPTOR.message_types_by_name['JWT'] = _JWT
DESCRIPTOR.message_types_by_name['AccessToken'] = _ACCESSTOKEN
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
JWT = _reflection.GeneratedProtocolMessageType('JWT', (_message.Message,), {'DESCRIPTOR': _JWT,
 '__module__': 'eve.id.auth.auth_pb2'})
_sym_db.RegisterMessage(JWT)
AccessToken = _reflection.GeneratedProtocolMessageType('AccessToken', (_message.Message,), {'DESCRIPTOR': _ACCESSTOKEN,
 '__module__': 'eve.id.auth.auth_pb2'})
_sym_db.RegisterMessage(AccessToken)
DESCRIPTOR._options = None
