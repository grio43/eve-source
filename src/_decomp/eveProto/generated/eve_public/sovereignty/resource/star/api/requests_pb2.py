#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\sovereignty\resource\star\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.sovereignty.resource.star import star_pb2 as eve__public_dot_sovereignty_dot_resource_dot_star_dot_star__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/sovereignty/resource/star/api/requests.proto', package='eve_public.sovereignty.resource.star.api', syntax='proto3', serialized_options='ZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/resource/star/api', create_key=_descriptor._internal_create_key, serialized_pb='\n7eve_public/sovereignty/resource/star/api/requests.proto\x12(eve_public.sovereignty.resource.star.api\x1a/eve_public/sovereignty/resource/star/star.proto"\x1d\n\x1bGetAllConfigurationsRequest"k\n\x1cGetAllConfigurationsResponse\x12K\n\x0econfigurations\x18\x01 \x03(\x0b23.eve_public.sovereignty.resource.star.ConfigurationBUZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/resource/star/apib\x06proto3', dependencies=[eve__public_dot_sovereignty_dot_resource_dot_star_dot_star__pb2.DESCRIPTOR])
_GETALLCONFIGURATIONSREQUEST = _descriptor.Descriptor(name='GetAllConfigurationsRequest', full_name='eve_public.sovereignty.resource.star.api.GetAllConfigurationsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=179)
_GETALLCONFIGURATIONSRESPONSE = _descriptor.Descriptor(name='GetAllConfigurationsResponse', full_name='eve_public.sovereignty.resource.star.api.GetAllConfigurationsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='configurations', full_name='eve_public.sovereignty.resource.star.api.GetAllConfigurationsResponse.configurations', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=181, serialized_end=288)
_GETALLCONFIGURATIONSRESPONSE.fields_by_name['configurations'].message_type = eve__public_dot_sovereignty_dot_resource_dot_star_dot_star__pb2._CONFIGURATION
DESCRIPTOR.message_types_by_name['GetAllConfigurationsRequest'] = _GETALLCONFIGURATIONSREQUEST
DESCRIPTOR.message_types_by_name['GetAllConfigurationsResponse'] = _GETALLCONFIGURATIONSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllConfigurationsRequest = _reflection.GeneratedProtocolMessageType('GetAllConfigurationsRequest', (_message.Message,), {'DESCRIPTOR': _GETALLCONFIGURATIONSREQUEST,
 '__module__': 'eve_public.sovereignty.resource.star.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllConfigurationsRequest)
GetAllConfigurationsResponse = _reflection.GeneratedProtocolMessageType('GetAllConfigurationsResponse', (_message.Message,), {'DESCRIPTOR': _GETALLCONFIGURATIONSRESPONSE,
 '__module__': 'eve_public.sovereignty.resource.star.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllConfigurationsResponse)
DESCRIPTOR._options = None
