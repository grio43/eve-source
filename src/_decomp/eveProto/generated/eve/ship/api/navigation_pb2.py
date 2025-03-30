#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\api\navigation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.bookmark import bookmark_pb2 as eve_dot_bookmark_dot_bookmark__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.planet import planet_pb2 as eve_dot_planet_dot_planet__pb2
from eveProto.generated.eve.ship import context_pb2 as eve_dot_ship_dot_context__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/api/navigation.proto', package='eve.ship.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/ship/api/navigation.proto\x12\x0ceve.ship.api\x1a\x1beve/bookmark/bookmark.proto\x1a\x1deve/character/character.proto\x1a eve/inventory/generic_item.proto\x1a\x15eve/math/vector.proto\x1a\x17eve/planet/planet.proto\x1a\x16eve/ship/context.proto\x1a\x13eve/ship/ship.proto"\x8a\x02\n\x06Target\x12\x11\n\x07unknown\x18\x01 \x01(\x08H\x00\x12,\n\x08bookmark\x18\x02 \x01(\x0b2\x18.eve.bookmark.IdentifierH\x00\x12.\n\tcharacter\x18\x03 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x125\n\x04item\x18\x04 \x01(\x0b2%.eve.inventory.genericitem.IdentifierH\x00\x12$\n\x04ship\x18\x05 \x01(\x0b2\x14.eve.ship.IdentifierH\x00\x12(\n\x06planet\x18\x06 \x01(\x0b2\x16.eve.planet.IdentifierH\x00B\x08\n\x06target"y\n\x0cAlignOrdered\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.Context\x12$\n\x06target\x18\x02 \x01(\x0b2\x14.eve.ship.api.Target\x12\x1f\n\x04dest\x18\x03 \x01(\x0b2\x11.eve.math.Vector3"W\n\x0bWarpOrdered\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.Context\x12$\n\x06target\x18\x02 \x01(\x0b2\x14.eve.ship.api.Target"X\n\x0cOrbitOrdered\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.Context\x12$\n\x06target\x18\x02 \x01(\x0b2\x14.eve.ship.api.Target"V\n\x0fPointApproached\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.Context\x12\x1f\n\x04dest\x18\x02 \x01(\x0b2\x11.eve.math.Vector3"9\n\x13DirectionApproached\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.Context":\n\x14AbyssalGateActivated\x12"\n\x07context\x18\x01 \x01(\x0b2\x11.eve.ship.ContextB9Z7github.com/ccpgames/eve-proto-go/generated/eve/ship/apib\x06proto3', dependencies=[eve_dot_bookmark_dot_bookmark__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_math_dot_vector__pb2.DESCRIPTOR,
 eve_dot_planet_dot_planet__pb2.DESCRIPTOR,
 eve_dot_ship_dot_context__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_TARGET = _descriptor.Descriptor(name='Target', full_name='eve.ship.api.Target', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unknown', full_name='eve.ship.api.Target.unknown', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='bookmark', full_name='eve.ship.api.Target.bookmark', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.ship.api.Target.character', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='item', full_name='eve.ship.api.Target.item', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.ship.api.Target.ship', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='planet', full_name='eve.ship.api.Target.planet', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='target', full_name='eve.ship.api.Target.target', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=235, serialized_end=501)
_ALIGNORDERED = _descriptor.Descriptor(name='AlignOrdered', full_name='eve.ship.api.AlignOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.AlignOrdered.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='target', full_name='eve.ship.api.AlignOrdered.target', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='dest', full_name='eve.ship.api.AlignOrdered.dest', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=503, serialized_end=624)
_WARPORDERED = _descriptor.Descriptor(name='WarpOrdered', full_name='eve.ship.api.WarpOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.WarpOrdered.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='target', full_name='eve.ship.api.WarpOrdered.target', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=626, serialized_end=713)
_ORBITORDERED = _descriptor.Descriptor(name='OrbitOrdered', full_name='eve.ship.api.OrbitOrdered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.OrbitOrdered.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='target', full_name='eve.ship.api.OrbitOrdered.target', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=715, serialized_end=803)
_POINTAPPROACHED = _descriptor.Descriptor(name='PointApproached', full_name='eve.ship.api.PointApproached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.PointApproached.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='dest', full_name='eve.ship.api.PointApproached.dest', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=805, serialized_end=891)
_DIRECTIONAPPROACHED = _descriptor.Descriptor(name='DirectionApproached', full_name='eve.ship.api.DirectionApproached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.DirectionApproached.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=893, serialized_end=950)
_ABYSSALGATEACTIVATED = _descriptor.Descriptor(name='AbyssalGateActivated', full_name='eve.ship.api.AbyssalGateActivated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.ship.api.AbyssalGateActivated.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=952, serialized_end=1010)
_TARGET.fields_by_name['bookmark'].message_type = eve_dot_bookmark_dot_bookmark__pb2._IDENTIFIER
_TARGET.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TARGET.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_TARGET.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_TARGET.fields_by_name['planet'].message_type = eve_dot_planet_dot_planet__pb2._IDENTIFIER
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['unknown'])
_TARGET.fields_by_name['unknown'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['bookmark'])
_TARGET.fields_by_name['bookmark'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['character'])
_TARGET.fields_by_name['character'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['item'])
_TARGET.fields_by_name['item'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['ship'])
_TARGET.fields_by_name['ship'].containing_oneof = _TARGET.oneofs_by_name['target']
_TARGET.oneofs_by_name['target'].fields.append(_TARGET.fields_by_name['planet'])
_TARGET.fields_by_name['planet'].containing_oneof = _TARGET.oneofs_by_name['target']
_ALIGNORDERED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_ALIGNORDERED.fields_by_name['target'].message_type = _TARGET
_ALIGNORDERED.fields_by_name['dest'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_WARPORDERED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_WARPORDERED.fields_by_name['target'].message_type = _TARGET
_ORBITORDERED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_ORBITORDERED.fields_by_name['target'].message_type = _TARGET
_POINTAPPROACHED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_POINTAPPROACHED.fields_by_name['dest'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_DIRECTIONAPPROACHED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
_ABYSSALGATEACTIVATED.fields_by_name['context'].message_type = eve_dot_ship_dot_context__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['Target'] = _TARGET
DESCRIPTOR.message_types_by_name['AlignOrdered'] = _ALIGNORDERED
DESCRIPTOR.message_types_by_name['WarpOrdered'] = _WARPORDERED
DESCRIPTOR.message_types_by_name['OrbitOrdered'] = _ORBITORDERED
DESCRIPTOR.message_types_by_name['PointApproached'] = _POINTAPPROACHED
DESCRIPTOR.message_types_by_name['DirectionApproached'] = _DIRECTIONAPPROACHED
DESCRIPTOR.message_types_by_name['AbyssalGateActivated'] = _ABYSSALGATEACTIVATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Target = _reflection.GeneratedProtocolMessageType('Target', (_message.Message,), {'DESCRIPTOR': _TARGET,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(Target)
AlignOrdered = _reflection.GeneratedProtocolMessageType('AlignOrdered', (_message.Message,), {'DESCRIPTOR': _ALIGNORDERED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(AlignOrdered)
WarpOrdered = _reflection.GeneratedProtocolMessageType('WarpOrdered', (_message.Message,), {'DESCRIPTOR': _WARPORDERED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(WarpOrdered)
OrbitOrdered = _reflection.GeneratedProtocolMessageType('OrbitOrdered', (_message.Message,), {'DESCRIPTOR': _ORBITORDERED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(OrbitOrdered)
PointApproached = _reflection.GeneratedProtocolMessageType('PointApproached', (_message.Message,), {'DESCRIPTOR': _POINTAPPROACHED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(PointApproached)
DirectionApproached = _reflection.GeneratedProtocolMessageType('DirectionApproached', (_message.Message,), {'DESCRIPTOR': _DIRECTIONAPPROACHED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(DirectionApproached)
AbyssalGateActivated = _reflection.GeneratedProtocolMessageType('AbyssalGateActivated', (_message.Message,), {'DESCRIPTOR': _ABYSSALGATEACTIVATED,
 '__module__': 'eve.ship.api.navigation_pb2'})
_sym_db.RegisterMessage(AbyssalGateActivated)
DESCRIPTOR._options = None
