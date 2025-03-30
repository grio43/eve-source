#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\structure\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.bubble import bubble_pb2 as eve_dot_bubble_dot_bubble__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/structure/api/api.proto', package='eve.structure.api', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/structure/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/structure/api/api.proto\x12\x11eve.structure.api\x1a\x17eve/bubble/bubble.proto\x1a\x1deve/character/character.proto\x1a\x13eve/ship/ship.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1deve/structure/structure.proto"A\n\x11UpkeepFullPowered\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier"@\n\x10UpkeepLowPowered\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier"?\n\x0fUpkeepAbandoned\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier"\xba\x03\n\x07Boarded\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12,\n\tstructure\x18\x02 \x01(\x0b2\x19.eve.structure.Identifier\x12-\n\rprevious_ship\x18\x03 \x01(\x0b2\x14.eve.ship.IdentifierH\x00\x127\n\x12previous_structure\x18\x04 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x12\x11\n\x07unknown\x18\x05 \x01(\x08H\x00\x123\n\x07context\x18\x06 \x01(\x0b2".eve.structure.api.Boarded.Context\x1a\x8d\x01\n\x07Context\x12(\n\x06bubble\x18\x01 \x01(\x0b2\x16.eve.bubble.IdentifierH\x00\x12\x13\n\tno_bubble\x18\x02 \x01(\x08H\x00\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB\x10\n\x0ecurrent_bubbleB\x13\n\x11previous_locationB>Z<github.com/ccpgames/eve-proto-go/generated/eve/structure/apib\x06proto3', dependencies=[eve_dot_bubble_dot_bubble__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_UPKEEPFULLPOWERED = _descriptor.Descriptor(name='UpkeepFullPowered', full_name='eve.structure.api.UpkeepFullPowered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.structure.api.UpkeepFullPowered.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=193, serialized_end=258)
_UPKEEPLOWPOWERED = _descriptor.Descriptor(name='UpkeepLowPowered', full_name='eve.structure.api.UpkeepLowPowered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.structure.api.UpkeepLowPowered.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=260, serialized_end=324)
_UPKEEPABANDONED = _descriptor.Descriptor(name='UpkeepAbandoned', full_name='eve.structure.api.UpkeepAbandoned', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.structure.api.UpkeepAbandoned.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=326, serialized_end=389)
_BOARDED_CONTEXT = _descriptor.Descriptor(name='Context', full_name='eve.structure.api.Boarded.Context', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='bubble', full_name='eve.structure.api.Boarded.Context.bubble', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='no_bubble', full_name='eve.structure.api.Boarded.Context.no_bubble', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.structure.api.Boarded.Context.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='current_bubble', full_name='eve.structure.api.Boarded.Context.current_bubble', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=672, serialized_end=813)
_BOARDED = _descriptor.Descriptor(name='Boarded', full_name='eve.structure.api.Boarded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.structure.api.Boarded.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.structure.api.Boarded.structure', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='previous_ship', full_name='eve.structure.api.Boarded.previous_ship', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='previous_structure', full_name='eve.structure.api.Boarded.previous_structure', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown', full_name='eve.structure.api.Boarded.unknown', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.structure.api.Boarded.context', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_BOARDED_CONTEXT], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='previous_location', full_name='eve.structure.api.Boarded.previous_location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=392, serialized_end=834)
_UPKEEPFULLPOWERED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_UPKEEPLOWPOWERED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_UPKEEPABANDONED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_BOARDED_CONTEXT.fields_by_name['bubble'].message_type = eve_dot_bubble_dot_bubble__pb2._IDENTIFIER
_BOARDED_CONTEXT.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_BOARDED_CONTEXT.containing_type = _BOARDED
_BOARDED_CONTEXT.oneofs_by_name['current_bubble'].fields.append(_BOARDED_CONTEXT.fields_by_name['bubble'])
_BOARDED_CONTEXT.fields_by_name['bubble'].containing_oneof = _BOARDED_CONTEXT.oneofs_by_name['current_bubble']
_BOARDED_CONTEXT.oneofs_by_name['current_bubble'].fields.append(_BOARDED_CONTEXT.fields_by_name['no_bubble'])
_BOARDED_CONTEXT.fields_by_name['no_bubble'].containing_oneof = _BOARDED_CONTEXT.oneofs_by_name['current_bubble']
_BOARDED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_BOARDED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_BOARDED.fields_by_name['previous_ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_BOARDED.fields_by_name['previous_structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_BOARDED.fields_by_name['context'].message_type = _BOARDED_CONTEXT
_BOARDED.oneofs_by_name['previous_location'].fields.append(_BOARDED.fields_by_name['previous_ship'])
_BOARDED.fields_by_name['previous_ship'].containing_oneof = _BOARDED.oneofs_by_name['previous_location']
_BOARDED.oneofs_by_name['previous_location'].fields.append(_BOARDED.fields_by_name['previous_structure'])
_BOARDED.fields_by_name['previous_structure'].containing_oneof = _BOARDED.oneofs_by_name['previous_location']
_BOARDED.oneofs_by_name['previous_location'].fields.append(_BOARDED.fields_by_name['unknown'])
_BOARDED.fields_by_name['unknown'].containing_oneof = _BOARDED.oneofs_by_name['previous_location']
DESCRIPTOR.message_types_by_name['UpkeepFullPowered'] = _UPKEEPFULLPOWERED
DESCRIPTOR.message_types_by_name['UpkeepLowPowered'] = _UPKEEPLOWPOWERED
DESCRIPTOR.message_types_by_name['UpkeepAbandoned'] = _UPKEEPABANDONED
DESCRIPTOR.message_types_by_name['Boarded'] = _BOARDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
UpkeepFullPowered = _reflection.GeneratedProtocolMessageType('UpkeepFullPowered', (_message.Message,), {'DESCRIPTOR': _UPKEEPFULLPOWERED,
 '__module__': 'eve.structure.api.api_pb2'})
_sym_db.RegisterMessage(UpkeepFullPowered)
UpkeepLowPowered = _reflection.GeneratedProtocolMessageType('UpkeepLowPowered', (_message.Message,), {'DESCRIPTOR': _UPKEEPLOWPOWERED,
 '__module__': 'eve.structure.api.api_pb2'})
_sym_db.RegisterMessage(UpkeepLowPowered)
UpkeepAbandoned = _reflection.GeneratedProtocolMessageType('UpkeepAbandoned', (_message.Message,), {'DESCRIPTOR': _UPKEEPABANDONED,
 '__module__': 'eve.structure.api.api_pb2'})
_sym_db.RegisterMessage(UpkeepAbandoned)
Boarded = _reflection.GeneratedProtocolMessageType('Boarded', (_message.Message,), {'Context': _reflection.GeneratedProtocolMessageType('Context', (_message.Message,), {'DESCRIPTOR': _BOARDED_CONTEXT,
             '__module__': 'eve.structure.api.api_pb2'}),
 'DESCRIPTOR': _BOARDED,
 '__module__': 'eve.structure.api.api_pb2'})
_sym_db.RegisterMessage(Boarded)
_sym_db.RegisterMessage(Boarded.Context)
DESCRIPTOR._options = None
