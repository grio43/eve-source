#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\job\status_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/job/status.proto', package='eve.industry.job.status', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/industry/job/status', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/industry/job/status.proto\x12\x17eve.industry.job.status\x1a\x1deve/character/character.proto\x1a\x1fgoogle/protobuf/timestamp.proto"n\n\x14CompletedDateAndChar\x12(\n\x04date\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.Identifier*h\n\x06Status\x12\x0f\n\x0bUNSUBMITTED\x10\x00\x12\n\n\x06ACTIVE\x10\x01\x12\n\n\x06PAUSED\x10\x02\x12\t\n\x05READY\x10\x03\x12\r\n\tDELIVERED\x10e\x12\r\n\tCANCELLED\x10f\x12\x0c\n\x08REVERTED\x10gBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/industry/job/statusb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_STATUS = _descriptor.EnumDescriptor(name='Status', full_name='eve.industry.job.status.Status', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNSUBMITTED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACTIVE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PAUSED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='READY', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DELIVERED', index=4, number=101, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CANCELLED', index=5, number=102, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='REVERTED', index=6, number=103, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=234, serialized_end=338)
_sym_db.RegisterEnumDescriptor(_STATUS)
Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
UNSUBMITTED = 0
ACTIVE = 1
PAUSED = 2
READY = 3
DELIVERED = 101
CANCELLED = 102
REVERTED = 103
_COMPLETEDDATEANDCHAR = _descriptor.Descriptor(name='CompletedDateAndChar', full_name='eve.industry.job.status.CompletedDateAndChar', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='date', full_name='eve.industry.job.status.CompletedDateAndChar.date', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.industry.job.status.CompletedDateAndChar.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=232)
_COMPLETEDDATEANDCHAR.fields_by_name['date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_COMPLETEDDATEANDCHAR.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CompletedDateAndChar'] = _COMPLETEDDATEANDCHAR
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CompletedDateAndChar = _reflection.GeneratedProtocolMessageType('CompletedDateAndChar', (_message.Message,), {'DESCRIPTOR': _COMPLETEDDATEANDCHAR,
 '__module__': 'eve.industry.job.status_pb2'})
_sym_db.RegisterMessage(CompletedDateAndChar)
DESCRIPTOR._options = None
