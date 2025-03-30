#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vendors\fusionauth\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from eveProto.generated.eve.vendors.fusionauth import user_pb2 as eve_dot_vendors_dot_fusionauth_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vendors/fusionauth/api/api.proto', package='eve.vendors.fusionauth.api', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/fusionauth/api', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/vendors/fusionauth/api/api.proto\x12\x1aeve.vendors.fusionauth.api\x1a\x13eve/user/user.proto\x1a!eve/vendors/fusionauth/user.proto"H\n\x0fLinkUserRequest\x125\n\x04user\x18\x01 \x01(\x0b2\'.eve.vendors.fusionauth.user.Identifier"6\n\x10LinkUserResponse\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/fusionauth/apib\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR, eve_dot_vendors_dot_fusionauth_dot_user__pb2.DESCRIPTOR])
_LINKUSERREQUEST = _descriptor.Descriptor(name='LinkUserRequest', full_name='eve.vendors.fusionauth.api.LinkUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.vendors.fusionauth.api.LinkUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=124, serialized_end=196)
_LINKUSERRESPONSE = _descriptor.Descriptor(name='LinkUserResponse', full_name='eve.vendors.fusionauth.api.LinkUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.vendors.fusionauth.api.LinkUserResponse.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=198, serialized_end=252)
_LINKUSERREQUEST.fields_by_name['user'].message_type = eve_dot_vendors_dot_fusionauth_dot_user__pb2._IDENTIFIER
_LINKUSERRESPONSE.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['LinkUserRequest'] = _LINKUSERREQUEST
DESCRIPTOR.message_types_by_name['LinkUserResponse'] = _LINKUSERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
LinkUserRequest = _reflection.GeneratedProtocolMessageType('LinkUserRequest', (_message.Message,), {'DESCRIPTOR': _LINKUSERREQUEST,
 '__module__': 'eve.vendors.fusionauth.api.api_pb2'})
_sym_db.RegisterMessage(LinkUserRequest)
LinkUserResponse = _reflection.GeneratedProtocolMessageType('LinkUserResponse', (_message.Message,), {'DESCRIPTOR': _LINKUSERRESPONSE,
 '__module__': 'eve.vendors.fusionauth.api.api_pb2'})
_sym_db.RegisterMessage(LinkUserResponse)
DESCRIPTOR._options = None
