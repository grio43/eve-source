#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\constellation\constellation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.math import vector_pb2 as eve_dot_math_dot_vector__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/constellation/constellation.proto', package='eve.constellation', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/constellation', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/constellation/constellation.proto\x12\x11eve.constellation\x1a\x15eve/math/vector.proto\x1a\x17eve/region/region.proto\x1a\x10eve/search.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"g\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12&\n\x06region\x18\x02 \x01(\x0b2\x16.eve.region.Identifier\x12#\n\x08position\x18\x03 \x01(\x0b2\x11.eve.math.Vector3"B\n\nGetRequest\x124\n\rconstellation\x18\x01 \x01(\x0b2\x1d.eve.constellation.Identifier"@\n\x0bGetResponse\x121\n\nattributes\x18\x01 \x01(\x0b2\x1d.eve.constellation.Attributes"\x0f\n\rGetAllRequest"G\n\x0eGetAllResponse\x125\n\x0econstellations\x18\x01 \x03(\x0b2\x1d.eve.constellation.Identifier"0\n\rSearchRequest\x12\x1f\n\x05query\x18\x01 \x01(\x0b2\x10.eve.SearchQuery"G\n\x0eSearchResponse\x125\n\x0econstellations\x18\x01 \x03(\x0b2\x1d.eve.constellation.IdentifierB>Z<github.com/ccpgames/eve-proto-go/generated/eve/constellationb\x06proto3', dependencies=[eve_dot_math_dot_vector__pb2.DESCRIPTOR, eve_dot_region_dot_region__pb2.DESCRIPTOR, eve_dot_search__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.constellation.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.constellation.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=158)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.constellation.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.constellation.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='region', full_name='eve.constellation.Attributes.region', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='position', full_name='eve.constellation.Attributes.position', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=160, serialized_end=263)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.constellation.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='constellation', full_name='eve.constellation.GetRequest.constellation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=265, serialized_end=331)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.constellation.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.constellation.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=333, serialized_end=397)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.constellation.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=399, serialized_end=414)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.constellation.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='constellations', full_name='eve.constellation.GetAllResponse.constellations', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=416, serialized_end=487)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.constellation.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='query', full_name='eve.constellation.SearchRequest.query', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=489, serialized_end=537)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.constellation.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='constellations', full_name='eve.constellation.SearchResponse.constellations', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=539, serialized_end=610)
_ATTRIBUTES.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['position'].message_type = eve_dot_math_dot_vector__pb2._VECTOR3
_GETREQUEST.fields_by_name['constellation'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = _ATTRIBUTES
_GETALLRESPONSE.fields_by_name['constellations'].message_type = _IDENTIFIER
_SEARCHREQUEST.fields_by_name['query'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['constellations'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.constellation.constellation_pb2'})
_sym_db.RegisterMessage(SearchResponse)
DESCRIPTOR._options = None
