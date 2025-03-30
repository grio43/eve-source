#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\thirdpartyapi\events_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/thirdpartyapi/events.proto', package='eve.thirdpartyapi', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/thirdpartyapi', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/thirdpartyapi/events.proto\x12\x11eve.thirdpartyapi\x1a\x1fgoogle/protobuf/timestamp.proto"\xda\x01\n\x0fRequestReceived\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x14\n\x0ccharacter_id\x18\x02 \x01(\x05\x12\x12\n\ndatasource\x18\x03 \x01(\t\x12\x1a\n\x12origin_fingerprint\x18\x04 \x01(\x0c\x12\r\n\x05route\x18\x05 \x01(\t\x12/\n\thttp_verb\x18\x06 \x01(\x0e2\x1c.eve.thirdpartyapi.HTTPVerbs\x12\x12\n\nuser_agent\x18\x07 \x01(\t*W\n\tHTTPVerbs\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x07\n\x03GET\x10\x01\x12\x08\n\x04HEAD\x10\x02\x12\x08\n\x04POST\x10\x03\x12\x07\n\x03PUT\x10\x04\x12\n\n\x06DELETE\x10\x05\x12\x0b\n\x07OPTIONS\x10\x06B>Z<github.com/ccpgames/eve-proto-go/generated/eve/thirdpartyapib\x06proto3', dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_HTTPVERBS = _descriptor.EnumDescriptor(name='HTTPVerbs', full_name='eve.thirdpartyapi.HTTPVerbs', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNKNOWN', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='GET', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='HEAD', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='POST', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PUT', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DELETE', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='OPTIONS', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=307, serialized_end=394)
_sym_db.RegisterEnumDescriptor(_HTTPVERBS)
HTTPVerbs = enum_type_wrapper.EnumTypeWrapper(_HTTPVERBS)
UNKNOWN = 0
GET = 1
HEAD = 2
POST = 3
PUT = 4
DELETE = 5
OPTIONS = 6
_REQUESTRECEIVED = _descriptor.Descriptor(name='RequestReceived', full_name='eve.thirdpartyapi.RequestReceived', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='timestamp', full_name='eve.thirdpartyapi.RequestReceived.timestamp', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character_id', full_name='eve.thirdpartyapi.RequestReceived.character_id', index=1, number=2, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='datasource', full_name='eve.thirdpartyapi.RequestReceived.datasource', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='origin_fingerprint', full_name='eve.thirdpartyapi.RequestReceived.origin_fingerprint', index=3, number=4, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='route', full_name='eve.thirdpartyapi.RequestReceived.route', index=4, number=5, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='http_verb', full_name='eve.thirdpartyapi.RequestReceived.http_verb', index=5, number=6, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user_agent', full_name='eve.thirdpartyapi.RequestReceived.user_agent', index=6, number=7, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=87, serialized_end=305)
_REQUESTRECEIVED.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_REQUESTRECEIVED.fields_by_name['http_verb'].enum_type = _HTTPVERBS
DESCRIPTOR.message_types_by_name['RequestReceived'] = _REQUESTRECEIVED
DESCRIPTOR.enum_types_by_name['HTTPVerbs'] = _HTTPVERBS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
RequestReceived = _reflection.GeneratedProtocolMessageType('RequestReceived', (_message.Message,), {'DESCRIPTOR': _REQUESTRECEIVED,
 '__module__': 'eve.thirdpartyapi.events_pb2'})
_sym_db.RegisterMessage(RequestReceived)
DESCRIPTOR._options = None
