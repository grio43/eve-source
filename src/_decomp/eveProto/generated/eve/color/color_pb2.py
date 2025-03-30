#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\color\color_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/color/color.proto', package='eve.color', syntax='proto3', serialized_options='Z4github.com/ccpgames/eve-proto-go/generated/eve/color', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/color/color.proto\x12\teve.color"/\n\x03RGB\x12\x0b\n\x03red\x18\x01 \x01(\r\x12\r\n\x05green\x18\x02 \x01(\r\x12\x0c\n\x04blue\x18\x03 \x01(\rB6Z4github.com/ccpgames/eve-proto-go/generated/eve/colorb\x06proto3')
_RGB = _descriptor.Descriptor(name='RGB', full_name='eve.color.RGB', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='red', full_name='eve.color.RGB.red', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='green', full_name='eve.color.RGB.green', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='blue', full_name='eve.color.RGB.blue', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=36, serialized_end=83)
DESCRIPTOR.message_types_by_name['RGB'] = _RGB
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
RGB = _reflection.GeneratedProtocolMessageType('RGB', (_message.Message,), {'DESCRIPTOR': _RGB,
 '__module__': 'eve.color.color_pb2'})
_sym_db.RegisterMessage(RGB)
DESCRIPTOR._options = None
