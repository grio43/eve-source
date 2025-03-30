#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\effect\combat\pve_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.ship import combat_pb2 as eve_dot_ship_dot_combat__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/effect/combat/pve.proto', package='eve.effect.combat.pve', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/effect/combat/pve', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/effect/combat/pve.proto\x12\x15eve.effect.combat.pve\x1a\x1deve/character/character.proto\x1a\x19eve/faction/faction.proto\x1a\x15eve/ship/combat.proto\x1a\x13eve/ship/ship.proto\x1a\x18eve/ship/ship_type.proto\x1a!eve/solarsystem/solarsystem.proto"\x9c\x02\n\x0fNPCShipExploded\x12+\n\x08exploder\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x124\n\x12exploded_ship_type\x18\x02 \x01(\x0b2\x18.eve.shiptype.Identifier\x126\n\x15exploded_ship_faction\x18\x03 \x01(\x0b2\x17.eve.faction.Identifier\x124\n\x0fsolar_system_id\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x124\n\x12exploder_ship_type\x18\x05 \x01(\x0b2\x18.eve.shiptype.Identifier:\x02\x18\x01"\xca\x02\n\x12PlayerShipExploded\x12/\n\x08exploded\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierB\x02\x18\x01\x128\n\x12exploded_ship_type\x18\x02 \x01(\x0b2\x18.eve.shiptype.IdentifierB\x02\x18\x01\x127\n\x16exploders_ship_faction\x18\x03 \x01(\x0b2\x17.eve.faction.Identifier\x125\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB\x02\x18\x01\x12/\n\rexploded_ship\x18\x05 \x01(\x0b2\x14.eve.ship.IdentifierB\x02\x18\x01\x12(\n\x06combat\x18\x06 \x01(\x0b2\x18.eve.ship.combat.ContextBBZ@github.com/ccpgames/eve-proto-go/generated/eve/effect/combat/pveb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_ship_dot_combat__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_NPCSHIPEXPLODED = _descriptor.Descriptor(name='NPCShipExploded', full_name='eve.effect.combat.pve.NPCShipExploded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='exploder', full_name='eve.effect.combat.pve.NPCShipExploded.exploder', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploded_ship_type', full_name='eve.effect.combat.pve.NPCShipExploded.exploded_ship_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploded_ship_faction', full_name='eve.effect.combat.pve.NPCShipExploded.exploded_ship_faction', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system_id', full_name='eve.effect.combat.pve.NPCShipExploded.solar_system_id', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploder_ship_type', full_name='eve.effect.combat.pve.NPCShipExploded.exploder_ship_type', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=218, serialized_end=502)
_PLAYERSHIPEXPLODED = _descriptor.Descriptor(name='PlayerShipExploded', full_name='eve.effect.combat.pve.PlayerShipExploded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='exploded', full_name='eve.effect.combat.pve.PlayerShipExploded.exploded', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploded_ship_type', full_name='eve.effect.combat.pve.PlayerShipExploded.exploded_ship_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploders_ship_faction', full_name='eve.effect.combat.pve.PlayerShipExploded.exploders_ship_faction', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.effect.combat.pve.PlayerShipExploded.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exploded_ship', full_name='eve.effect.combat.pve.PlayerShipExploded.exploded_ship', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='combat', full_name='eve.effect.combat.pve.PlayerShipExploded.combat', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=505, serialized_end=835)
_NPCSHIPEXPLODED.fields_by_name['exploder'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_NPCSHIPEXPLODED.fields_by_name['exploded_ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_NPCSHIPEXPLODED.fields_by_name['exploded_ship_faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_NPCSHIPEXPLODED.fields_by_name['solar_system_id'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_NPCSHIPEXPLODED.fields_by_name['exploder_ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['exploded'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['exploded_ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['exploders_ship_faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['exploded_ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_PLAYERSHIPEXPLODED.fields_by_name['combat'].message_type = eve_dot_ship_dot_combat__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['NPCShipExploded'] = _NPCSHIPEXPLODED
DESCRIPTOR.message_types_by_name['PlayerShipExploded'] = _PLAYERSHIPEXPLODED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
NPCShipExploded = _reflection.GeneratedProtocolMessageType('NPCShipExploded', (_message.Message,), {'DESCRIPTOR': _NPCSHIPEXPLODED,
 '__module__': 'eve.effect.combat.pve_pb2'})
_sym_db.RegisterMessage(NPCShipExploded)
PlayerShipExploded = _reflection.GeneratedProtocolMessageType('PlayerShipExploded', (_message.Message,), {'DESCRIPTOR': _PLAYERSHIPEXPLODED,
 '__module__': 'eve.effect.combat.pve_pb2'})
_sym_db.RegisterMessage(PlayerShipExploded)
DESCRIPTOR._options = None
_NPCSHIPEXPLODED._options = None
_PLAYERSHIPEXPLODED.fields_by_name['exploded']._options = None
_PLAYERSHIPEXPLODED.fields_by_name['exploded_ship_type']._options = None
_PLAYERSHIPEXPLODED.fields_by_name['solar_system']._options = None
_PLAYERSHIPEXPLODED.fields_by_name['exploded_ship']._options = None
