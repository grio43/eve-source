#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\tracecontext_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/tracecontext.proto', package='eve.tracecontext', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/tracecontext', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/tracecontext.proto\x12\x10eve.tracecontext"\x8d\x01\n\x0cTraceContext\x12\x10\n\x08trace_id\x18\x01 \x01(\x0c\x12\x11\n\tparent_id\x18\x02 \x01(\x0c\x12+\n\x05flags\x18\x03 \x01(\x0b2\x1c.eve.tracecontext.TraceFlags\x12+\n\x05state\x18\x04 \x01(\x0b2\x1c.eve.tracecontext.TraceState"\x1d\n\nTraceFlags\x12\x0f\n\x07sampled\x18\x01 \x01(\x08"!\n\nTraceState\x12\x13\n\x0bsample_rate\x18\x01 \x01(\rB=Z;github.com/ccpgames/eve-proto-go/generated/eve/tracecontextb\x06proto3')
_TRACECONTEXT = _descriptor.Descriptor(name='TraceContext', full_name='eve.tracecontext.TraceContext', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='trace_id', full_name='eve.tracecontext.TraceContext.trace_id', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='parent_id', full_name='eve.tracecontext.TraceContext.parent_id', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='flags', full_name='eve.tracecontext.TraceContext.flags', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='state', full_name='eve.tracecontext.TraceContext.state', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=45, serialized_end=186)
_TRACEFLAGS = _descriptor.Descriptor(name='TraceFlags', full_name='eve.tracecontext.TraceFlags', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sampled', full_name='eve.tracecontext.TraceFlags.sampled', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=188, serialized_end=217)
_TRACESTATE = _descriptor.Descriptor(name='TraceState', full_name='eve.tracecontext.TraceState', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sample_rate', full_name='eve.tracecontext.TraceState.sample_rate', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=219, serialized_end=252)
_TRACECONTEXT.fields_by_name['flags'].message_type = _TRACEFLAGS
_TRACECONTEXT.fields_by_name['state'].message_type = _TRACESTATE
DESCRIPTOR.message_types_by_name['TraceContext'] = _TRACECONTEXT
DESCRIPTOR.message_types_by_name['TraceFlags'] = _TRACEFLAGS
DESCRIPTOR.message_types_by_name['TraceState'] = _TRACESTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
TraceContext = _reflection.GeneratedProtocolMessageType('TraceContext', (_message.Message,), {'DESCRIPTOR': _TRACECONTEXT,
 '__module__': 'eve.tracecontext_pb2'})
_sym_db.RegisterMessage(TraceContext)
TraceFlags = _reflection.GeneratedProtocolMessageType('TraceFlags', (_message.Message,), {'DESCRIPTOR': _TRACEFLAGS,
 '__module__': 'eve.tracecontext_pb2'})
_sym_db.RegisterMessage(TraceFlags)
TraceState = _reflection.GeneratedProtocolMessageType('TraceState', (_message.Message,), {'DESCRIPTOR': _TRACESTATE,
 '__module__': 'eve.tracecontext_pb2'})
_sym_db.RegisterMessage(TraceState)
DESCRIPTOR._options = None
