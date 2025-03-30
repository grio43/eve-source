#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pvp\structure\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.pvp import pvp_pb2 as eve_dot_pvp_dot_pvp__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.structure import group_pb2 as eve_dot_structure_dot_group__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from eveProto.generated.eve.structure import structure_type_pb2 as eve_dot_structure_dot_structure__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pvp/structure/api/events.proto', package='eve.pvp.structure.api', syntax='proto3', serialized_options='ZKgithub.com/ccpgames/eve-proto-go/generated/eve/effect/combat/electronic/pvp', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/pvp/structure/api/events.proto\x12\x15eve.pvp.structure.api\x1a%eve/constellation/constellation.proto\x1a\x11eve/pvp/pvp.proto\x1a\x17eve/region/region.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x19eve/structure/group.proto\x1a\x1deve/structure/structure.proto\x1a"eve/structure/structure_type.proto"\xfe\x02\n\x07Damaged\x12&\n\x08attacker\x18\x01 \x01(\x0b2\x14.eve.pvp.Participant\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12,\n\tstructure\x18\x03 \x01(\x0b2\x19.eve.structure.Identifier\x12\x1b\n\x13damage_amount_dealt\x18\x04 \x01(\r\x124\n\rconstellation\x18\x05 \x01(\x0b2\x1d.eve.constellation.Identifier\x12&\n\x06region\x18\x06 \x01(\x0b2\x16.eve.region.Identifier\x125\n\x0estructure_type\x18\x07 \x01(\x0b2\x1d.eve.structuretype.Identifier\x128\n\x0fstructure_group\x18\x08 \x01(\x0b2\x1f.eve.structure.group.IdentifierBMZKgithub.com/ccpgames/eve-proto-go/generated/eve/effect/combat/electronic/pvpb\x06proto3', dependencies=[eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR,
 eve_dot_pvp_dot_pvp__pb2.DESCRIPTOR,
 eve_dot_region_dot_region__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_structure_dot_group__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__type__pb2.DESCRIPTOR])
_DAMAGED = _descriptor.Descriptor(name='Damaged', full_name='eve.pvp.structure.api.Damaged', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attacker', full_name='eve.pvp.structure.api.Damaged.attacker', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.pvp.structure.api.Damaged.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.pvp.structure.api.Damaged.structure', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='damage_amount_dealt', full_name='eve.pvp.structure.api.Damaged.damage_amount_dealt', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.pvp.structure.api.Damaged.constellation', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.pvp.structure.api.Damaged.region', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure_type', full_name='eve.pvp.structure.api.Damaged.structure_type', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure_group', full_name='eve.pvp.structure.api.Damaged.structure_group', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=274, serialized_end=656)
_DAMAGED.fields_by_name['attacker'].message_type = eve_dot_pvp_dot_pvp__pb2._PARTICIPANT
_DAMAGED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_DAMAGED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_DAMAGED.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_DAMAGED.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_DAMAGED.fields_by_name['structure_type'].message_type = eve_dot_structure_dot_structure__type__pb2._IDENTIFIER
_DAMAGED.fields_by_name['structure_group'].message_type = eve_dot_structure_dot_group__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Damaged'] = _DAMAGED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Damaged = _reflection.GeneratedProtocolMessageType('Damaged', (_message.Message,), {'DESCRIPTOR': _DAMAGED,
 '__module__': 'eve.pvp.structure.api.events_pb2'})
_sym_db.RegisterMessage(Damaged)
DESCRIPTOR._options = None
