#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\goal\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.goal import goal_pb2 as eve__public_dot_goal_dot_goal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/goal/api/events.proto', package='eve_public.goal.api', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve_public/goal/api', create_key=_descriptor._internal_create_key, serialized_pb='\n eve_public/goal/api/events.proto\x12\x13eve_public.goal.api\x1a\x1aeve_public/goal/goal.proto":\n\x0fCloneFormOpened\x12\'\n\x02id\x18\x01 \x01(\x0b2\x1b.eve_public.goal.IdentifierB@Z>github.com/ccpgames/eve-proto-go/generated/eve_public/goal/apib\x06proto3', dependencies=[eve__public_dot_goal_dot_goal__pb2.DESCRIPTOR])
_CLONEFORMOPENED = _descriptor.Descriptor(name='CloneFormOpened', full_name='eve_public.goal.api.CloneFormOpened', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve_public.goal.api.CloneFormOpened.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=85, serialized_end=143)
_CLONEFORMOPENED.fields_by_name['id'].message_type = eve__public_dot_goal_dot_goal__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CloneFormOpened'] = _CLONEFORMOPENED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CloneFormOpened = _reflection.GeneratedProtocolMessageType('CloneFormOpened', (_message.Message,), {'DESCRIPTOR': _CLONEFORMOPENED,
 '__module__': 'eve_public.goal.api.events_pb2'})
_sym_db.RegisterMessage(CloneFormOpened)
DESCRIPTOR._options = None
