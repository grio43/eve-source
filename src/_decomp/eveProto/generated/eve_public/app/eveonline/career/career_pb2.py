#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\career\career_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.career import goal_pb2 as eve__public_dot_career_dot_goal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/career/career.proto', package='eve_public.app.eveonline.career', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/career', create_key=_descriptor._internal_create_key, serialized_pb='\n,eve_public/app/eveonline/career/career.proto\x12\x1feve_public.app.eveonline.career\x1a\x1ceve_public/career/goal.proto"<\n\x08Selected\x120\n\x04goal\x18\x01 \x01(\x0b2".eve_public.career.goal.IdentifierBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/careerb\x06proto3', dependencies=[eve__public_dot_career_dot_goal__pb2.DESCRIPTOR])
_SELECTED = _descriptor.Descriptor(name='Selected', full_name='eve_public.app.eveonline.career.Selected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve_public.app.eveonline.career.Selected.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=111, serialized_end=171)
_SELECTED.fields_by_name['goal'].message_type = eve__public_dot_career_dot_goal__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Selected'] = _SELECTED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Selected = _reflection.GeneratedProtocolMessageType('Selected', (_message.Message,), {'DESCRIPTOR': _SELECTED,
 '__module__': 'eve_public.app.eveonline.career.career_pb2'})
_sym_db.RegisterMessage(Selected)
DESCRIPTOR._options = None
