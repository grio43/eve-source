#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\planet\planet_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.planet import planet_type_pb2 as eve_dot_planet_dot_planet__type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/planet/planet.proto', package='eve.planet', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/planet', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/planet/planet.proto\x12\neve.planet\x1a\x15eve/math/vector.proto\x1a\x1ceve/planet/planet_type.proto\x1a!eve/solarsystem/solarsystem.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\xc5\x01\n\nAttributes\x120\n\x0bsolarsystem\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12(\n\x07surface\x18\x02 \x01(\x0e2\x13.eve.planet.SurfaceB\x02\x18\x01\x12\x0c\n\x04name\x18\x03 \x01(\t\x12#\n\x08position\x18\x04 \x01(\x0b2\x11.eve.math.Vector3\x12(\n\x04type\x18\x05 \x01(\x0b2\x1a.eve.planettype.Identifier"X\n\x06Planet\x12"\n\x02id\x18\x01 \x01(\x0b2\x16.eve.planet.Identifier\x12*\n\nattributes\x18\x02 \x01(\x0b2\x16.eve.planet.Attributes"4\n\nGetRequest\x12&\n\x06planet\x18\x01 \x01(\x0b2\x16.eve.planet.Identifier"5\n\x0bGetResponse\x12&\n\x06planet\x18\x01 \x01(\x0b2\x16.eve.planet.Attributes"S\n\x1eGetPlanetsInSolarSystemRequest\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier"J\n\x1fGetPlanetsInSolarSystemResponse\x12\'\n\x07planets\x18\x01 \x03(\x0b2\x16.eve.planet.Identifier*q\n\x07Surface\x12\x0b\n\x07UNKNOWN\x10\x00\x12\r\n\tTEMPERATE\x10\x01\x12\n\n\x06BARREN\x10\x02\x12\x0b\n\x07OCEANIC\x10\x03\x12\x07\n\x03ICE\x10\x04\x12\x07\n\x03GAS\x10\x05\x12\x08\n\x04LAVA\x10\x06\x12\t\n\x05STORM\x10\x07\x12\n\n\x06PLASMA\x10\x08B7Z5github.com/ccpgames/eve-proto-go/generated/eve/planetb\x06proto3', dependencies=[eve_dot_math_dot_vector__pb2.DESCRIPTOR, eve_dot_planet_dot_planet__type__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_SURFACE = _descriptor.EnumDescriptor(name='Surface', full_name='eve.planet.Surface', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNKNOWN', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TEMPERATE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='BARREN', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='OCEANIC', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ICE', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='GAS', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LAVA', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STORM', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PLASMA', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=721, serialized_end=834)
_sym_db.RegisterEnumDescriptor(_SURFACE)
Surface = enum_type_wrapper.EnumTypeWrapper(_SURFACE)
UNKNOWN = 0
TEMPERATE = 1
BARREN = 2
OCEANIC = 3
ICE = 4
GAS = 5
LAVA = 6
STORM = 7
PLASMA = 8
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.planet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.planet.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=127, serialized_end=159)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.planet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystem', full_name='eve.planet.Attributes.solarsystem', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='surface', full_name='eve.planet.Attributes.surface', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='name', full_name='eve.planet.Attributes.name', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='position', full_name='eve.planet.Attributes.position', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='type', full_name='eve.planet.Attributes.type', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=162, serialized_end=359)
_PLANET = _descriptor.Descriptor(name='Planet', full_name='eve.planet.Planet', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.planet.Planet.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.planet.Planet.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=361, serialized_end=449)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.planet.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='planet', full_name='eve.planet.GetRequest.planet', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=451, serialized_end=503)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.planet.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='planet', full_name='eve.planet.GetResponse.planet', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=505, serialized_end=558)
_GETPLANETSINSOLARSYSTEMREQUEST = _descriptor.Descriptor(name='GetPlanetsInSolarSystemRequest', full_name='eve.planet.GetPlanetsInSolarSystemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.planet.GetPlanetsInSolarSystemRequest.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=560, serialized_end=643)
_GETPLANETSINSOLARSYSTEMRESPONSE = _descriptor.Descriptor(name='GetPlanetsInSolarSystemResponse', full_name='eve.planet.GetPlanetsInSolarSystemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='planets', full_name='eve.planet.GetPlanetsInSolarSystemResponse.planets', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=645, serialized_end=719)
_ATTRIBUTES.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['surface'].enum_type = _SURFACE
_ATTRIBUTES.fields_by_name['position'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_ATTRIBUTES.fields_by_name['type'].message_type = eve_dot_planet_dot_planet__type__pb2._IDENTIFIER
_PLANET.fields_by_name['id'].message_type = _IDENTIFIER
_PLANET.fields_by_name['attributes'].message_type = _ATTRIBUTES
_GETREQUEST.fields_by_name['planet'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['planet'].message_type = _ATTRIBUTES
_GETPLANETSINSOLARSYSTEMREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETPLANETSINSOLARSYSTEMRESPONSE.fields_by_name['planets'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Planet'] = _PLANET
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetPlanetsInSolarSystemRequest'] = _GETPLANETSINSOLARSYSTEMREQUEST
DESCRIPTOR.message_types_by_name['GetPlanetsInSolarSystemResponse'] = _GETPLANETSINSOLARSYSTEMRESPONSE
DESCRIPTOR.enum_types_by_name['Surface'] = _SURFACE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(Attributes)
Planet = _reflection.GeneratedProtocolMessageType('Planet', (_message.Message,), {'DESCRIPTOR': _PLANET,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(Planet)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetPlanetsInSolarSystemRequest = _reflection.GeneratedProtocolMessageType('GetPlanetsInSolarSystemRequest', (_message.Message,), {'DESCRIPTOR': _GETPLANETSINSOLARSYSTEMREQUEST,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(GetPlanetsInSolarSystemRequest)
GetPlanetsInSolarSystemResponse = _reflection.GeneratedProtocolMessageType('GetPlanetsInSolarSystemResponse', (_message.Message,), {'DESCRIPTOR': _GETPLANETSINSOLARSYSTEMRESPONSE,
 '__module__': 'eve.planet.planet_pb2'})
_sym_db.RegisterMessage(GetPlanetsInSolarSystemResponse)
DESCRIPTOR._options = None
_ATTRIBUTES.fields_by_name['surface']._options = None
