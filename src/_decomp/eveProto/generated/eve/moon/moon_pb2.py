#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\moon\moon_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.planet import planet_pb2 as eve_dot_planet_dot_planet__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/moon/moon.proto', package='eve.moon', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/moon', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/moon/moon.proto\x12\x08eve.moon\x1a\x15eve/math/vector.proto\x1a\x17eve/planet/planet.proto\x1a!eve/solarsystem/solarsystem.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"r\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12#\n\x08position\x18\x02 \x01(\x0b2\x11.eve.math.Vector3\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier"0\n\nGetRequest\x12"\n\x04moon\x18\x01 \x01(\x0b2\x14.eve.moon.Identifier"7\n\x0bGetResponse\x12(\n\nattributes\x18\x01 \x01(\x0b2\x14.eve.moon.Attributes"A\n\x17GetMoonsOfPlanetRequest\x12&\n\x06planet\x18\x01 \x01(\x0b2\x16.eve.planet.Identifier"?\n\x18GetMoonsOfPlanetResponse\x12#\n\x05moons\x18\x01 \x03(\x0b2\x14.eve.moon.IdentifierB5Z3github.com/ccpgames/eve-proto-go/generated/eve/moonb\x06proto3', dependencies=[eve_dot_math_dot_vector__pb2.DESCRIPTOR, eve_dot_planet_dot_planet__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.moon.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.moon.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=116, serialized_end=148)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.moon.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.moon.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='position', full_name='eve.moon.Attributes.position', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.moon.Attributes.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=264)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.moon.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='moon', full_name='eve.moon.GetRequest.moon', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=266, serialized_end=314)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.moon.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.moon.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=316, serialized_end=371)
_GETMOONSOFPLANETREQUEST = _descriptor.Descriptor(name='GetMoonsOfPlanetRequest', full_name='eve.moon.GetMoonsOfPlanetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='planet', full_name='eve.moon.GetMoonsOfPlanetRequest.planet', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=373, serialized_end=438)
_GETMOONSOFPLANETRESPONSE = _descriptor.Descriptor(name='GetMoonsOfPlanetResponse', full_name='eve.moon.GetMoonsOfPlanetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='moons', full_name='eve.moon.GetMoonsOfPlanetResponse.moons', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=440, serialized_end=503)
_ATTRIBUTES.fields_by_name['position'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_ATTRIBUTES.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['moon'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = _ATTRIBUTES
_GETMOONSOFPLANETREQUEST.fields_by_name['planet'].message_type = eve_dot_planet_dot_planet__pb2._IDENTIFIER
_GETMOONSOFPLANETRESPONSE.fields_by_name['moons'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetMoonsOfPlanetRequest'] = _GETMOONSOFPLANETREQUEST
DESCRIPTOR.message_types_by_name['GetMoonsOfPlanetResponse'] = _GETMOONSOFPLANETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetMoonsOfPlanetRequest = _reflection.GeneratedProtocolMessageType('GetMoonsOfPlanetRequest', (_message.Message,), {'DESCRIPTOR': _GETMOONSOFPLANETREQUEST,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(GetMoonsOfPlanetRequest)
GetMoonsOfPlanetResponse = _reflection.GeneratedProtocolMessageType('GetMoonsOfPlanetResponse', (_message.Message,), {'DESCRIPTOR': _GETMOONSOFPLANETRESPONSE,
 '__module__': 'eve.moon.moon_pb2'})
_sym_db.RegisterMessage(GetMoonsOfPlanetResponse)
DESCRIPTOR._options = None
