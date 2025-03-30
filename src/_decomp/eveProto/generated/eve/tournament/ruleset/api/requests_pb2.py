#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\tournament\ruleset\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
from eveProto.generated.eve.tournament.ruleset import ruleset_pb2 as eve_dot_tournament_dot_ruleset_dot_ruleset__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/tournament/ruleset/api/requests.proto', package='eve.tournament.ruleset.api', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/tournament/ruleset/api', create_key=_descriptor._internal_create_key, serialized_pb='\n)eve/tournament/ruleset/api/requests.proto\x12\x1aeve.tournament.ruleset.api\x1a\x10eve/search.proto\x1a$eve/tournament/ruleset/ruleset.proto"A\n\nGetRequest\x123\n\x07ruleset\x18\x01 \x01(\x0b2".eve.tournament.ruleset.Identifier"B\n\x0bGetResponse\x123\n\x07ruleset\x18\x01 \x01(\x0b2".eve.tournament.ruleset.Attributes"\x0f\n\rGetAllRequest"F\n\x0eGetAllResponse\x124\n\x08rulesets\x18\x01 \x03(\x0b2".eve.tournament.ruleset.Identifier"1\n\rSearchRequest\x12 \n\x06search\x18\x01 \x01(\x0b2\x10.eve.SearchQuery"F\n\x0eSearchResponse\x124\n\x08rulesets\x18\x01 \x03(\x0b2".eve.tournament.ruleset.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/tournament/ruleset/apib\x06proto3', dependencies=[eve_dot_search__pb2.DESCRIPTOR, eve_dot_tournament_dot_ruleset_dot_ruleset__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.tournament.ruleset.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ruleset', full_name='eve.tournament.ruleset.api.GetRequest.ruleset', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=129, serialized_end=194)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.tournament.ruleset.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ruleset', full_name='eve.tournament.ruleset.api.GetResponse.ruleset', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=196, serialized_end=262)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.tournament.ruleset.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=264, serialized_end=279)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.tournament.ruleset.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='rulesets', full_name='eve.tournament.ruleset.api.GetAllResponse.rulesets', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=281, serialized_end=351)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.tournament.ruleset.api.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='search', full_name='eve.tournament.ruleset.api.SearchRequest.search', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=353, serialized_end=402)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.tournament.ruleset.api.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='rulesets', full_name='eve.tournament.ruleset.api.SearchResponse.rulesets', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=404, serialized_end=474)
_GETREQUEST.fields_by_name['ruleset'].message_type = eve_dot_tournament_dot_ruleset_dot_ruleset__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['ruleset'].message_type = eve_dot_tournament_dot_ruleset_dot_ruleset__pb2._ATTRIBUTES
_GETALLRESPONSE.fields_by_name['rulesets'].message_type = eve_dot_tournament_dot_ruleset_dot_ruleset__pb2._IDENTIFIER
_SEARCHREQUEST.fields_by_name['search'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['rulesets'].message_type = eve_dot_tournament_dot_ruleset_dot_ruleset__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.tournament.ruleset.api.requests_pb2'})
_sym_db.RegisterMessage(SearchResponse)
DESCRIPTOR._options = None
