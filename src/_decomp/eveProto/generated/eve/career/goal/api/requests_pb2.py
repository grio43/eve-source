#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\career\goal\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.career import goal_pb2 as eve_dot_career_dot_goal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/career/goal/api/requests.proto', package='eve.career.goal.api', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/career/goal/api', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/career/goal/api/requests.proto\x12\x13eve.career.goal.api\x1a\x15eve/career/goal.proto"\x17\n\x15GetDefinitionsRequest"\xbd\x01\n\x16GetDefinitionsResponse\x12?\n\x05goals\x18\x01 \x03(\x0b20.eve.career.goal.api.GetDefinitionsResponse.Goal\x1ab\n\x04Goal\x12)\n\x04goal\x18\x01 \x01(\x0b2\x1b.eve.career.goal.Identifier\x12/\n\nattributes\x18\x02 \x01(\x0b2\x1b.eve.career.goal.AttributesB@Z>github.com/ccpgames/eve-proto-go/generated/eve/career/goal/apib\x06proto3', dependencies=[eve_dot_career_dot_goal__pb2.DESCRIPTOR])
_GETDEFINITIONSREQUEST = _descriptor.Descriptor(name='GetDefinitionsRequest', full_name='eve.career.goal.api.GetDefinitionsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=82, serialized_end=105)
_GETDEFINITIONSRESPONSE_GOAL = _descriptor.Descriptor(name='Goal', full_name='eve.career.goal.api.GetDefinitionsResponse.Goal', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve.career.goal.api.GetDefinitionsResponse.Goal.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.career.goal.api.GetDefinitionsResponse.Goal.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=199, serialized_end=297)
_GETDEFINITIONSRESPONSE = _descriptor.Descriptor(name='GetDefinitionsResponse', full_name='eve.career.goal.api.GetDefinitionsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goals', full_name='eve.career.goal.api.GetDefinitionsResponse.goals', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETDEFINITIONSRESPONSE_GOAL], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=108, serialized_end=297)
_GETDEFINITIONSRESPONSE_GOAL.fields_by_name['goal'].message_type = eve_dot_career_dot_goal__pb2._IDENTIFIER
_GETDEFINITIONSRESPONSE_GOAL.fields_by_name['attributes'].message_type = eve_dot_career_dot_goal__pb2._ATTRIBUTES
_GETDEFINITIONSRESPONSE_GOAL.containing_type = _GETDEFINITIONSRESPONSE
_GETDEFINITIONSRESPONSE.fields_by_name['goals'].message_type = _GETDEFINITIONSRESPONSE_GOAL
DESCRIPTOR.message_types_by_name['GetDefinitionsRequest'] = _GETDEFINITIONSREQUEST
DESCRIPTOR.message_types_by_name['GetDefinitionsResponse'] = _GETDEFINITIONSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetDefinitionsRequest = _reflection.GeneratedProtocolMessageType('GetDefinitionsRequest', (_message.Message,), {'DESCRIPTOR': _GETDEFINITIONSREQUEST,
 '__module__': 'eve.career.goal.api.requests_pb2'})
_sym_db.RegisterMessage(GetDefinitionsRequest)
GetDefinitionsResponse = _reflection.GeneratedProtocolMessageType('GetDefinitionsResponse', (_message.Message,), {'Goal': _reflection.GeneratedProtocolMessageType('Goal', (_message.Message,), {'DESCRIPTOR': _GETDEFINITIONSRESPONSE_GOAL,
          '__module__': 'eve.career.goal.api.requests_pb2'}),
 'DESCRIPTOR': _GETDEFINITIONSRESPONSE,
 '__module__': 'eve.career.goal.api.requests_pb2'})
_sym_db.RegisterMessage(GetDefinitionsResponse)
_sym_db.RegisterMessage(GetDefinitionsResponse.Goal)
DESCRIPTOR._options = None
