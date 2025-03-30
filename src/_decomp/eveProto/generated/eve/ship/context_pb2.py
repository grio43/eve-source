#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\context_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.ship import pilot_pb2 as eve_dot_ship_dot_pilot__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/context.proto', package='eve.ship', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/ship/context', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/ship/context.proto\x12\x08eve.ship\x1a\x14eve/ship/pilot.proto\x1a\x13eve/ship/ship.proto\x1a\x18eve/ship/ship_type.proto\x1a!eve/solarsystem/solarsystem.proto"\xad\x01\n\x07Context\x12\x1e\n\x05pilot\x18\x01 \x01(\x0b2\x0f.eve.ship.Pilot\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.Identifier\x12+\n\tship_type\x18\x03 \x01(\x0b2\x18.eve.shiptype.Identifier\x121\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB=Z;github.com/ccpgames/eve-proto-go/generated/eve/ship/contextb\x06proto3', dependencies=[eve_dot_ship_dot_pilot__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_CONTEXT = _descriptor.Descriptor(name='Context', full_name='eve.ship.Context', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pilot', full_name='eve.ship.Context.pilot', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.ship.Context.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship_type', full_name='eve.ship.Context.ship_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.ship.Context.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=141, serialized_end=314)
_CONTEXT.fields_by_name['pilot'].message_type = eve_dot_ship_dot_pilot__pb2._PILOT
_CONTEXT.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_CONTEXT.fields_by_name['ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_CONTEXT.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Context'] = _CONTEXT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Context = _reflection.GeneratedProtocolMessageType('Context', (_message.Message,), {'DESCRIPTOR': _CONTEXT,
 '__module__': 'eve.ship.context_pb2'})
_sym_db.RegisterMessage(Context)
DESCRIPTOR._options = None
