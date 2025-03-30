#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\note_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/note.proto', package='eve.user.note', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/user/note', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/user/note.proto\x12\reve.user.note\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x11"\x96\x01\n\nAttributes\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12%\n\x07subject\x18\x02 \x01(\x0b2\x14.eve.user.Identifier\x12$\n\x06author\x18\x03 \x01(\x0b2\x14.eve.user.Identifier\x12\x0c\n\x04text\x18\x04 \x01(\t"g\n\nAddRequest\x12%\n\x07subject\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12$\n\x06author\x18\x02 \x01(\x0b2\x14.eve.user.Identifier\x12\x0c\n\x04text\x18\x03 \x01(\t"\r\n\x0bAddResponseB:Z8github.com/ccpgames/eve-proto-go/generated/eve/user/noteb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.user.note.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.user.note.Identifier.sequential', index=0, number=1, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=92, serialized_end=124)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.user.note.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='timestamp', full_name='eve.user.note.Attributes.timestamp', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='subject', full_name='eve.user.note.Attributes.subject', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='author', full_name='eve.user.note.Attributes.author', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='text', full_name='eve.user.note.Attributes.text', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=127, serialized_end=277)
_ADDREQUEST = _descriptor.Descriptor(name='AddRequest', full_name='eve.user.note.AddRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='subject', full_name='eve.user.note.AddRequest.subject', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='author', full_name='eve.user.note.AddRequest.author', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='text', full_name='eve.user.note.AddRequest.text', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=279, serialized_end=382)
_ADDRESPONSE = _descriptor.Descriptor(name='AddResponse', full_name='eve.user.note.AddResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=384, serialized_end=397)
_ATTRIBUTES.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['subject'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['author'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ADDREQUEST.fields_by_name['subject'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ADDREQUEST.fields_by_name['author'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['AddRequest'] = _ADDREQUEST
DESCRIPTOR.message_types_by_name['AddResponse'] = _ADDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.user.note_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.user.note_pb2'})
_sym_db.RegisterMessage(Attributes)
AddRequest = _reflection.GeneratedProtocolMessageType('AddRequest', (_message.Message,), {'DESCRIPTOR': _ADDREQUEST,
 '__module__': 'eve.user.note_pb2'})
_sym_db.RegisterMessage(AddRequest)
AddResponse = _reflection.GeneratedProtocolMessageType('AddResponse', (_message.Message,), {'DESCRIPTOR': _ADDRESPONSE,
 '__module__': 'eve.user.note_pb2'})
_sym_db.RegisterMessage(AddResponse)
DESCRIPTOR._options = None
