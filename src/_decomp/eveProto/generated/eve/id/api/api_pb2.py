#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\id\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.id import id_pb2 as eve_dot_id_dot_id__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/id/api/api.proto', package='eve.id.api', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/id/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x14eve/id/api/api.proto\x12\neve.id.api\x1a\x0feve/id/id.proto\x1a\x13eve/user/user.proto",\n\nGetRequest\x12\x1e\n\x02id\x18\x01 \x01(\x0b2\x12.eve.id.Identifier"-\n\x0bGetResponse\x12\x1e\n\x02id\x18\x01 \x01(\x0b2\x12.eve.id.Attributes"6\n\x10GetByUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"3\n\x11GetByUserResponse\x12\x1e\n\x02id\x18\x01 \x01(\x0b2\x12.eve.id.IdentifierB7Z5github.com/ccpgames/eve-proto-go/generated/eve/id/apib\x06proto3', dependencies=[eve_dot_id_dot_id__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.id.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.id.api.GetRequest.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=74, serialized_end=118)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.id.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.id.api.GetResponse.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=165)
_GETBYUSERREQUEST = _descriptor.Descriptor(name='GetByUserRequest', full_name='eve.id.api.GetByUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.id.api.GetByUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=167, serialized_end=221)
_GETBYUSERRESPONSE = _descriptor.Descriptor(name='GetByUserResponse', full_name='eve.id.api.GetByUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.id.api.GetByUserResponse.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=223, serialized_end=274)
_GETREQUEST.fields_by_name['id'].message_type = eve_dot_id_dot_id__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['id'].message_type = eve_dot_id_dot_id__pb2._ATTRIBUTES
_GETBYUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETBYUSERRESPONSE.fields_by_name['id'].message_type = eve_dot_id_dot_id__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetByUserRequest'] = _GETBYUSERREQUEST
DESCRIPTOR.message_types_by_name['GetByUserResponse'] = _GETBYUSERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.id.api.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.id.api.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetByUserRequest = _reflection.GeneratedProtocolMessageType('GetByUserRequest', (_message.Message,), {'DESCRIPTOR': _GETBYUSERREQUEST,
 '__module__': 'eve.id.api.api_pb2'})
_sym_db.RegisterMessage(GetByUserRequest)
GetByUserResponse = _reflection.GeneratedProtocolMessageType('GetByUserResponse', (_message.Message,), {'DESCRIPTOR': _GETBYUSERRESPONSE,
 '__module__': 'eve.id.api.api_pb2'})
_sym_db.RegisterMessage(GetByUserResponse)
DESCRIPTOR._options = None
