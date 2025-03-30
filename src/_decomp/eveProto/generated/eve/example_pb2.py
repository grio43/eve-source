#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\example_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/example.proto', package='eve.example', syntax='proto3', serialized_options='Z6github.com/ccpgames/eve-proto-go/generated/eve/example', create_key=_descriptor._internal_create_key, serialized_pb='\n\x11eve/example.proto\x12\x0beve.example".\n\x14ExampleActionRequest\x12\x16\n\x0erequest_string\x18\x01 \x01(\t"0\n\x15ExampleActionResponse\x12\x17\n\x0fresponse_string\x18\x01 \x01(\t",\n\x14ExampleMonolithEvent\x12\x14\n\x0cevent_string\x18\x01 \x01(\tB8Z6github.com/ccpgames/eve-proto-go/generated/eve/exampleb\x06proto3')
_EXAMPLEACTIONREQUEST = _descriptor.Descriptor(name='ExampleActionRequest', full_name='eve.example.ExampleActionRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='request_string', full_name='eve.example.ExampleActionRequest.request_string', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=34, serialized_end=80)
_EXAMPLEACTIONRESPONSE = _descriptor.Descriptor(name='ExampleActionResponse', full_name='eve.example.ExampleActionResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='response_string', full_name='eve.example.ExampleActionResponse.response_string', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=82, serialized_end=130)
_EXAMPLEMONOLITHEVENT = _descriptor.Descriptor(name='ExampleMonolithEvent', full_name='eve.example.ExampleMonolithEvent', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='event_string', full_name='eve.example.ExampleMonolithEvent.event_string', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=176)
DESCRIPTOR.message_types_by_name['ExampleActionRequest'] = _EXAMPLEACTIONREQUEST
DESCRIPTOR.message_types_by_name['ExampleActionResponse'] = _EXAMPLEACTIONRESPONSE
DESCRIPTOR.message_types_by_name['ExampleMonolithEvent'] = _EXAMPLEMONOLITHEVENT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ExampleActionRequest = _reflection.GeneratedProtocolMessageType('ExampleActionRequest', (_message.Message,), {'DESCRIPTOR': _EXAMPLEACTIONREQUEST,
 '__module__': 'eve.example_pb2'})
_sym_db.RegisterMessage(ExampleActionRequest)
ExampleActionResponse = _reflection.GeneratedProtocolMessageType('ExampleActionResponse', (_message.Message,), {'DESCRIPTOR': _EXAMPLEACTIONRESPONSE,
 '__module__': 'eve.example_pb2'})
_sym_db.RegisterMessage(ExampleActionResponse)
ExampleMonolithEvent = _reflection.GeneratedProtocolMessageType('ExampleMonolithEvent', (_message.Message,), {'DESCRIPTOR': _EXAMPLEMONOLITHEVENT,
 '__module__': 'eve.example_pb2'})
_sym_db.RegisterMessage(ExampleMonolithEvent)
DESCRIPTOR._options = None
