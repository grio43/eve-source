#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\notification\notification_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.notification import sender_pb2 as eve_dot_notification_dot_sender__pb2
from eveProto.generated.eve.notification import type_pb2 as eve_dot_notification_dot_type__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/notification/notification.proto', package='eve.notification', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/notification', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/notification/notification.proto\x12\x10eve.notification\x1a\x1deve/notification/sender.proto\x1a\x1beve/notification/type.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xc0\x01\n\nAttributes\x12.\n\x04type\x18\x01 \x01(\x0b2 .eve.notificationtype.Identifier\x123\n\x06sender\x18\x02 \x01(\x0b2#.eve.notification.sender.Identifier\x12-\n\ttimestamp\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x10\n\x08was_read\x18\x04 \x01(\x08\x12\x0c\n\x04data\x18\x05 \x01(\tB=Z;github.com/ccpgames/eve-proto-go/generated/eve/notificationb\x06proto3', dependencies=[eve_dot_notification_dot_sender__pb2.DESCRIPTOR, eve_dot_notification_dot_type__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.notification.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.notification.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=182)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.notification.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.notification.Attributes.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sender', full_name='eve.notification.Attributes.sender', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='timestamp', full_name='eve.notification.Attributes.timestamp', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='was_read', full_name='eve.notification.Attributes.was_read', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='data', full_name='eve.notification.Attributes.data', index=4, number=5, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=185, serialized_end=377)
_ATTRIBUTES.fields_by_name['type'].message_type = eve_dot_notification_dot_type__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['sender'].message_type = eve_dot_notification_dot_sender__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.notification.notification_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.notification.notification_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
