#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\license\api\commands_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user.license import license_pb2 as eve_dot_user_dot_license_dot_license__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/license/api/commands.proto', package='eve.user.license.api', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/user/license/api', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/user/license/api/commands.proto\x12\x14eve.user.license.api\x1a\x1eeve/user/license/license.proto"@\n\x0fVerifyCommanded\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.IdentifierBAZ?github.com/ccpgames/eve-proto-go/generated/eve/user/license/apib\x06proto3', dependencies=[eve_dot_user_dot_license_dot_license__pb2.DESCRIPTOR])
_VERIFYCOMMANDED = _descriptor.Descriptor(name='VerifyCommanded', full_name='eve.user.license.api.VerifyCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.VerifyCommanded.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=157)
_VERIFYCOMMANDED.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['VerifyCommanded'] = _VERIFYCOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
VerifyCommanded = _reflection.GeneratedProtocolMessageType('VerifyCommanded', (_message.Message,), {'DESCRIPTOR': _VERIFYCOMMANDED,
 '__module__': 'eve.user.license.api.commands_pb2'})
_sym_db.RegisterMessage(VerifyCommanded)
DESCRIPTOR._options = None
