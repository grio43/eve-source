#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\generic_ui\input\idle_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/generic_ui/input/idle.proto', package='eve_public.app.eveonline.generic_ui.input', syntax='proto3', serialized_options='ZTgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/generic_ui/input', create_key=_descriptor._internal_create_key, serialized_pb='\n4eve_public/app/eveonline/generic_ui/input/idle.proto\x12)eve_public.app.eveonline.generic_ui.input\x1a\x1egoogle/protobuf/duration.proto"D\n\x14IdleThresholdReached\x12,\n\tthreshold\x18\x01 \x01(\x0b2\x19.google.protobuf.Duration"\x11\n\x0fActivityResumedBVZTgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/generic_ui/inputb\x06proto3', dependencies=[google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_IDLETHRESHOLDREACHED = _descriptor.Descriptor(name='IdleThresholdReached', full_name='eve_public.app.eveonline.generic_ui.input.IdleThresholdReached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='threshold', full_name='eve_public.app.eveonline.generic_ui.input.IdleThresholdReached.threshold', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=131, serialized_end=199)
_ACTIVITYRESUMED = _descriptor.Descriptor(name='ActivityResumed', full_name='eve_public.app.eveonline.generic_ui.input.ActivityResumed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=201, serialized_end=218)
_IDLETHRESHOLDREACHED.fields_by_name['threshold'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
DESCRIPTOR.message_types_by_name['IdleThresholdReached'] = _IDLETHRESHOLDREACHED
DESCRIPTOR.message_types_by_name['ActivityResumed'] = _ACTIVITYRESUMED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
IdleThresholdReached = _reflection.GeneratedProtocolMessageType('IdleThresholdReached', (_message.Message,), {'DESCRIPTOR': _IDLETHRESHOLDREACHED,
 '__module__': 'eve_public.app.eveonline.generic_ui.input.idle_pb2'})
_sym_db.RegisterMessage(IdleThresholdReached)
ActivityResumed = _reflection.GeneratedProtocolMessageType('ActivityResumed', (_message.Message,), {'DESCRIPTOR': _ACTIVITYRESUMED,
 '__module__': 'eve_public.app.eveonline.generic_ui.input.idle_pb2'})
_sym_db.RegisterMessage(ActivityResumed)
DESCRIPTOR._options = None
