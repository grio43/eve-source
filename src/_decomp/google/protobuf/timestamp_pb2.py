#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\timestamp_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='google/protobuf/timestamp.proto', package='google.protobuf', syntax='proto3', serialized_options='\n\x13com.google.protobufB\x0eTimestampProtoP\x01Z2google.golang.org/protobuf/types/known/timestamppb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypes', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1fgoogle/protobuf/timestamp.proto\x12\x0fgoogle.protobuf"+\n\tTimestamp\x12\x0f\n\x07seconds\x18\x01 \x01(\x03\x12\r\n\x05nanos\x18\x02 \x01(\x05B\x85\x01\n\x13com.google.protobufB\x0eTimestampProtoP\x01Z2google.golang.org/protobuf/types/known/timestamppb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesb\x06proto3')
_TIMESTAMP = _descriptor.Descriptor(name='Timestamp', full_name='google.protobuf.Timestamp', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='seconds', full_name='google.protobuf.Timestamp.seconds', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='google.protobuf.Timestamp.nanos', index=1, number=2, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=52, serialized_end=95)
DESCRIPTOR.message_types_by_name['Timestamp'] = _TIMESTAMP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Timestamp = _reflection.GeneratedProtocolMessageType('Timestamp', (_message.Message,), {'DESCRIPTOR': _TIMESTAMP,
 '__module__': 'google.protobuf.timestamp_pb2'})
_sym_db.RegisterMessage(Timestamp)
DESCRIPTOR._options = None
