#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\dungeon\dungeon_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/dungeon/dungeon.proto', package='eve.dungeon', syntax='proto3', serialized_options='Z6github.com/ccpgames/eve-proto-go/generated/eve/dungeon', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/dungeon/dungeon.proto\x12\x0beve.dungeon\x1a\x1deve/character/character.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04";\n\x07Entered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01":\n\x06Exited\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01B8Z6github.com/ccpgames/eve-proto-go/generated/eve/dungeonb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.dungeon.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.dungeon.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=73, serialized_end=105)
_ENTERED = _descriptor.Descriptor(name='Entered', full_name='eve.dungeon.Entered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.dungeon.Entered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=107, serialized_end=166)
_EXITED = _descriptor.Descriptor(name='Exited', full_name='eve.dungeon.Exited', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.dungeon.Exited.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=168, serialized_end=226)
_ENTERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_EXITED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Entered'] = _ENTERED
DESCRIPTOR.message_types_by_name['Exited'] = _EXITED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.dungeon.dungeon_pb2'})
_sym_db.RegisterMessage(Identifier)
Entered = _reflection.GeneratedProtocolMessageType('Entered', (_message.Message,), {'DESCRIPTOR': _ENTERED,
 '__module__': 'eve.dungeon.dungeon_pb2'})
_sym_db.RegisterMessage(Entered)
Exited = _reflection.GeneratedProtocolMessageType('Exited', (_message.Message,), {'DESCRIPTOR': _EXITED,
 '__module__': 'eve.dungeon.dungeon_pb2'})
_sym_db.RegisterMessage(Exited)
DESCRIPTOR._options = None
_ENTERED._options = None
_EXITED._options = None
