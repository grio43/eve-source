#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\network\rtt_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/network/rtt.proto', package='eve_public.network.rtt', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/network/rtt', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve_public/network/rtt.proto\x12\x16eve_public.network.rtt\x1a\x1egoogle/protobuf/duration.proto"\xbb\x01\n\x06Sample\x129\n\x08protocol\x18\x01 \x01(\x0e2\'.eve_public.network.rtt.Sample.Protocol\x12&\n\x03rtt\x18\x02 \x01(\x0b2\x19.google.protobuf.Duration"N\n\x08Protocol\x12\x18\n\x14PROTOCOL_UNSPECIFIED\x10\x00\x12\x15\n\x11PROTOCOL_MACHONET\x10\x01\x12\x11\n\rPROTOCOL_GRPC\x10\x02BCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/network/rttb\x06proto3', dependencies=[google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_SAMPLE_PROTOCOL = _descriptor.EnumDescriptor(name='Protocol', full_name='eve_public.network.rtt.Sample.Protocol', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PROTOCOL_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='PROTOCOL_MACHONET', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='PROTOCOL_GRPC', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=198, serialized_end=276)
_sym_db.RegisterEnumDescriptor(_SAMPLE_PROTOCOL)
_SAMPLE = _descriptor.Descriptor(name='Sample', full_name='eve_public.network.rtt.Sample', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='protocol', full_name='eve_public.network.rtt.Sample.protocol', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='rtt', full_name='eve_public.network.rtt.Sample.rtt', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_SAMPLE_PROTOCOL], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=89, serialized_end=276)
_SAMPLE.fields_by_name['protocol'].enum_type = _SAMPLE_PROTOCOL
_SAMPLE.fields_by_name['rtt'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_SAMPLE_PROTOCOL.containing_type = _SAMPLE
DESCRIPTOR.message_types_by_name['Sample'] = _SAMPLE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Sample = _reflection.GeneratedProtocolMessageType('Sample', (_message.Message,), {'DESCRIPTOR': _SAMPLE,
 '__module__': 'eve_public.network.rtt_pb2'})
_sym_db.RegisterMessage(Sample)
DESCRIPTOR._options = None
