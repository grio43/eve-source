#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\deadspace\gassite_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.dungeon import dungeon_pb2 as eve_dot_dungeon_dot_dungeon__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/deadspace/gassite.proto', package='eve.character.deadspace.gassite', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/character/deadspace/gassite', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/character/deadspace/gassite.proto\x12\x1feve.character.deadspace.gassite\x1a\x1deve/character/character.proto\x1a\x19eve/dungeon/dungeon.proto"a\n\x07Entered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12(\n\x07dungeon\x18\x02 \x01(\x0b2\x17.eve.dungeon.IdentifierBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/character/deadspace/gassiteb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_dungeon_dot_dungeon__pb2.DESCRIPTOR])
_ENTERED = _descriptor.Descriptor(name='Entered', full_name='eve.character.deadspace.gassite.Entered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.deadspace.gassite.Entered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='dungeon', full_name='eve.character.deadspace.gassite.Entered.dungeon', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=229)
_ENTERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ENTERED.fields_by_name['dungeon'].message_type = eve_dot_dungeon_dot_dungeon__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Entered'] = _ENTERED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Entered = _reflection.GeneratedProtocolMessageType('Entered', (_message.Message,), {'DESCRIPTOR': _ENTERED,
 '__module__': 'eve.character.deadspace.gassite_pb2'})
_sym_db.RegisterMessage(Entered)
DESCRIPTOR._options = None
