#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\csat\survey_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/csat/survey.proto', package='eve.csat', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/csat', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/csat/survey.proto\x12\x08eve.csat\x1a\x13eve/user/user.proto"-\n\x06Survey\x12\x11\n\tthumbs_up\x18\x01 \x01(\x08\x12\x10\n\x08feedback\x18\x02 \x01(\t"W\n\x0fSurveyCompleted\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12 \n\x06survey\x18\x02 \x01(\x0b2\x10.eve.csat.SurveyB5Z3github.com/ccpgames/eve-proto-go/generated/eve/csatb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_SURVEY = _descriptor.Descriptor(name='Survey', full_name='eve.csat.Survey', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='thumbs_up', full_name='eve.csat.Survey.thumbs_up', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='feedback', full_name='eve.csat.Survey.feedback', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=56, serialized_end=101)
_SURVEYCOMPLETED = _descriptor.Descriptor(name='SurveyCompleted', full_name='eve.csat.SurveyCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.csat.SurveyCompleted.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='survey', full_name='eve.csat.SurveyCompleted.survey', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=103, serialized_end=190)
_SURVEYCOMPLETED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_SURVEYCOMPLETED.fields_by_name['survey'].message_type = _SURVEY
DESCRIPTOR.message_types_by_name['Survey'] = _SURVEY
DESCRIPTOR.message_types_by_name['SurveyCompleted'] = _SURVEYCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Survey = _reflection.GeneratedProtocolMessageType('Survey', (_message.Message,), {'DESCRIPTOR': _SURVEY,
 '__module__': 'eve.csat.survey_pb2'})
_sym_db.RegisterMessage(Survey)
SurveyCompleted = _reflection.GeneratedProtocolMessageType('SurveyCompleted', (_message.Message,), {'DESCRIPTOR': _SURVEYCOMPLETED,
 '__module__': 'eve.csat.survey_pb2'})
_sym_db.RegisterMessage(SurveyCompleted)
DESCRIPTOR._options = None
