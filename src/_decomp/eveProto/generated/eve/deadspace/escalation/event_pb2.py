#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\deadspace\escalation\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.deadspace import archetype_pb2 as eve_dot_deadspace_dot_archetype__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/deadspace/escalation/event.proto', package='eve.deadspace.escalation.event', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve/deadspace/escalation/event', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/deadspace/escalation/event.proto\x12\x1eeve.deadspace.escalation.event\x1a\x1deve/character/character.proto\x1a\x1deve/deadspace/archetype.proto"z\n\x12CharacterCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x126\n\tarchetype\x18\x02 \x01(\x0b2#.eve.deadspace.archetype.IdentifierBKZIgithub.com/ccpgames/eve-proto-go/generated/eve/deadspace/escalation/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_deadspace_dot_archetype__pb2.DESCRIPTOR])
_CHARACTERCOMPLETED = _descriptor.Descriptor(name='CharacterCompleted', full_name='eve.deadspace.escalation.event.CharacterCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.deadspace.escalation.event.CharacterCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='archetype', full_name='eve.deadspace.escalation.event.CharacterCompleted.archetype', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=134, serialized_end=256)
_CHARACTERCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CHARACTERCOMPLETED.fields_by_name['archetype'].message_type = eve_dot_deadspace_dot_archetype__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CharacterCompleted'] = _CHARACTERCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CharacterCompleted = _reflection.GeneratedProtocolMessageType('CharacterCompleted', (_message.Message,), {'DESCRIPTOR': _CHARACTERCOMPLETED,
 '__module__': 'eve.deadspace.escalation.event_pb2'})
_sym_db.RegisterMessage(CharacterCompleted)
DESCRIPTOR._options = None
