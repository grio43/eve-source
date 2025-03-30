#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\stargate\lock\api\commands_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.stargate.lock import lock_pb2 as eve_dot_stargate_dot_lock_dot_lock__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/stargate/lock/api/commands.proto', package='eve.stargate.lock.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/stargate/lock/api', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/stargate/lock/api/commands.proto\x12\x15eve.stargate.lock.api\x1a\x1deve/character/character.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1ceve/stargate/lock/lock.proto"\x9e\x01\n\x0fDeleteCommanded\x12+\n\x04lock\x18\x01 \x01(\x0b2\x1d.eve.stargate.lock.Identifier\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x120\n\x0bsolarsystem\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.IdentifierBBZ@github.com/ccpgames/eve-proto-go/generated/eve/stargate/lock/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR, eve_dot_stargate_dot_lock_dot_lock__pb2.DESCRIPTOR])
_DELETECOMMANDED = _descriptor.Descriptor(name='DeleteCommanded', full_name='eve.stargate.lock.api.DeleteCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='lock', full_name='eve.stargate.lock.api.DeleteCommanded.lock', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.stargate.lock.api.DeleteCommanded.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solarsystem', full_name='eve.stargate.lock.api.DeleteCommanded.solarsystem', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=160, serialized_end=318)
_DELETECOMMANDED.fields_by_name['lock'].message_type = eve_dot_stargate_dot_lock_dot_lock__pb2._IDENTIFIER
_DELETECOMMANDED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_DELETECOMMANDED.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['DeleteCommanded'] = _DELETECOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DeleteCommanded = _reflection.GeneratedProtocolMessageType('DeleteCommanded', (_message.Message,), {'DESCRIPTOR': _DELETECOMMANDED,
 '__module__': 'eve.stargate.lock.api.commands_pb2'})
_sym_db.RegisterMessage(DeleteCommanded)
DESCRIPTOR._options = None
