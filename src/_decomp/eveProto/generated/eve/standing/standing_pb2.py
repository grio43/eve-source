#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\standing\standing_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/standing/standing.proto', package='eve.standing', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/standing', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/standing/standing.proto\x12\x0ceve.standing"%\n\x05Value\x12\r\n\x05units\x18\x01 \x01(\x12\x12\r\n\x05nanos\x18\x02 \x01(\x11B9Z7github.com/ccpgames/eve-proto-go/generated/eve/standingb\x06proto3')
_VALUE = _descriptor.Descriptor(name='Value', full_name='eve.standing.Value', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='units', full_name='eve.standing.Value.units', index=0, number=1, type=18, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve.standing.Value.nanos', index=1, number=2, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=45, serialized_end=82)
DESCRIPTOR.message_types_by_name['Value'] = _VALUE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Value = _reflection.GeneratedProtocolMessageType('Value', (_message.Message,), {'DESCRIPTOR': _VALUE,
 '__module__': 'eve.standing.standing_pb2'})
_sym_db.RegisterMessage(Value)
DESCRIPTOR._options = None
