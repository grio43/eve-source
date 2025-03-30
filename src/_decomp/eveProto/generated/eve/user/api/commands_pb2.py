#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\api\commands_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/api/commands.proto', package='eve.user.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/user/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/user/api/commands.proto\x12\x0ceve.user.api\x1a\x13eve/user/user.proto"d\n&EmailVerificationStatusChangeCommanded\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12\x16\n\x0eemail_verified\x18\x02 \x01(\x08B9Z7github.com/ccpgames/eve-proto-go/generated/eve/user/apib\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_EMAILVERIFICATIONSTATUSCHANGECOMMANDED = _descriptor.Descriptor(name='EmailVerificationStatusChangeCommanded', full_name='eve.user.api.EmailVerificationStatusChangeCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.api.EmailVerificationStatusChangeCommanded.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='email_verified', full_name='eve.user.api.EmailVerificationStatusChangeCommanded.email_verified', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=66, serialized_end=166)
_EMAILVERIFICATIONSTATUSCHANGECOMMANDED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['EmailVerificationStatusChangeCommanded'] = _EMAILVERIFICATIONSTATUSCHANGECOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
EmailVerificationStatusChangeCommanded = _reflection.GeneratedProtocolMessageType('EmailVerificationStatusChangeCommanded', (_message.Message,), {'DESCRIPTOR': _EMAILVERIFICATIONSTATUSCHANGECOMMANDED,
 '__module__': 'eve.user.api.commands_pb2'})
_sym_db.RegisterMessage(EmailVerificationStatusChangeCommanded)
DESCRIPTOR._options = None
