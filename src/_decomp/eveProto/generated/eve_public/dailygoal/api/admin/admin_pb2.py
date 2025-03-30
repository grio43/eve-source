#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\dailygoal\api\admin\admin_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.character import character_pb2 as eve__public_dot_character_dot_character__pb2
from eveProto.generated.eve_public.dailygoal import goal_pb2 as eve__public_dot_dailygoal_dot_goal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/dailygoal/api/admin/admin.proto', package='eve_public.dailygoal.api.admin', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve_public/dailygoal/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve_public/dailygoal/api/admin/admin.proto\x12\x1eeve_public.dailygoal.api.admin\x1a$eve_public/character/character.proto\x1a\x1feve_public/dailygoal/goal.proto"\x88\x01\n\x0fProgressRequest\x12.\n\x04goal\x18\x01 \x01(\x0b2 .eve_public.dailygoal.Identifier\x123\n\tcharacter\x18\x02 \x01(\x0b2 .eve_public.character.Identifier\x12\x10\n\x08progress\x18\x03 \x01(\x04"\x12\n\x10ProgressResponseBKZIgithub.com/ccpgames/eve-proto-go/generated/eve_public/dailygoal/api/adminb\x06proto3', dependencies=[eve__public_dot_character_dot_character__pb2.DESCRIPTOR, eve__public_dot_dailygoal_dot_goal__pb2.DESCRIPTOR])
_PROGRESSREQUEST = _descriptor.Descriptor(name='ProgressRequest', full_name='eve_public.dailygoal.api.admin.ProgressRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve_public.dailygoal.api.admin.ProgressRequest.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve_public.dailygoal.api.admin.ProgressRequest.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='progress', full_name='eve_public.dailygoal.api.admin.ProgressRequest.progress', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=286)
_PROGRESSRESPONSE = _descriptor.Descriptor(name='ProgressResponse', full_name='eve_public.dailygoal.api.admin.ProgressResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=288, serialized_end=306)
_PROGRESSREQUEST.fields_by_name['goal'].message_type = eve__public_dot_dailygoal_dot_goal__pb2._IDENTIFIER
_PROGRESSREQUEST.fields_by_name['character'].message_type = eve__public_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ProgressRequest'] = _PROGRESSREQUEST
DESCRIPTOR.message_types_by_name['ProgressResponse'] = _PROGRESSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ProgressRequest = _reflection.GeneratedProtocolMessageType('ProgressRequest', (_message.Message,), {'DESCRIPTOR': _PROGRESSREQUEST,
 '__module__': 'eve_public.dailygoal.api.admin.admin_pb2'})
_sym_db.RegisterMessage(ProgressRequest)
ProgressResponse = _reflection.GeneratedProtocolMessageType('ProgressResponse', (_message.Message,), {'DESCRIPTOR': _PROGRESSRESPONSE,
 '__module__': 'eve_public.dailygoal.api.admin.admin_pb2'})
_sym_db.RegisterMessage(ProgressResponse)
DESCRIPTOR._options = None
