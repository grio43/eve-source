#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\device\user\user_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.user import user_pb2 as eve__public_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/device/user/user.proto', package='eve_public.device.user', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/device/user', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve_public/device/user/user.proto\x12\x16eve_public.device.user\x1a\x1aeve_public/user/user.proto"G\n\nIdentifier\x12\x0e\n\x06device\x18\x01 \x01(\x0c\x12)\n\x04user\x18\x02 \x01(\x0b2\x1b.eve_public.user.IdentifierBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/device/userb\x06proto3', dependencies=[eve__public_dot_user_dot_user__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.device.user.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='device', full_name='eve_public.device.user.Identifier.device', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='user', full_name='eve_public.device.user.Identifier.user', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=89, serialized_end=160)
_IDENTIFIER.fields_by_name['user'].message_type = eve__public_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.device.user.user_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
