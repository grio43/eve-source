#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pvp\ship\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.fighter import fighter_type_pb2 as eve_dot_fighter_dot_fighter__type__pb2
from eveProto.generated.eve.membership import membership_pb2 as eve_dot_membership_dot_membership__pb2
from eveProto.generated.eve.module import module_type_pb2 as eve_dot_module_dot_module__type__pb2
from eveProto.generated.eve.pvp import pvp_pb2 as eve_dot_pvp_dot_pvp__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve.ship.drone import drone_type_pb2 as eve_dot_ship_dot_drone_dot_drone__type__pb2
from eveProto.generated.eve.ship.module import charge_type_pb2 as eve_dot_ship_dot_module_dot_charge__type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pvp/ship/api.proto', package='eve.pvp.ship.api', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/pvp/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/pvp/ship/api.proto\x12\x10eve.pvp.ship.api\x1a%eve/constellation/constellation.proto\x1a\x1eeve/fighter/fighter_type.proto\x1a\x1feve/membership/membership.proto\x1a\x1ceve/module/module_type.proto\x1a\x11eve/pvp/pvp.proto\x1a\x17eve/region/region.proto\x1a\x1feve/ship/drone/drone_type.proto\x1a!eve/ship/module/charge_type.proto\x1a!eve/solarsystem/solarsystem.proto"\xf0\x02\n\tDestroyed\x12\'\n\tdestroyer\x18\x01 \x01(\x0b2\x14.eve.pvp.Participant\x12\'\n\tdestroyed\x18\x02 \x01(\x0b2\x14.eve.pvp.Participant\x12?\n\x14destroyed_membership\x18\x03 \x01(\x0b2\x1d.eve.membership.AllMembershipB\x02\x18\x01\x121\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12?\n\x14destroyer_membership\x18\x05 \x01(\x0b2\x1d.eve.membership.AllMembershipB\x02\x18\x01\x124\n\rconstellation\x18\x06 \x01(\x0b2\x1d.eve.constellation.Identifier\x12&\n\x06region\x18\x07 \x01(\x0b2\x16.eve.region.Identifier"\xce\x05\n\x07Damaged\x12&\n\x08attacker\x18\x01 \x01(\x0b2\x14.eve.pvp.Participant\x12&\n\x08attacked\x18\x02 \x01(\x0b2\x14.eve.pvp.Participant\x12>\n\x13attacked_membership\x18\x03 \x01(\x0b2\x1d.eve.membership.AllMembershipB\x02\x18\x01\x121\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12\x1b\n\x13damage_amount_dealt\x18\x05 \x01(\r\x124\n\rconstellation\x18\x06 \x01(\x0b2\x1d.eve.constellation.Identifier\x12&\n\x06region\x18\x07 \x01(\x0b2\x16.eve.region.Identifier\x12@\n\x0edamage_sources\x18\x08 \x03(\x0b2(.eve.pvp.ship.api.Damaged.DamageBySource\x1a\xc2\x02\n\x0eDamageBySource\x12\x1b\n\x13damage_amount_dealt\x18\x01 \x01(\r\x12\x1b\n\x11unregistered_type\x18\x02 \x01(\x04H\x00\x121\n\x0bmodule_type\x18\x03 \x01(\x0b2\x1a.eve.moduletype.IdentifierH\x00\x12;\n\tammo_type\x18\x04 \x01(\x0b2&.eve.ship.module.chargetype.IdentifierH\x00\x12:\n\ndrone_type\x18\x05 \x01(\x0b2$.eve.ship.drone.dronetype.IdentifierH\x00\x12;\n\x0cfighter_type\x18\x06 \x01(\x0b2#.eve.fighter.fightertype.IdentifierH\x00B\r\n\x0bsource_typeB=Z;github.com/ccpgames/eve-proto-go/generated/eve/pvp/ship/apib\x06proto3', dependencies=[eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR,
 eve_dot_fighter_dot_fighter__type__pb2.DESCRIPTOR,
 eve_dot_membership_dot_membership__pb2.DESCRIPTOR,
 eve_dot_module_dot_module__type__pb2.DESCRIPTOR,
 eve_dot_pvp_dot_pvp__pb2.DESCRIPTOR,
 eve_dot_region_dot_region__pb2.DESCRIPTOR,
 eve_dot_ship_dot_drone_dot_drone__type__pb2.DESCRIPTOR,
 eve_dot_ship_dot_module_dot_charge__type__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_DESTROYED = _descriptor.Descriptor(name='Destroyed', full_name='eve.pvp.ship.api.Destroyed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='destroyer', full_name='eve.pvp.ship.api.Destroyed.destroyer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='destroyed', full_name='eve.pvp.ship.api.Destroyed.destroyed', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='destroyed_membership', full_name='eve.pvp.ship.api.Destroyed.destroyed_membership', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.pvp.ship.api.Destroyed.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='destroyer_membership', full_name='eve.pvp.ship.api.Destroyed.destroyer_membership', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.pvp.ship.api.Destroyed.constellation', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.pvp.ship.api.Destroyed.region', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=326, serialized_end=694)
_DAMAGED_DAMAGEBYSOURCE = _descriptor.Descriptor(name='DamageBySource', full_name='eve.pvp.ship.api.Damaged.DamageBySource', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='damage_amount_dealt', full_name='eve.pvp.ship.api.Damaged.DamageBySource.damage_amount_dealt', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unregistered_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.unregistered_type', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='module_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.module_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ammo_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.ammo_type', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='drone_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.drone_type', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='fighter_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.fighter_type', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='source_type', full_name='eve.pvp.ship.api.Damaged.DamageBySource.source_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1093, serialized_end=1415)
_DAMAGED = _descriptor.Descriptor(name='Damaged', full_name='eve.pvp.ship.api.Damaged', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attacker', full_name='eve.pvp.ship.api.Damaged.attacker', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='attacked', full_name='eve.pvp.ship.api.Damaged.attacked', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='attacked_membership', full_name='eve.pvp.ship.api.Damaged.attacked_membership', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.pvp.ship.api.Damaged.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='damage_amount_dealt', full_name='eve.pvp.ship.api.Damaged.damage_amount_dealt', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.pvp.ship.api.Damaged.constellation', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.pvp.ship.api.Damaged.region', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='damage_sources', full_name='eve.pvp.ship.api.Damaged.damage_sources', index=7, number=8, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_DAMAGED_DAMAGEBYSOURCE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=697, serialized_end=1415)
_DESTROYED.fields_by_name['destroyer'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_DESTROYED.fields_by_name['destroyed'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_DESTROYED.fields_by_name['destroyed_membership'].message_type = eve_dot_membership_dot_membership__pb2._ALLMEMBERSHIP
_DESTROYED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_DESTROYED.fields_by_name['destroyer_membership'].message_type = eve_dot_membership_dot_membership__pb2._ALLMEMBERSHIP
_DESTROYED.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_DESTROYED.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['module_type'].message_type = eve_dot_module_dot_module__type__pb2._IDENTIFIER
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['ammo_type'].message_type = eve_dot_ship_dot_module_dot_charge__type__pb2._IDENTIFIER
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['drone_type'].message_type = eve_dot_ship_dot_drone_dot_drone__type__pb2._IDENTIFIER
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['fighter_type'].message_type = eve_dot_fighter_dot_fighter__type__pb2._IDENTIFIER
_DAMAGED_DAMAGEBYSOURCE.containing_type = _DAMAGED
_DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type'].fields.append(_DAMAGED_DAMAGEBYSOURCE.fields_by_name['unregistered_type'])
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['unregistered_type'].containing_oneof = _DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type']
_DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type'].fields.append(_DAMAGED_DAMAGEBYSOURCE.fields_by_name['module_type'])
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['module_type'].containing_oneof = _DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type']
_DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type'].fields.append(_DAMAGED_DAMAGEBYSOURCE.fields_by_name['ammo_type'])
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['ammo_type'].containing_oneof = _DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type']
_DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type'].fields.append(_DAMAGED_DAMAGEBYSOURCE.fields_by_name['drone_type'])
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['drone_type'].containing_oneof = _DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type']
_DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type'].fields.append(_DAMAGED_DAMAGEBYSOURCE.fields_by_name['fighter_type'])
_DAMAGED_DAMAGEBYSOURCE.fields_by_name['fighter_type'].containing_oneof = _DAMAGED_DAMAGEBYSOURCE.oneofs_by_name['source_type']
_DAMAGED.fields_by_name['attacker'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_DAMAGED.fields_by_name['attacked'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_DAMAGED.fields_by_name['attacked_membership'].message_type = eve_dot_membership_dot_membership__pb2._ALLMEMBERSHIP
_DAMAGED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_DAMAGED.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_DAMAGED.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_DAMAGED.fields_by_name['damage_sources'].message_type = _DAMAGED_DAMAGEBYSOURCE
DESCRIPTOR.message_types_by_name['Destroyed'] = _DESTROYED
DESCRIPTOR.message_types_by_name['Damaged'] = _DAMAGED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Destroyed = _reflection.GeneratedProtocolMessageType('Destroyed', (_message.Message,), {'DESCRIPTOR': _DESTROYED,
 '__module__': 'eve.pvp.ship.api_pb2'})
_sym_db.RegisterMessage(Destroyed)
Damaged = _reflection.GeneratedProtocolMessageType('Damaged', (_message.Message,), {'DamageBySource': _reflection.GeneratedProtocolMessageType('DamageBySource', (_message.Message,), {'DESCRIPTOR': _DAMAGED_DAMAGEBYSOURCE,
                    '__module__': 'eve.pvp.ship.api_pb2'}),
 'DESCRIPTOR': _DAMAGED,
 '__module__': 'eve.pvp.ship.api_pb2'})
_sym_db.RegisterMessage(Damaged)
_sym_db.RegisterMessage(Damaged.DamageBySource)
DESCRIPTOR._options = None
_DESTROYED.fields_by_name['destroyed_membership']._options = None
_DESTROYED.fields_by_name['destroyer_membership']._options = None
_DAMAGED.fields_by_name['attacked_membership']._options = None
