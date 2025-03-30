#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\career\goal\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.career import goal_pb2 as eve__public_dot_career_dot_goal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/career/goal/api/admin/requests.proto', package='eve_public.career.goal.api.admin', syntax='proto3', serialized_options='ZKgithub.com/ccpgames/eve-proto-go/generated/eve_public/career/goal/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n/eve_public/career/goal/api/admin/requests.proto\x12 eve_public.career.goal.api.admin\x1a\x1ceve_public/career/goal.proto"C\n\x0fCompleteRequest\x120\n\x04goal\x18\x01 \x01(\x0b2".eve_public.career.goal.Identifier"\x12\n\x10CompleteResponse"U\n\x0fProgressRequest\x120\n\x04goal\x18\x01 \x01(\x0b2".eve_public.career.goal.Identifier\x12\x10\n\x08progress\x18\x02 \x01(\r"\x12\n\x10ProgressResponseBMZKgithub.com/ccpgames/eve-proto-go/generated/eve_public/career/goal/api/adminb\x06proto3', dependencies=[eve__public_dot_career_dot_goal__pb2.DESCRIPTOR])
_COMPLETEREQUEST = _descriptor.Descriptor(name='CompleteRequest', full_name='eve_public.career.goal.api.admin.CompleteRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve_public.career.goal.api.admin.CompleteRequest.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=115, serialized_end=182)
_COMPLETERESPONSE = _descriptor.Descriptor(name='CompleteResponse', full_name='eve_public.career.goal.api.admin.CompleteResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=184, serialized_end=202)
_PROGRESSREQUEST = _descriptor.Descriptor(name='ProgressRequest', full_name='eve_public.career.goal.api.admin.ProgressRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve_public.career.goal.api.admin.ProgressRequest.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='progress', full_name='eve_public.career.goal.api.admin.ProgressRequest.progress', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=204, serialized_end=289)
_PROGRESSRESPONSE = _descriptor.Descriptor(name='ProgressResponse', full_name='eve_public.career.goal.api.admin.ProgressResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=291, serialized_end=309)
_COMPLETEREQUEST.fields_by_name['goal'].message_type = eve__public_dot_career_dot_goal__pb2._IDENTIFIER
_PROGRESSREQUEST.fields_by_name['goal'].message_type = eve__public_dot_career_dot_goal__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CompleteRequest'] = _COMPLETEREQUEST
DESCRIPTOR.message_types_by_name['CompleteResponse'] = _COMPLETERESPONSE
DESCRIPTOR.message_types_by_name['ProgressRequest'] = _PROGRESSREQUEST
DESCRIPTOR.message_types_by_name['ProgressResponse'] = _PROGRESSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CompleteRequest = _reflection.GeneratedProtocolMessageType('CompleteRequest', (_message.Message,), {'DESCRIPTOR': _COMPLETEREQUEST,
 '__module__': 'eve_public.career.goal.api.admin.requests_pb2'})
_sym_db.RegisterMessage(CompleteRequest)
CompleteResponse = _reflection.GeneratedProtocolMessageType('CompleteResponse', (_message.Message,), {'DESCRIPTOR': _COMPLETERESPONSE,
 '__module__': 'eve_public.career.goal.api.admin.requests_pb2'})
_sym_db.RegisterMessage(CompleteResponse)
ProgressRequest = _reflection.GeneratedProtocolMessageType('ProgressRequest', (_message.Message,), {'DESCRIPTOR': _PROGRESSREQUEST,
 '__module__': 'eve_public.career.goal.api.admin.requests_pb2'})
_sym_db.RegisterMessage(ProgressRequest)
ProgressResponse = _reflection.GeneratedProtocolMessageType('ProgressResponse', (_message.Message,), {'DESCRIPTOR': _PROGRESSRESPONSE,
 '__module__': 'eve_public.career.goal.api.admin.requests_pb2'})
_sym_db.RegisterMessage(ProgressResponse)
DESCRIPTOR._options = None
