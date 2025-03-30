#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mission\storyline\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mission/storyline/event.proto', package='eve.mission.storyline.event', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve/mission/storyline/event', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/mission/storyline/event.proto\x12\x1beve.mission.storyline.event\x1a\x1deve/character/character.proto"Q\n\x12CharacterCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12\r\n\x05level\x18\x03 \x01(\rBHZFgithub.com/ccpgames/eve-proto-go/generated/eve/mission/storyline/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_CHARACTERCOMPLETED = _descriptor.Descriptor(name='CharacterCompleted', full_name='eve.mission.storyline.event.CharacterCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.mission.storyline.event.CharacterCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='level', full_name='eve.mission.storyline.event.CharacterCompleted.level', index=1, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=97, serialized_end=178)
_CHARACTERCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CharacterCompleted'] = _CHARACTERCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CharacterCompleted = _reflection.GeneratedProtocolMessageType('CharacterCompleted', (_message.Message,), {'DESCRIPTOR': _CHARACTERCOMPLETED,
 '__module__': 'eve.mission.storyline.event_pb2'})
_sym_db.RegisterMessage(CharacterCompleted)
DESCRIPTOR._options = None
