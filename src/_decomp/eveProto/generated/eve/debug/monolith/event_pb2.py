#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\debug\monolith\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/debug/monolith/event.proto', package='eve.debug.monolith.event', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/debug/monolith/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/debug/monolith/event.proto\x12\x18eve.debug.monolith.event"\x1e\n\x0cEventEmitted\x12\x0e\n\x06tracer\x18\x01 \x01(\tBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/debug/monolith/eventb\x06proto3')
_EVENTEMITTED = _descriptor.Descriptor(name='EventEmitted', full_name='eve.debug.monolith.event.EventEmitted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='tracer', full_name='eve.debug.monolith.event.EventEmitted.tracer', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=60, serialized_end=90)
DESCRIPTOR.message_types_by_name['EventEmitted'] = _EVENTEMITTED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
EventEmitted = _reflection.GeneratedProtocolMessageType('EventEmitted', (_message.Message,), {'DESCRIPTOR': _EVENTEMITTED,
 '__module__': 'eve.debug.monolith.event_pb2'})
_sym_db.RegisterMessage(EventEmitted)
DESCRIPTOR._options = None
