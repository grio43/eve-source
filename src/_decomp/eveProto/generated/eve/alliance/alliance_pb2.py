#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\alliance\alliance_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.race import race_pb2 as eve_dot_race_dot_race__pb2
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/alliance/alliance.proto', package='eve.alliance', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/alliance', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/alliance/alliance.proto\x12\x0ceve.alliance\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x13eve/race/race.proto\x1a\x10eve/search.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x05"\xe4\x02\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nshort_name\x18\x02 \x01(\t\x120\n\x0cdate_founded\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x127\n\x14creator_character_id\x18\x04 \x01(\x0b2\x19.eve.character.Identifier\x12;\n\x16creator_corporation_id\x18\x05 \x01(\x0b2\x1b.eve.corporation.Identifier\x12>\n\x17executor_corporation_id\x18\x06 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12!\n\x17no_executor_corporation\x18\x08 \x01(\x08H\x00\x12\x0b\n\x03url\x18\t \x01(\tB\x16\n\x14executor_corporationJ\x04\x08\x07\x10\x08";\n\nGetRequest\x12-\n\x0balliance_id\x18\x01 \x01(\x0b2\x18.eve.alliance.Identifier"9\n\x0bGetResponse\x12*\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.Attributes"\x0f\n\rGetAllRequest"@\n\x0eGetAllResponse\x12.\n\x0calliance_ids\x18\x01 \x03(\x0b2\x18.eve.alliance.Identifier"0\n\rSearchRequest\x12\x1f\n\x05query\x18\x01 \x01(\x0b2\x10.eve.SearchQuery"=\n\x0eSearchResponse\x12+\n\talliances\x18\x01 \x03(\x0b2\x18.eve.alliance.Identifier"6\n\x10GetByRaceRequest\x12"\n\x04race\x18\x01 \x01(\x0b2\x14.eve.race.Identifier"?\n\x11GetByRaceResponse\x12*\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/allianceb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_race_dot_race__pb2.DESCRIPTOR,
 eve_dot_search__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.alliance.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.alliance.Identifier.sequential', index=0, number=1, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=183, serialized_end=215)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.alliance.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.alliance.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='short_name', full_name='eve.alliance.Attributes.short_name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='date_founded', full_name='eve.alliance.Attributes.date_founded', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='creator_character_id', full_name='eve.alliance.Attributes.creator_character_id', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='creator_corporation_id', full_name='eve.alliance.Attributes.creator_corporation_id', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='executor_corporation_id', full_name='eve.alliance.Attributes.executor_corporation_id', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_executor_corporation', full_name='eve.alliance.Attributes.no_executor_corporation', index=6, number=8, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='url', full_name='eve.alliance.Attributes.url', index=7, number=9, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='executor_corporation', full_name='eve.alliance.Attributes.executor_corporation', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=218, serialized_end=574)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.alliance.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance_id', full_name='eve.alliance.GetRequest.alliance_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=576, serialized_end=635)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.alliance.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.alliance.GetResponse.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=637, serialized_end=694)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.alliance.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=696, serialized_end=711)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.alliance.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance_ids', full_name='eve.alliance.GetAllResponse.alliance_ids', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=713, serialized_end=777)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.alliance.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='query', full_name='eve.alliance.SearchRequest.query', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=779, serialized_end=827)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.alliance.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliances', full_name='eve.alliance.SearchResponse.alliances', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=829, serialized_end=890)
_GETBYRACEREQUEST = _descriptor.Descriptor(name='GetByRaceRequest', full_name='eve.alliance.GetByRaceRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='race', full_name='eve.alliance.GetByRaceRequest.race', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=892, serialized_end=946)
_GETBYRACERESPONSE = _descriptor.Descriptor(name='GetByRaceResponse', full_name='eve.alliance.GetByRaceResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.alliance.GetByRaceResponse.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=948, serialized_end=1011)
_ATTRIBUTES.fields_by_name['date_founded'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['creator_character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['creator_corporation_id'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['executor_corporation_id'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ATTRIBUTES.oneofs_by_name['executor_corporation'].fields.append(_ATTRIBUTES.fields_by_name['executor_corporation_id'])
_ATTRIBUTES.fields_by_name['executor_corporation_id'].containing_oneof = _ATTRIBUTES.oneofs_by_name['executor_corporation']
_ATTRIBUTES.oneofs_by_name['executor_corporation'].fields.append(_ATTRIBUTES.fields_by_name['no_executor_corporation'])
_ATTRIBUTES.fields_by_name['no_executor_corporation'].containing_oneof = _ATTRIBUTES.oneofs_by_name['executor_corporation']
_GETREQUEST.fields_by_name['alliance_id'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['alliance'].message_type = _ATTRIBUTES
_GETALLRESPONSE.fields_by_name['alliance_ids'].message_type = _IDENTIFIER
_SEARCHREQUEST.fields_by_name['query'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['alliances'].message_type = _IDENTIFIER
_GETBYRACEREQUEST.fields_by_name['race'].message_type = eve_dot_race_dot_race__pb2._IDENTIFIER
_GETBYRACERESPONSE.fields_by_name['alliance'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
DESCRIPTOR.message_types_by_name['GetByRaceRequest'] = _GETBYRACEREQUEST
DESCRIPTOR.message_types_by_name['GetByRaceResponse'] = _GETBYRACERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(SearchResponse)
GetByRaceRequest = _reflection.GeneratedProtocolMessageType('GetByRaceRequest', (_message.Message,), {'DESCRIPTOR': _GETBYRACEREQUEST,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetByRaceRequest)
GetByRaceResponse = _reflection.GeneratedProtocolMessageType('GetByRaceResponse', (_message.Message,), {'DESCRIPTOR': _GETBYRACERESPONSE,
 '__module__': 'eve.alliance.alliance_pb2'})
_sym_db.RegisterMessage(GetByRaceResponse)
DESCRIPTOR._options = None
