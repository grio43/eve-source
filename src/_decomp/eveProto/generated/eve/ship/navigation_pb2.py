#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\navigation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.ship import context_pb2 as eve_dot_ship_dot_context__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/navigation.proto', package='eve.ship.navigation', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/ship/navigation', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/ship/navigation.proto\x12\x13eve.ship.navigation\x1a\x1deve/character/character.proto\x1a\x15eve/math/vector.proto\x1a\x16eve/ship/context.proto\x1a!eve/solarsystem/solarsystem.proto"@\n\x0cAlignOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"J\n\x16AlignToBookmarkOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"I\n\x15WarpToBookmarkOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"E\n\x11WarpToCharOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"E\n\x11WarpToItemOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"E\n\x11WarpToScanOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"\xf8\x01\n\x0bWarpEntered\x12,\n\x05pilot\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierB\x02\x18\x01\x124\n\x0bsolarSystem\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB\x02\x18\x01\x12&\n\x0bdestination\x18\x03 \x01(\x0b2\x11.eve.math.Vector3\x12!\n\x06origin\x18\x04 \x01(\x0b2\x11.eve.math.Vector3\x12\x16\n\x0eaus_per_second\x18\x05 \x01(\x01\x12"\n\x07context\x18\x06 \x01(\x0b2\x11.eve.ship.Context"\xb9\x01\n\nWarpExited\x12,\n\x05pilot\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierB\x02\x18\x01\x124\n\x0bsolarSystem\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB\x02\x18\x01\x12#\n\x08location\x18\x03 \x01(\x0b2\x11.eve.math.Vector3\x12"\n\x07context\x18\x04 \x01(\x0b2\x11.eve.ship.Context"@\n\x0cOrbitOrdered\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"A\n\rFleetWarpLead\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"C\n\x0fPointApproached\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"K\n\x13DirectionApproached\x120\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierB\x02\x18\x01:\x02\x18\x01"H\n\x14AbyssalGateActivated\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01B@Z>github.com/ccpgames/eve-proto-go/generated/eve/ship/navigationb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_math_dot_vector__pb2.DESCRIPTOR,
 eve_dot_ship_dot_context__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_ALIGNORDERED = _descriptor.Descriptor(name='AlignOrdered', full_name='eve.ship.navigation.AlignOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.AlignOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=163, serialized_end=227)
_ALIGNTOBOOKMARKORDERED = _descriptor.Descriptor(name='AlignToBookmarkOrdered', full_name='eve.ship.navigation.AlignToBookmarkOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.AlignToBookmarkOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=229, serialized_end=303)
_WARPTOBOOKMARKORDERED = _descriptor.Descriptor(name='WarpToBookmarkOrdered', full_name='eve.ship.navigation.WarpToBookmarkOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.WarpToBookmarkOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=305, serialized_end=378)
_WARPTOCHARORDERED = _descriptor.Descriptor(name='WarpToCharOrdered', full_name='eve.ship.navigation.WarpToCharOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.WarpToCharOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=380, serialized_end=449)
_WARPTOITEMORDERED = _descriptor.Descriptor(name='WarpToItemOrdered', full_name='eve.ship.navigation.WarpToItemOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.WarpToItemOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=451, serialized_end=520)
_WARPTOSCANORDERED = _descriptor.Descriptor(name='WarpToScanOrdered', full_name='eve.ship.navigation.WarpToScanOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.WarpToScanOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=522, serialized_end=591)
_WARPENTERED = _descriptor.Descriptor(name='WarpEntered', full_name='eve.ship.navigation.WarpEntered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pilot', full_name='eve.ship.navigation.WarpEntered.pilot', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solarSystem', full_name='eve.ship.navigation.WarpEntered.solarSystem', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='destination', full_name='eve.ship.navigation.WarpEntered.destination', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='origin', full_name='eve.ship.navigation.WarpEntered.origin', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='aus_per_second', full_name='eve.ship.navigation.WarpEntered.aus_per_second', index=4, number=5, type=1, cpp_type=5, label=1, has_default_value=False, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.ship.navigation.WarpEntered.context', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=594, serialized_end=842)
_WARPEXITED = _descriptor.Descriptor(name='WarpExited', full_name='eve.ship.navigation.WarpExited', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pilot', full_name='eve.ship.navigation.WarpExited.pilot', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solarSystem', full_name='eve.ship.navigation.WarpExited.solarSystem', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='location', full_name='eve.ship.navigation.WarpExited.location', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.ship.navigation.WarpExited.context', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=845, serialized_end=1030)
_ORBITORDERED = _descriptor.Descriptor(name='OrbitOrdered', full_name='eve.ship.navigation.OrbitOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.OrbitOrdered.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1032, serialized_end=1096)
_FLEETWARPLEAD = _descriptor.Descriptor(name='FleetWarpLead', full_name='eve.ship.navigation.FleetWarpLead', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.FleetWarpLead.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1098, serialized_end=1163)
_POINTAPPROACHED = _descriptor.Descriptor(name='PointApproached', full_name='eve.ship.navigation.PointApproached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.PointApproached.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1165, serialized_end=1232)
_DIRECTIONAPPROACHED = _descriptor.Descriptor(name='DirectionApproached', full_name='eve.ship.navigation.DirectionApproached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.DirectionApproached.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1234, serialized_end=1309)
_ABYSSALGATEACTIVATED = _descriptor.Descriptor(name='AbyssalGateActivated', full_name='eve.ship.navigation.AbyssalGateActivated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.navigation.AbyssalGateActivated.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1311, serialized_end=1383)
_ALIGNORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ALIGNTOBOOKMARKORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPTOBOOKMARKORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPTOCHARORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPTOITEMORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPTOSCANORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPENTERED.fields_by_name['pilot'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPENTERED.fields_by_name['solarSystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_WARPENTERED.fields_by_name['destination'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_WARPENTERED.fields_by_name['origin'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_WARPENTERED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_WARPEXITED.fields_by_name['pilot'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_WARPEXITED.fields_by_name['solarSystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_WARPEXITED.fields_by_name['location'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_WARPEXITED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_ORBITORDERED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_FLEETWARPLEAD.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_POINTAPPROACHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_DIRECTIONAPPROACHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ABYSSALGATEACTIVATED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['AlignOrdered'] = _ALIGNORDERED
DESCRIPTOR.message_types_by_name['AlignToBookmarkOrdered'] = _ALIGNTOBOOKMARKORDERED
DESCRIPTOR.message_types_by_name['WarpToBookmarkOrdered'] = _WARPTOBOOKMARKORDERED
DESCRIPTOR.message_types_by_name['WarpToCharOrdered'] = _WARPTOCHARORDERED
DESCRIPTOR.message_types_by_name['WarpToItemOrdered'] = _WARPTOITEMORDERED
DESCRIPTOR.message_types_by_name['WarpToScanOrdered'] = _WARPTOSCANORDERED
DESCRIPTOR.message_types_by_name['WarpEntered'] = _WARPENTERED
DESCRIPTOR.message_types_by_name['WarpExited'] = _WARPEXITED
DESCRIPTOR.message_types_by_name['OrbitOrdered'] = _ORBITORDERED
DESCRIPTOR.message_types_by_name['FleetWarpLead'] = _FLEETWARPLEAD
DESCRIPTOR.message_types_by_name['PointApproached'] = _POINTAPPROACHED
DESCRIPTOR.message_types_by_name['DirectionApproached'] = _DIRECTIONAPPROACHED
DESCRIPTOR.message_types_by_name['AbyssalGateActivated'] = _ABYSSALGATEACTIVATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
AlignOrdered = _reflection.GeneratedProtocolMessageType('AlignOrdered', (_message.Message,), {'DESCRIPTOR': _ALIGNORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(AlignOrdered)
AlignToBookmarkOrdered = _reflection.GeneratedProtocolMessageType('AlignToBookmarkOrdered', (_message.Message,), {'DESCRIPTOR': _ALIGNTOBOOKMARKORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(AlignToBookmarkOrdered)
WarpToBookmarkOrdered = _reflection.GeneratedProtocolMessageType('WarpToBookmarkOrdered', (_message.Message,), {'DESCRIPTOR': _WARPTOBOOKMARKORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpToBookmarkOrdered)
WarpToCharOrdered = _reflection.GeneratedProtocolMessageType('WarpToCharOrdered', (_message.Message,), {'DESCRIPTOR': _WARPTOCHARORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpToCharOrdered)
WarpToItemOrdered = _reflection.GeneratedProtocolMessageType('WarpToItemOrdered', (_message.Message,), {'DESCRIPTOR': _WARPTOITEMORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpToItemOrdered)
WarpToScanOrdered = _reflection.GeneratedProtocolMessageType('WarpToScanOrdered', (_message.Message,), {'DESCRIPTOR': _WARPTOSCANORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpToScanOrdered)
WarpEntered = _reflection.GeneratedProtocolMessageType('WarpEntered', (_message.Message,), {'DESCRIPTOR': _WARPENTERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpEntered)
WarpExited = _reflection.GeneratedProtocolMessageType('WarpExited', (_message.Message,), {'DESCRIPTOR': _WARPEXITED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(WarpExited)
OrbitOrdered = _reflection.GeneratedProtocolMessageType('OrbitOrdered', (_message.Message,), {'DESCRIPTOR': _ORBITORDERED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(OrbitOrdered)
FleetWarpLead = _reflection.GeneratedProtocolMessageType('FleetWarpLead', (_message.Message,), {'DESCRIPTOR': _FLEETWARPLEAD,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(FleetWarpLead)
PointApproached = _reflection.GeneratedProtocolMessageType('PointApproached', (_message.Message,), {'DESCRIPTOR': _POINTAPPROACHED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(PointApproached)
DirectionApproached = _reflection.GeneratedProtocolMessageType('DirectionApproached', (_message.Message,), {'DESCRIPTOR': _DIRECTIONAPPROACHED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(DirectionApproached)
AbyssalGateActivated = _reflection.GeneratedProtocolMessageType('AbyssalGateActivated', (_message.Message,), {'DESCRIPTOR': _ABYSSALGATEACTIVATED,
 '__module__': 'eve.ship.navigation_pb2'})
_sym_db.RegisterMessage(AbyssalGateActivated)
DESCRIPTOR._options = None
_ALIGNORDERED._options = None
_ALIGNTOBOOKMARKORDERED._options = None
_WARPTOBOOKMARKORDERED._options = None
_WARPTOCHARORDERED._options = None
_WARPTOITEMORDERED._options = None
_WARPTOSCANORDERED._options = None
_WARPENTERED.fields_by_name['pilot']._options = None
_WARPENTERED.fields_by_name['solarSystem']._options = None
_WARPEXITED.fields_by_name['pilot']._options = None
_WARPEXITED.fields_by_name['solarSystem']._options = None
_ORBITORDERED._options = None
_FLEETWARPLEAD._options = None
_POINTAPPROACHED._options = None
_DIRECTIONAPPROACHED.fields_by_name['character']._options = None
_DIRECTIONAPPROACHED._options = None
_ABYSSALGATEACTIVATED._options = None
