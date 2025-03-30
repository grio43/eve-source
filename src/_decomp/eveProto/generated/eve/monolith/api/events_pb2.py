#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\monolith\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/monolith/api/events.proto', package='eve.monolith.api', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/monolith/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/monolith/api/events.proto\x12\x10eve.monolith.api\x1a!eve/solarsystem/solarsystem.proto"F\n\x11SolarSystemLoaded\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB=Z;github.com/ccpgames/eve-proto-go/generated/eve/monolith/apib\x06proto3', dependencies=[eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_SOLARSYSTEMLOADED = _descriptor.Descriptor(name='SolarSystemLoaded', full_name='eve.monolith.api.SolarSystemLoaded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.monolith.api.SolarSystemLoaded.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=156)
_SOLARSYSTEMLOADED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['SolarSystemLoaded'] = _SOLARSYSTEMLOADED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SolarSystemLoaded = _reflection.GeneratedProtocolMessageType('SolarSystemLoaded', (_message.Message,), {'DESCRIPTOR': _SOLARSYSTEMLOADED,
 '__module__': 'eve.monolith.api.events_pb2'})
_sym_db.RegisterMessage(SolarSystemLoaded)
DESCRIPTOR._options = None
