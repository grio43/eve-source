#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\faction\faction_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.race import race_pb2 as eve_dot_race_dot_race__pb2
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/faction/faction.proto', package='eve.faction', syntax='proto3', serialized_options='Z6github.com/ccpgames/eve-proto-go/generated/eve/faction', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/faction/faction.proto\x12\x0beve.faction\x1a\x13eve/race/race.proto\x1a\x10eve/search.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"P\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08icon_url\x18\x02 \x01(\t\x12"\n\x04race\x18\x03 \x01(\x0b2\x14.eve.race.Identifier"0\n\rSearchRequest\x12\x1f\n\x05query\x18\x01 \x01(\x0b2\x10.eve.SearchQuery";\n\x0eSearchResponse\x12)\n\x08factions\x18\x01 \x03(\x0b2\x17.eve.faction.IdentifierB8Z6github.com/ccpgames/eve-proto-go/generated/eve/factionb\x06proto3', dependencies=[eve_dot_race_dot_race__pb2.DESCRIPTOR, eve_dot_search__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.faction.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.faction.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=81, serialized_end=113)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.faction.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.faction.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='icon_url', full_name='eve.faction.Attributes.icon_url', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='race', full_name='eve.faction.Attributes.race', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=115, serialized_end=195)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.faction.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='query', full_name='eve.faction.SearchRequest.query', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=197, serialized_end=245)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.faction.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='factions', full_name='eve.faction.SearchResponse.factions', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=247, serialized_end=306)
_ATTRIBUTES.fields_by_name['race'].message_type = eve_dot_race_dot_race__pb2._IDENTIFIER
_SEARCHREQUEST.fields_by_name['query'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['factions'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.faction.faction_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.faction.faction_pb2'})
_sym_db.RegisterMessage(Attributes)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.faction.faction_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.faction.faction_pb2'})
_sym_db.RegisterMessage(SearchResponse)
DESCRIPTOR._options = None
