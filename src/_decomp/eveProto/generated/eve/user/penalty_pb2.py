#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\penalty_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/penalty.proto', package='eve.user.penalty', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/user/penalty', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/user/penalty.proto\x12\x10eve.user.penalty\x1a\x13eve/user/user.proto"A\n\x1bCheckIsUserPenalizedRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"8\n\x1cCheckIsUserPenalizedResponse\x12\x18\n\x10is_under_penalty\x18\x01 \x01(\x08B=Z;github.com/ccpgames/eve-proto-go/generated/eve/user/penaltyb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_CHECKISUSERPENALIZEDREQUEST = _descriptor.Descriptor(name='CheckIsUserPenalizedRequest', full_name='eve.user.penalty.CheckIsUserPenalizedRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.penalty.CheckIsUserPenalizedRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=65, serialized_end=130)
_CHECKISUSERPENALIZEDRESPONSE = _descriptor.Descriptor(name='CheckIsUserPenalizedResponse', full_name='eve.user.penalty.CheckIsUserPenalizedResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='is_under_penalty', full_name='eve.user.penalty.CheckIsUserPenalizedResponse.is_under_penalty', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=188)
_CHECKISUSERPENALIZEDREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CheckIsUserPenalizedRequest'] = _CHECKISUSERPENALIZEDREQUEST
DESCRIPTOR.message_types_by_name['CheckIsUserPenalizedResponse'] = _CHECKISUSERPENALIZEDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CheckIsUserPenalizedRequest = _reflection.GeneratedProtocolMessageType('CheckIsUserPenalizedRequest', (_message.Message,), {'DESCRIPTOR': _CHECKISUSERPENALIZEDREQUEST,
 '__module__': 'eve.user.penalty_pb2'})
_sym_db.RegisterMessage(CheckIsUserPenalizedRequest)
CheckIsUserPenalizedResponse = _reflection.GeneratedProtocolMessageType('CheckIsUserPenalizedResponse', (_message.Message,), {'DESCRIPTOR': _CHECKISUSERPENALIZEDRESPONSE,
 '__module__': 'eve.user.penalty_pb2'})
_sym_db.RegisterMessage(CheckIsUserPenalizedResponse)
DESCRIPTOR._options = None
