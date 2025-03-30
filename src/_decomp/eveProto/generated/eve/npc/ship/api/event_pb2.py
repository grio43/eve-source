#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\npc\ship\api\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.npc.ship import ship_pb2 as eve_dot_npc_dot_ship_dot_ship__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/npc/ship/api/event.proto', package='eve.npc.ship.api', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/npc/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/npc/ship/api/event.proto\x12\x10eve.npc.ship.api\x1a\x1deve/character/character.proto\x1a%eve/constellation/constellation.proto\x1a\x19eve/faction/faction.proto\x1a\x17eve/npc/ship/ship.proto\x1a\x17eve/region/region.proto\x1a\x18eve/ship/ship_type.proto\x1a!eve/solarsystem/solarsystem.proto"\xa3\x04\n\x08Exploded\x12%\n\x03npc\x18\x01 \x01(\x0b2\x18.eve.npc.ship.Identifier\x12.\n\x07faction\x18\x02 \x01(\x0b2\x17.eve.faction.IdentifierB\x02\x18\x01H\x00\x12$\n\x16no_faction_affiliation\x18\x03 \x01(\x08B\x02\x18\x01H\x00\x122\n\x06killer\x18\x04 \x01(\x0b2 .eve.npc.ship.api.Exploded.PilotH\x01\x12\x18\n\x0ekiller_unknown\x18\x05 \x01(\x08H\x01\x126\n\x0cparticipants\x18\x06 \x03(\x0b2 .eve.npc.ship.api.Exploded.Pilot\x121\n\x0csolar_system\x18\x07 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12&\n\x06region\x18\x08 \x01(\x0b2\x16.eve.region.Identifier\x124\n\rconstellation\x18\t \x01(\x0b2\x1d.eve.constellation.Identifier\x1a^\n\x05Pilot\x12(\n\x05pilot\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12+\n\tship_type\x18\x02 \x01(\x0b2\x18.eve.shiptype.IdentifierB\x15\n\x13faction_affiliationB\x0c\n\nfinal_blowB=Z;github.com/ccpgames/eve-proto-go/generated/eve/npc/ship/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_npc_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_region_dot_region__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_EXPLODED_PILOT = _descriptor.Descriptor(name='Pilot', full_name='eve.npc.ship.api.Exploded.Pilot', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pilot', full_name='eve.npc.ship.api.Exploded.Pilot.pilot', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ship_type', full_name='eve.npc.ship.api.Exploded.Pilot.ship_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=675, serialized_end=769)
_EXPLODED = _descriptor.Descriptor(name='Exploded', full_name='eve.npc.ship.api.Exploded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='npc', full_name='eve.npc.ship.api.Exploded.npc', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='faction', full_name='eve.npc.ship.api.Exploded.faction', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_faction_affiliation', full_name='eve.npc.ship.api.Exploded.no_faction_affiliation', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='killer', full_name='eve.npc.ship.api.Exploded.killer', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='killer_unknown', full_name='eve.npc.ship.api.Exploded.killer_unknown', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='participants', full_name='eve.npc.ship.api.Exploded.participants', index=5, number=6, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.npc.ship.api.Exploded.solar_system', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.npc.ship.api.Exploded.region', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.npc.ship.api.Exploded.constellation', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_EXPLODED_PILOT], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='faction_affiliation', full_name='eve.npc.ship.api.Exploded.faction_affiliation', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='final_blow', full_name='eve.npc.ship.api.Exploded.final_blow', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=259, serialized_end=806)
_EXPLODED_PILOT.fields_by_name['pilot'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_EXPLODED_PILOT.fields_by_name['ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_EXPLODED_PILOT.containing_type = _EXPLODED
_EXPLODED.fields_by_name['npc'].message_type = eve_dot_npc_dot_ship_dot_ship__pb2._IDENTIFIER
_EXPLODED.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_EXPLODED.fields_by_name['killer'].message_type = _EXPLODED_PILOT
_EXPLODED.fields_by_name['participants'].message_type = _EXPLODED_PILOT
_EXPLODED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_EXPLODED.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_EXPLODED.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_EXPLODED.oneofs_by_name['faction_affiliation'].fields.append(_EXPLODED.fields_by_name['faction'])
_EXPLODED.fields_by_name['faction'].containing_oneof = _EXPLODED.oneofs_by_name['faction_affiliation']
_EXPLODED.oneofs_by_name['faction_affiliation'].fields.append(_EXPLODED.fields_by_name['no_faction_affiliation'])
_EXPLODED.fields_by_name['no_faction_affiliation'].containing_oneof = _EXPLODED.oneofs_by_name['faction_affiliation']
_EXPLODED.oneofs_by_name['final_blow'].fields.append(_EXPLODED.fields_by_name['killer'])
_EXPLODED.fields_by_name['killer'].containing_oneof = _EXPLODED.oneofs_by_name['final_blow']
_EXPLODED.oneofs_by_name['final_blow'].fields.append(_EXPLODED.fields_by_name['killer_unknown'])
_EXPLODED.fields_by_name['killer_unknown'].containing_oneof = _EXPLODED.oneofs_by_name['final_blow']
DESCRIPTOR.message_types_by_name['Exploded'] = _EXPLODED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Exploded = _reflection.GeneratedProtocolMessageType('Exploded', (_message.Message,), {'Pilot': _reflection.GeneratedProtocolMessageType('Pilot', (_message.Message,), {'DESCRIPTOR': _EXPLODED_PILOT,
           '__module__': 'eve.npc.ship.api.event_pb2'}),
 'DESCRIPTOR': _EXPLODED,
 '__module__': 'eve.npc.ship.api.event_pb2'})
_sym_db.RegisterMessage(Exploded)
_sym_db.RegisterMessage(Exploded.Pilot)
DESCRIPTOR._options = None
_EXPLODED.fields_by_name['faction']._options = None
_EXPLODED.fields_by_name['no_faction_affiliation']._options = None
