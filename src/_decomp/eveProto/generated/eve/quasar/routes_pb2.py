#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\quasar\routes_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/quasar/routes.proto', package='eve.quasar', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/quasar', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/quasar/routes.proto\x12\neve.quasar\x1a\x1deve/character/character.proto\x1a!eve/solarsystem/solarsystem.proto"I\n\x19CharacterRouteEstablished\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"~\n\x1bSolarSystemRouteEstablished\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB7Z5github.com/ccpgames/eve-proto-go/generated/eve/quasarb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_CHARACTERROUTEESTABLISHED = _descriptor.Descriptor(name='CharacterRouteEstablished', full_name='eve.quasar.CharacterRouteEstablished', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.quasar.CharacterRouteEstablished.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=105, serialized_end=178)
_SOLARSYSTEMROUTEESTABLISHED = _descriptor.Descriptor(name='SolarSystemRouteEstablished', full_name='eve.quasar.SolarSystemRouteEstablished', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.quasar.SolarSystemRouteEstablished.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.quasar.SolarSystemRouteEstablished.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=180, serialized_end=306)
_CHARACTERROUTEESTABLISHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SOLARSYSTEMROUTEESTABLISHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SOLARSYSTEMROUTEESTABLISHED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CharacterRouteEstablished'] = _CHARACTERROUTEESTABLISHED
DESCRIPTOR.message_types_by_name['SolarSystemRouteEstablished'] = _SOLARSYSTEMROUTEESTABLISHED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CharacterRouteEstablished = _reflection.GeneratedProtocolMessageType('CharacterRouteEstablished', (_message.Message,), {'DESCRIPTOR': _CHARACTERROUTEESTABLISHED,
 '__module__': 'eve.quasar.routes_pb2'})
_sym_db.RegisterMessage(CharacterRouteEstablished)
SolarSystemRouteEstablished = _reflection.GeneratedProtocolMessageType('SolarSystemRouteEstablished', (_message.Message,), {'DESCRIPTOR': _SOLARSYSTEMROUTEESTABLISHED,
 '__module__': 'eve.quasar.routes_pb2'})
_sym_db.RegisterMessage(SolarSystemRouteEstablished)
DESCRIPTOR._options = None
