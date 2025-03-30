#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\any_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='google/protobuf/any.proto', package='google.protobuf', syntax='proto3', serialized_options='\n\x13com.google.protobufB\x08AnyProtoP\x01Z,google.golang.org/protobuf/types/known/anypb\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypes', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19google/protobuf/any.proto\x12\x0fgoogle.protobuf"&\n\x03Any\x12\x10\n\x08type_url\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0cBv\n\x13com.google.protobufB\x08AnyProtoP\x01Z,google.golang.org/protobuf/types/known/anypb\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesb\x06proto3')
_ANY = _descriptor.Descriptor(name='Any', full_name='google.protobuf.Any', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type_url', full_name='google.protobuf.Any.type_url', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='value', full_name='google.protobuf.Any.value', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=46, serialized_end=84)
DESCRIPTOR.message_types_by_name['Any'] = _ANY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Any = _reflection.GeneratedProtocolMessageType('Any', (_message.Message,), {'DESCRIPTOR': _ANY,
 '__module__': 'google.protobuf.any_pb2'})
_sym_db.RegisterMessage(Any)
DESCRIPTOR._options = None
