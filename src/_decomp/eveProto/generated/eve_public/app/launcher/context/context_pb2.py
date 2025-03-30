#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\launcher\context\context_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/launcher/context/context.proto', package='eve_public.app.launcher.context', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/launcher/context', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve_public/app/launcher/context/context.proto\x12\x1feve_public.app.launcher.context"5\n\rEventMetadata\x12\x14\n\x0cmachine_uuid\x18\x01 \x01(\x0c\x12\x0e\n\x06device\x18\x02 \x01(\x0cBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/launcher/contextb\x06proto3')
_EVENTMETADATA = _descriptor.Descriptor(name='EventMetadata', full_name='eve_public.app.launcher.context.EventMetadata', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='machine_uuid', full_name='eve_public.app.launcher.context.EventMetadata.machine_uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='device', full_name='eve_public.app.launcher.context.EventMetadata.device', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=82, serialized_end=135)
DESCRIPTOR.message_types_by_name['EventMetadata'] = _EVENTMETADATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
EventMetadata = _reflection.GeneratedProtocolMessageType('EventMetadata', (_message.Message,), {'DESCRIPTOR': _EVENTMETADATA,
 '__module__': 'eve_public.app.launcher.context.context_pb2'})
_sym_db.RegisterMessage(EventMetadata)
DESCRIPTOR._options = None
