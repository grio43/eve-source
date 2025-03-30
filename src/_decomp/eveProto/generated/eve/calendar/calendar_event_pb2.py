#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\calendar\calendar_event_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/calendar/calendar_event.proto', package='eve.calendar.calendar_event', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/calendar', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/calendar/calendar_event.proto\x12\x1beve.calendar.calendar_event" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x05*"\n\nImportance\x12\n\n\x06Normal\x10\x00\x12\x08\n\x04High\x10\x01B9Z7github.com/ccpgames/eve-proto-go/generated/eve/calendarb\x06proto3')
_IMPORTANCE = _descriptor.EnumDescriptor(name='Importance', full_name='eve.calendar.calendar_event.Importance', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='Normal', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='High', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=100, serialized_end=134)
_sym_db.RegisterEnumDescriptor(_IMPORTANCE)
Importance = enum_type_wrapper.EnumTypeWrapper(_IMPORTANCE)
Normal = 0
High = 1
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.calendar.calendar_event.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.calendar.calendar_event.Identifier.sequential', index=0, number=1, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=66, serialized_end=98)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.enum_types_by_name['Importance'] = _IMPORTANCE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.calendar.calendar_event_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
