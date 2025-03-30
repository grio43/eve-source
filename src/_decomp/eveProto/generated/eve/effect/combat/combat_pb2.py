#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\effect\combat\combat_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.module import module_pb2 as eve_dot_module_dot_module__pb2
from eveProto.generated.eve.module import module_type_pb2 as eve_dot_module_dot_module__type__pb2
from eveProto.generated.eve.ship import combat_pb2 as eve_dot_ship_dot_combat__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/effect/combat/combat.proto', package='eve.effect.combat', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/effect/combat', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/effect/combat/combat.proto\x12\x11eve.effect.combat\x1a\x17eve/module/module.proto\x1a\x1ceve/module/module_type.proto\x1a\x15eve/ship/combat.proto"a\n\x06Module\x12*\n\nidentifier\x18\x01 \x01(\x0b2\x16.eve.module.Identifier\x12+\n\x07type_id\x18\x02 \x01(\x0b2\x1a.eve.moduletype.Identifier"p\n\x07Context\x12(\n\x06combat\x18\x01 \x01(\x0b2\x18.eve.ship.combat.Context\x12)\n\x06module\x18\x02 \x01(\x0b2\x19.eve.effect.combat.Module\x12\x10\n\x08distance\x18\x03 \x01(\x04B>Z<github.com/ccpgames/eve-proto-go/generated/eve/effect/combatb\x06proto3', dependencies=[eve_dot_module_dot_module__pb2.DESCRIPTOR, eve_dot_module_dot_module__type__pb2.DESCRIPTOR, eve_dot_ship_dot_combat__pb2.DESCRIPTOR])
_MODULE = _descriptor.Descriptor(name='Module', full_name='eve.effect.combat.Module', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.effect.combat.Module.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='type_id', full_name='eve.effect.combat.Module.type_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=131, serialized_end=228)
_CONTEXT = _descriptor.Descriptor(name='Context', full_name='eve.effect.combat.Context', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='combat', full_name='eve.effect.combat.Context.combat', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='module', full_name='eve.effect.combat.Context.module', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='distance', full_name='eve.effect.combat.Context.distance', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=230, serialized_end=342)
_MODULE.fields_by_name['identifier'].message_type = eve_dot_module_dot_module__pb2._IDENTIFIER
_MODULE.fields_by_name['type_id'].message_type = eve_dot_module_dot_module__type__pb2._IDENTIFIER
_CONTEXT.fields_by_name['combat'].message_type = eve_dot_ship_dot_combat__pb2._CONTEXT
_CONTEXT.fields_by_name['module'].message_type = _MODULE
DESCRIPTOR.message_types_by_name['Module'] = _MODULE
DESCRIPTOR.message_types_by_name['Context'] = _CONTEXT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Module = _reflection.GeneratedProtocolMessageType('Module', (_message.Message,), {'DESCRIPTOR': _MODULE,
 '__module__': 'eve.effect.combat.combat_pb2'})
_sym_db.RegisterMessage(Module)
Context = _reflection.GeneratedProtocolMessageType('Context', (_message.Message,), {'DESCRIPTOR': _CONTEXT,
 '__module__': 'eve.effect.combat.combat_pb2'})
_sym_db.RegisterMessage(Context)
DESCRIPTOR._options = None
