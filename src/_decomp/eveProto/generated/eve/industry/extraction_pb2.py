#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\extraction_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/extraction.proto', package='eve.industry.extraction', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/industry/extraction', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/industry/extraction.proto\x12\x17eve.industry.extraction\x1a\x1deve/structure/structure.proto\x1a\x1fgoogle/protobuf/timestamp.proto":\n\nIdentifier\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier"\xb7\x01\n\nAttributes\x129\n\x15extraction_start_time\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x126\n\x12chunk_arrival_time\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x126\n\x12natural_decay_time\x18\x03 \x01(\x0b2\x1a.google.protobuf.TimestampBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/industry/extractionb\x06proto3', dependencies=[eve_dot_structure_dot_structure__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.industry.extraction.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.industry.extraction.Identifier.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=180)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.industry.extraction.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='extraction_start_time', full_name='eve.industry.extraction.Attributes.extraction_start_time', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='chunk_arrival_time', full_name='eve.industry.extraction.Attributes.chunk_arrival_time', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='natural_decay_time', full_name='eve.industry.extraction.Attributes.natural_decay_time', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=183, serialized_end=366)
_IDENTIFIER.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['extraction_start_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['chunk_arrival_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['natural_decay_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.industry.extraction_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.industry.extraction_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
