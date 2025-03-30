#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\probe\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.deadspace import archetype_pb2 as eve_dot_deadspace_dot_archetype__pb2
from eveProto.generated.eve.deadspace import signaturetype_pb2 as eve_dot_deadspace_dot_signaturetype__pb2
from eveProto.generated.eve.probe import exploration_scanresult_pb2 as eve_dot_probe_dot_exploration__scanresult__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/probe/event.proto', package='eve.probe.event', syntax='proto3', serialized_options='Z:github.com/ccpgames/eve-proto-go/generated/eve/probe/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/probe/event.proto\x12\x0feve.probe.event\x1a\x1deve/character/character.proto\x1a%eve/constellation/constellation.proto\x1a\x1deve/deadspace/archetype.proto\x1a!eve/deadspace/signaturetype.proto\x1a&eve/probe/exploration_scanresult.proto\x1a\x17eve/region/region.proto\x1a!eve/solarsystem/solarsystem.proto"\x9b\x03\n\x1bExplorationSignatureScanned\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12D\n\x0bscan_result\x18\x02 \x01(\x0b2+.eve.probe.explorationscanresult.AttributesB\x02\x18\x01\x126\n\tarchetype\x18\x03 \x01(\x0b2#.eve.deadspace.archetype.Identifier\x12?\n\x0esignature_type\x18\x04 \x01(\x0b2\'.eve.deadspace.signaturetype.Identifier\x121\n\x0csolar_system\x18\x05 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x124\n\rconstellation\x18\x06 \x01(\x0b2\x1d.eve.constellation.Identifier\x12&\n\x06region\x18\x07 \x01(\x0b2\x16.eve.region.IdentifierB<Z:github.com/ccpgames/eve-proto-go/generated/eve/probe/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR,
 eve_dot_deadspace_dot_archetype__pb2.DESCRIPTOR,
 eve_dot_deadspace_dot_signaturetype__pb2.DESCRIPTOR,
 eve_dot_probe_dot_exploration__scanresult__pb2.DESCRIPTOR,
 eve_dot_region_dot_region__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_EXPLORATIONSIGNATURESCANNED = _descriptor.Descriptor(name='ExplorationSignatureScanned', full_name='eve.probe.event.ExplorationSignatureScanned', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.probe.event.ExplorationSignatureScanned.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='scan_result', full_name='eve.probe.event.ExplorationSignatureScanned.scan_result', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='archetype', full_name='eve.probe.event.ExplorationSignatureScanned.archetype', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='signature_type', full_name='eve.probe.event.ExplorationSignatureScanned.signature_type', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.probe.event.ExplorationSignatureScanned.solar_system', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='constellation', full_name='eve.probe.event.ExplorationSignatureScanned.constellation', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.probe.event.ExplorationSignatureScanned.region', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=279, serialized_end=690)
_EXPLORATIONSIGNATURESCANNED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_EXPLORATIONSIGNATURESCANNED.fields_by_name['scan_result'].message_type = eve_dot_probe_dot_exploration__scanresult__pb2._ATTRIBUTES
_EXPLORATIONSIGNATURESCANNED.fields_by_name['archetype'].message_type = eve_dot_deadspace_dot_archetype__pb2._IDENTIFIER
_EXPLORATIONSIGNATURESCANNED.fields_by_name['signature_type'].message_type = eve_dot_deadspace_dot_signaturetype__pb2._IDENTIFIER
_EXPLORATIONSIGNATURESCANNED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_EXPLORATIONSIGNATURESCANNED.fields_by_name['constellation'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
_EXPLORATIONSIGNATURESCANNED.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ExplorationSignatureScanned'] = _EXPLORATIONSIGNATURESCANNED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ExplorationSignatureScanned = _reflection.GeneratedProtocolMessageType('ExplorationSignatureScanned', (_message.Message,), {'DESCRIPTOR': _EXPLORATIONSIGNATURESCANNED,
 '__module__': 'eve.probe.event_pb2'})
_sym_db.RegisterMessage(ExplorationSignatureScanned)
DESCRIPTOR._options = None
_EXPLORATIONSIGNATURESCANNED.fields_by_name['scan_result']._options = None
