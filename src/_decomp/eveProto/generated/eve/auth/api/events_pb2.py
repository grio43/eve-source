#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\auth\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/auth/api/events.proto', package='eve.auth.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/auth/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/auth/api/events.proto\x12\x0ceve.auth.api\x1a\x13eve/user/user.proto"6\n\x10TwoFactorEnabled\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"7\n\x11TwoFactorDisabled\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/auth/apib\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_TWOFACTORENABLED = _descriptor.Descriptor(name='TwoFactorEnabled', full_name='eve.auth.api.TwoFactorEnabled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.auth.api.TwoFactorEnabled.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=64, serialized_end=118)
_TWOFACTORDISABLED = _descriptor.Descriptor(name='TwoFactorDisabled', full_name='eve.auth.api.TwoFactorDisabled', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.auth.api.TwoFactorDisabled.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=175)
_TWOFACTORENABLED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_TWOFACTORDISABLED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['TwoFactorEnabled'] = _TWOFACTORENABLED
DESCRIPTOR.message_types_by_name['TwoFactorDisabled'] = _TWOFACTORDISABLED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
TwoFactorEnabled = _reflection.GeneratedProtocolMessageType('TwoFactorEnabled', (_message.Message,), {'DESCRIPTOR': _TWOFACTORENABLED,
 '__module__': 'eve.auth.api.events_pb2'})
_sym_db.RegisterMessage(TwoFactorEnabled)
TwoFactorDisabled = _reflection.GeneratedProtocolMessageType('TwoFactorDisabled', (_message.Message,), {'DESCRIPTOR': _TWOFACTORDISABLED,
 '__module__': 'eve.auth.api.events_pb2'})
_sym_db.RegisterMessage(TwoFactorDisabled)
DESCRIPTOR._options = None
