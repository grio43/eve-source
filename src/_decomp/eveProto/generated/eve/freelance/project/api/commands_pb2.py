#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\freelance\project\api\commands_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.freelance.project import project_pb2 as eve_dot_freelance_dot_project_dot_project__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/freelance/project/api/commands.proto', package='eve.freelance.project.api', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/freelance/project/api', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/freelance/project/api/commands.proto\x12\x19eve.freelance.project.api\x1a#eve/freelance/project/project.proto"E\n\x0fExpireCommanded\x122\n\x07project\x18\x01 \x01(\x0b2!.eve.freelance.project.Identifier"G\n\x11CompleteCommanded\x122\n\x07project\x18\x01 \x01(\x0b2!.eve.freelance.project.Identifier"\x1c\n\x1aAutoRedeemRewardsCommandedBFZDgithub.com/ccpgames/eve-proto-go/generated/eve/freelance/project/apib\x06proto3', dependencies=[eve_dot_freelance_dot_project_dot_project__pb2.DESCRIPTOR])
_EXPIRECOMMANDED = _descriptor.Descriptor(name='ExpireCommanded', full_name='eve.freelance.project.api.ExpireCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='project', full_name='eve.freelance.project.api.ExpireCommanded.project', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=108, serialized_end=177)
_COMPLETECOMMANDED = _descriptor.Descriptor(name='CompleteCommanded', full_name='eve.freelance.project.api.CompleteCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='project', full_name='eve.freelance.project.api.CompleteCommanded.project', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=179, serialized_end=250)
_AUTOREDEEMREWARDSCOMMANDED = _descriptor.Descriptor(name='AutoRedeemRewardsCommanded', full_name='eve.freelance.project.api.AutoRedeemRewardsCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=252, serialized_end=280)
_EXPIRECOMMANDED.fields_by_name['project'].message_type = eve_dot_freelance_dot_project_dot_project__pb2._IDENTIFIER
_COMPLETECOMMANDED.fields_by_name['project'].message_type = eve_dot_freelance_dot_project_dot_project__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ExpireCommanded'] = _EXPIRECOMMANDED
DESCRIPTOR.message_types_by_name['CompleteCommanded'] = _COMPLETECOMMANDED
DESCRIPTOR.message_types_by_name['AutoRedeemRewardsCommanded'] = _AUTOREDEEMREWARDSCOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ExpireCommanded = _reflection.GeneratedProtocolMessageType('ExpireCommanded', (_message.Message,), {'DESCRIPTOR': _EXPIRECOMMANDED,
 '__module__': 'eve.freelance.project.api.commands_pb2'})
_sym_db.RegisterMessage(ExpireCommanded)
CompleteCommanded = _reflection.GeneratedProtocolMessageType('CompleteCommanded', (_message.Message,), {'DESCRIPTOR': _COMPLETECOMMANDED,
 '__module__': 'eve.freelance.project.api.commands_pb2'})
_sym_db.RegisterMessage(CompleteCommanded)
AutoRedeemRewardsCommanded = _reflection.GeneratedProtocolMessageType('AutoRedeemRewardsCommanded', (_message.Message,), {'DESCRIPTOR': _AUTOREDEEMREWARDSCOMMANDED,
 '__module__': 'eve.freelance.project.api.commands_pb2'})
_sym_db.RegisterMessage(AutoRedeemRewardsCommanded)
DESCRIPTOR._options = None
