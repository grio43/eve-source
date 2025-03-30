#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\search_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/search.proto', package='eve', syntax='proto3', serialized_options='Z.github.com/ccpgames/eve-proto-go/generated/eve', create_key=_descriptor._internal_create_key, serialized_pb='\n\x10eve/search.proto\x12\x03eve"\x83\x01\n\nSearchMode\x12\x1e\n\x14keywords_as_prefixes\x18\x01 \x01(\x08H\x00\x12\x18\n\x0eexact_keywords\x18\x02 \x01(\x08H\x00\x12\x16\n\x0cexact_phrase\x18\x03 \x01(\x08H\x00\x12\x1b\n\x11exact_phrase_only\x18\x04 \x01(\x08H\x00B\x06\n\x04mode">\n\x0bSearchQuery\x12\x10\n\x08keywords\x18\x01 \x03(\t\x12\x1d\n\x04mode\x18\x02 \x01(\x0b2\x0f.eve.SearchModeB0Z.github.com/ccpgames/eve-proto-go/generated/eveb\x06proto3')
_SEARCHMODE = _descriptor.Descriptor(name='SearchMode', full_name='eve.SearchMode', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='keywords_as_prefixes', full_name='eve.SearchMode.keywords_as_prefixes', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exact_keywords', full_name='eve.SearchMode.exact_keywords', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exact_phrase', full_name='eve.SearchMode.exact_phrase', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='exact_phrase_only', full_name='eve.SearchMode.exact_phrase_only', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='mode', full_name='eve.SearchMode.mode', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=26, serialized_end=157)
_SEARCHQUERY = _descriptor.Descriptor(name='SearchQuery', full_name='eve.SearchQuery', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='keywords', full_name='eve.SearchQuery.keywords', index=0, number=1, type=9, cpp_type=9, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='mode', full_name='eve.SearchQuery.mode', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=159, serialized_end=221)
_SEARCHMODE.oneofs_by_name['mode'].fields.append(_SEARCHMODE.fields_by_name['keywords_as_prefixes'])
_SEARCHMODE.fields_by_name['keywords_as_prefixes'].containing_oneof = _SEARCHMODE.oneofs_by_name['mode']
_SEARCHMODE.oneofs_by_name['mode'].fields.append(_SEARCHMODE.fields_by_name['exact_keywords'])
_SEARCHMODE.fields_by_name['exact_keywords'].containing_oneof = _SEARCHMODE.oneofs_by_name['mode']
_SEARCHMODE.oneofs_by_name['mode'].fields.append(_SEARCHMODE.fields_by_name['exact_phrase'])
_SEARCHMODE.fields_by_name['exact_phrase'].containing_oneof = _SEARCHMODE.oneofs_by_name['mode']
_SEARCHMODE.oneofs_by_name['mode'].fields.append(_SEARCHMODE.fields_by_name['exact_phrase_only'])
_SEARCHMODE.fields_by_name['exact_phrase_only'].containing_oneof = _SEARCHMODE.oneofs_by_name['mode']
_SEARCHQUERY.fields_by_name['mode'].message_type = _SEARCHMODE
DESCRIPTOR.message_types_by_name['SearchMode'] = _SEARCHMODE
DESCRIPTOR.message_types_by_name['SearchQuery'] = _SEARCHQUERY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SearchMode = _reflection.GeneratedProtocolMessageType('SearchMode', (_message.Message,), {'DESCRIPTOR': _SEARCHMODE,
 '__module__': 'eve.search_pb2'})
_sym_db.RegisterMessage(SearchMode)
SearchQuery = _reflection.GeneratedProtocolMessageType('SearchQuery', (_message.Message,), {'DESCRIPTOR': _SEARCHQUERY,
 '__module__': 'eve.search_pb2'})
_sym_db.RegisterMessage(SearchQuery)
DESCRIPTOR._options = None
