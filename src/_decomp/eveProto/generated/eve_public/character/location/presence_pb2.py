#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\character\location\presence_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.solarsystem import solarsystem_pb2 as eve__public_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/character/location/presence.proto', package='eve_public.character.location.presence', syntax='proto3', serialized_options='ZQgithub.com/ccpgames/eve-proto-go/generated/eve_public/character/location/presence', create_key=_descriptor._internal_create_key, serialized_pb='\n,eve_public/character/location/presence.proto\x12&eve_public.character.location.presence\x1a(eve_public/solarsystem/solarsystem.proto"X\n\x18SolarSystemEnteredNotice\x128\n\x0csolar_system\x18\x01 \x01(\x0b2".eve_public.solarsystem.Identifier:\x02\x18\x01"W\n\x17SolarSystemExitedNotice\x128\n\x0csolar_system\x18\x01 \x01(\x0b2".eve_public.solarsystem.Identifier:\x02\x18\x01BSZQgithub.com/ccpgames/eve-proto-go/generated/eve_public/character/location/presenceb\x06proto3', dependencies=[eve__public_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_SOLARSYSTEMENTEREDNOTICE = _descriptor.Descriptor(name='SolarSystemEnteredNotice', full_name='eve_public.character.location.presence.SolarSystemEnteredNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve_public.character.location.presence.SolarSystemEnteredNotice.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=130, serialized_end=218)
_SOLARSYSTEMEXITEDNOTICE = _descriptor.Descriptor(name='SolarSystemExitedNotice', full_name='eve_public.character.location.presence.SolarSystemExitedNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve_public.character.location.presence.SolarSystemExitedNotice.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=220, serialized_end=307)
_SOLARSYSTEMENTEREDNOTICE.fields_by_name['solar_system'].message_type = eve__public_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_SOLARSYSTEMEXITEDNOTICE.fields_by_name['solar_system'].message_type = eve__public_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['SolarSystemEnteredNotice'] = _SOLARSYSTEMENTEREDNOTICE
DESCRIPTOR.message_types_by_name['SolarSystemExitedNotice'] = _SOLARSYSTEMEXITEDNOTICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SolarSystemEnteredNotice = _reflection.GeneratedProtocolMessageType('SolarSystemEnteredNotice', (_message.Message,), {'DESCRIPTOR': _SOLARSYSTEMENTEREDNOTICE,
 '__module__': 'eve_public.character.location.presence_pb2'})
_sym_db.RegisterMessage(SolarSystemEnteredNotice)
SolarSystemExitedNotice = _reflection.GeneratedProtocolMessageType('SolarSystemExitedNotice', (_message.Message,), {'DESCRIPTOR': _SOLARSYSTEMEXITEDNOTICE,
 '__module__': 'eve_public.character.location.presence_pb2'})
_sym_db.RegisterMessage(SolarSystemExitedNotice)
DESCRIPTOR._options = None
_SOLARSYSTEMENTEREDNOTICE._options = None
_SOLARSYSTEMEXITEDNOTICE._options = None
