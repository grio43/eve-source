#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mail\body_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.mail import mail_pb2 as eve_dot_mail_dot_mail__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mail/body.proto', package='eve.mail.body', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/mail/body', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/mail/body.proto\x12\reve.mail.body\x1a\x13eve/mail/mail.proto"3\n\nIdentifier\x12%\n\x07mail_id\x18\x01 \x01(\x0b2\x14.eve.mail.Identifier"\x1a\n\nAttributes\x12\x0c\n\x04text\x18\x01 \x01(\tB:Z8github.com/ccpgames/eve-proto-go/generated/eve/mail/bodyb\x06proto3', dependencies=[eve_dot_mail_dot_mail__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.mail.body.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='mail_id', full_name='eve.mail.body.Identifier.mail_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=59, serialized_end=110)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.mail.body.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='text', full_name='eve.mail.body.Attributes.text', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=112, serialized_end=138)
_IDENTIFIER.fields_by_name['mail_id'].message_type = eve_dot_mail_dot_mail__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.mail.body_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.mail.body_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
