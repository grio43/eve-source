#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\sovereignty\resource\star\star_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.star import star_pb2 as eve__public_dot_star_dot_star__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/sovereignty/resource/star/star.proto', package='eve_public.sovereignty.resource.star', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/resource/star', create_key=_descriptor._internal_create_key, serialized_pb='\n/eve_public/sovereignty/resource/star/star.proto\x12$eve_public.sovereignty.resource.star\x1a\x1aeve_public/star/star.proto"I\n\rConfiguration\x12)\n\x04star\x18\x01 \x01(\x0b2\x1b.eve_public.star.Identifier\x12\r\n\x05power\x18\x02 \x01(\x04BQZOgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/resource/starb\x06proto3', dependencies=[eve__public_dot_star_dot_star__pb2.DESCRIPTOR])
_CONFIGURATION = _descriptor.Descriptor(name='Configuration', full_name='eve_public.sovereignty.resource.star.Configuration', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='star', full_name='eve_public.sovereignty.resource.star.Configuration.star', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='power', full_name='eve_public.sovereignty.resource.star.Configuration.power', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=117, serialized_end=190)
_CONFIGURATION.fields_by_name['star'].message_type = eve__public_dot_star_dot_star__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Configuration'] = _CONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Configuration = _reflection.GeneratedProtocolMessageType('Configuration', (_message.Message,), {'DESCRIPTOR': _CONFIGURATION,
 '__module__': 'eve_public.sovereignty.resource.star.star_pb2'})
_sym_db.RegisterMessage(Configuration)
DESCRIPTOR._options = None
