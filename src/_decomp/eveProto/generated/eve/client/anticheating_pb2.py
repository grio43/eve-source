#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\client\anticheating_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/client/anticheating.proto', package='eve.client.anticheating', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/client/anticheating', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/client/anticheating.proto\x12\x17eve.client.anticheating\x1a\x13eve/user/user.proto"9\n\x13AntiCheatingStarted\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"9\n\x13AntiCheatingStopped\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.IdentifierBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/client/anticheatingb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_ANTICHEATINGSTARTED = _descriptor.Descriptor(name='AntiCheatingStarted', full_name='eve.client.anticheating.AntiCheatingStarted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.client.anticheating.AntiCheatingStarted.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=79, serialized_end=136)
_ANTICHEATINGSTOPPED = _descriptor.Descriptor(name='AntiCheatingStopped', full_name='eve.client.anticheating.AntiCheatingStopped', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.client.anticheating.AntiCheatingStopped.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=138, serialized_end=195)
_ANTICHEATINGSTARTED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ANTICHEATINGSTOPPED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['AntiCheatingStarted'] = _ANTICHEATINGSTARTED
DESCRIPTOR.message_types_by_name['AntiCheatingStopped'] = _ANTICHEATINGSTOPPED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
AntiCheatingStarted = _reflection.GeneratedProtocolMessageType('AntiCheatingStarted', (_message.Message,), {'DESCRIPTOR': _ANTICHEATINGSTARTED,
 '__module__': 'eve.client.anticheating_pb2'})
_sym_db.RegisterMessage(AntiCheatingStarted)
AntiCheatingStopped = _reflection.GeneratedProtocolMessageType('AntiCheatingStopped', (_message.Message,), {'DESCRIPTOR': _ANTICHEATINGSTOPPED,
 '__module__': 'eve.client.anticheating_pb2'})
_sym_db.RegisterMessage(AntiCheatingStopped)
DESCRIPTOR._options = None
