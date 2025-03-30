#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\notification\contact_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.notification import sender_pb2 as eve_dot_notification_dot_sender__pb2
from eveProto.generated.eve.standing import standing_pb2 as eve_dot_standing_dot_standing__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/notification/contact.proto', package='eve.notification.contact', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/notification/contact', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/notification/contact.proto\x12\x18eve.notification.contact\x1a\x1deve/notification/sender.proto\x1a\x1beve/standing/standing.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xa8\x01\n\nAttributes\x123\n\x06sender\x18\x01 \x01(\x0b2#.eve.notification.sender.Identifier\x12-\n\ttimestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12%\n\x08standing\x18\x03 \x01(\x0b2\x13.eve.standing.Value\x12\x0f\n\x07message\x18\x04 \x01(\tBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/notification/contactb\x06proto3', dependencies=[eve_dot_notification_dot_sender__pb2.DESCRIPTOR, eve_dot_standing_dot_standing__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.notification.contact.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sender', full_name='eve.notification.contact.Attributes.sender', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='timestamp', full_name='eve.notification.contact.Attributes.timestamp', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='standing', full_name='eve.notification.contact.Attributes.standing', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='message', full_name='eve.notification.contact.Attributes.message', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=154, serialized_end=322)
_ATTRIBUTES.fields_by_name['sender'].message_type = eve_dot_notification_dot_sender__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['standing'].message_type = eve_dot_standing_dot_standing__pb2._VALUE
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.notification.contact_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
