#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\resource\star\star_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.star import star_pb2 as eve_dot_star_dot_star__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/resource/star/star.proto', package='eve.sovereignty.resource.star', syntax='proto3', serialized_options='ZHgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/resource/star', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/sovereignty/resource/star/star.proto\x12\x1deve.sovereignty.resource.star\x1a\x13eve/star/star.proto"B\n\rConfiguration\x12"\n\x04star\x18\x01 \x01(\x0b2\x14.eve.star.Identifier\x12\r\n\x05power\x18\x02 \x01(\x04BJZHgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/resource/starb\x06proto3', dependencies=[eve_dot_star_dot_star__pb2.DESCRIPTOR])
_CONFIGURATION = _descriptor.Descriptor(name='Configuration', full_name='eve.sovereignty.resource.star.Configuration', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='star', full_name='eve.sovereignty.resource.star.Configuration.star', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='power', full_name='eve.sovereignty.resource.star.Configuration.power', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=96, serialized_end=162)
_CONFIGURATION.fields_by_name['star'].message_type = eve_dot_star_dot_star__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Configuration'] = _CONFIGURATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Configuration = _reflection.GeneratedProtocolMessageType('Configuration', (_message.Message,), {'DESCRIPTOR': _CONFIGURATION,
 '__module__': 'eve.sovereignty.resource.star.star_pb2'})
_sym_db.RegisterMessage(Configuration)
DESCRIPTOR._options = None
