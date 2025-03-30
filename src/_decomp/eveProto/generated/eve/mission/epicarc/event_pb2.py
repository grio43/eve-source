#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mission\epicarc\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mission/epicarc/event.proto', package='eve.mission.epicarc.event', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/mission/epicarc/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/mission/epicarc/event.proto\x12\x19eve.mission.epicarc.event\x1a\x1deve/character/character.proto\x1a\x19eve/faction/faction.proto"l\n\x12CharacterCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12(\n\x07faction\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier"f\n\x0cArcCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12(\n\x07faction\x18\x02 \x01(\x0b2\x17.eve.faction.IdentifierBFZDgithub.com/ccpgames/eve-proto-go/generated/eve/mission/epicarc/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_faction_dot_faction__pb2.DESCRIPTOR])
_CHARACTERCOMPLETED = _descriptor.Descriptor(name='CharacterCompleted', full_name='eve.mission.epicarc.event.CharacterCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.mission.epicarc.event.CharacterCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='faction', full_name='eve.mission.epicarc.event.CharacterCompleted.faction', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=228)
_ARCCOMPLETED = _descriptor.Descriptor(name='ArcCompleted', full_name='eve.mission.epicarc.event.ArcCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.mission.epicarc.event.ArcCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='faction', full_name='eve.mission.epicarc.event.ArcCompleted.faction', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=230, serialized_end=332)
_CHARACTERCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CHARACTERCOMPLETED.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_ARCCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ARCCOMPLETED.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CharacterCompleted'] = _CHARACTERCOMPLETED
DESCRIPTOR.message_types_by_name['ArcCompleted'] = _ARCCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CharacterCompleted = _reflection.GeneratedProtocolMessageType('CharacterCompleted', (_message.Message,), {'DESCRIPTOR': _CHARACTERCOMPLETED,
 '__module__': 'eve.mission.epicarc.event_pb2'})
_sym_db.RegisterMessage(CharacterCompleted)
ArcCompleted = _reflection.GeneratedProtocolMessageType('ArcCompleted', (_message.Message,), {'DESCRIPTOR': _ARCCOMPLETED,
 '__module__': 'eve.mission.epicarc.event_pb2'})
_sym_db.RegisterMessage(ArcCompleted)
DESCRIPTOR._options = None
