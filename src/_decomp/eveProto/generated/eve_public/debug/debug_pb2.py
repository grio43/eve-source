#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\debug\debug_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/debug/debug.proto', package='eve_public.debug', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve_public/debug', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve_public/debug/debug.proto\x12\x10eve_public.debug"\x16\n\x06Notice\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\x15\n\x05Event\x12\x0c\n\x04data\x18\x01 \x01(\x0c"\x17\n\x07Request\x12\x0c\n\x04data\x18\x01 \x01(\x0c"\x18\n\x08Response\x12\x0c\n\x04data\x18\x01 \x01(\x0cB=Z;github.com/ccpgames/eve-proto-go/generated/eve_public/debugb\x06proto3')
_NOTICE = _descriptor.Descriptor(name='Notice', full_name='eve_public.debug.Notice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve_public.debug.Notice.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=50, serialized_end=72)
_EVENT = _descriptor.Descriptor(name='Event', full_name='eve_public.debug.Event', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='data', full_name='eve_public.debug.Event.data', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=74, serialized_end=95)
_REQUEST = _descriptor.Descriptor(name='Request', full_name='eve_public.debug.Request', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='data', full_name='eve_public.debug.Request.data', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=97, serialized_end=120)
_RESPONSE = _descriptor.Descriptor(name='Response', full_name='eve_public.debug.Response', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='data', full_name='eve_public.debug.Response.data', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=146)
DESCRIPTOR.message_types_by_name['Notice'] = _NOTICE
DESCRIPTOR.message_types_by_name['Event'] = _EVENT
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Notice = _reflection.GeneratedProtocolMessageType('Notice', (_message.Message,), {'DESCRIPTOR': _NOTICE,
 '__module__': 'eve_public.debug.debug_pb2'})
_sym_db.RegisterMessage(Notice)
Event = _reflection.GeneratedProtocolMessageType('Event', (_message.Message,), {'DESCRIPTOR': _EVENT,
 '__module__': 'eve_public.debug.debug_pb2'})
_sym_db.RegisterMessage(Event)
Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {'DESCRIPTOR': _REQUEST,
 '__module__': 'eve_public.debug.debug_pb2'})
_sym_db.RegisterMessage(Request)
Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {'DESCRIPTOR': _RESPONSE,
 '__module__': 'eve_public.debug.debug_pb2'})
_sym_db.RegisterMessage(Response)
DESCRIPTOR._options = None
