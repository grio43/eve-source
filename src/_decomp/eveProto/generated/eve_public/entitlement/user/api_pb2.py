#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\entitlement\user\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.entitlement.user import entitlement_pb2 as eve__public_dot_entitlement_dot_user_dot_entitlement__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/entitlement/user/api.proto', package='eve_public.entitlement.user.api', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/user/api', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve_public/entitlement/user/api.proto\x12\x1feve_public.entitlement.user.api\x1a-eve_public/entitlement/user/entitlement.proto"\x0c\n\nGetRequest"X\n\x0bGetResponse\x12I\n\x0bentitlement\x18\x01 \x01(\x0b24.eve_public.entitlement.user.entitlement.EntitlementBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/user/apib\x06proto3', dependencies=[eve__public_dot_entitlement_dot_user_dot_entitlement__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.entitlement.user.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=121, serialized_end=133)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.entitlement.user.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.entitlement.user.api.GetResponse.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=135, serialized_end=223)
_GETRESPONSE.fields_by_name['entitlement'].message_type = eve__public_dot_entitlement_dot_user_dot_entitlement__pb2._ENTITLEMENT
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.entitlement.user.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.entitlement.user.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
