#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\alliance\mail\mail_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.mail import mail_pb2 as eve_dot_mail_dot_mail__pb2
from eveProto.generated.eve.mail import status_pb2 as eve_dot_mail_dot_status__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/alliance/mail/mail.proto', package='eve.alliance.mail', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/alliance/mail', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/alliance/mail/mail.proto\x12\x11eve.alliance.mail\x1a\x1beve/alliance/alliance.proto\x1a\x13eve/mail/mail.proto\x1a\x15eve/mail/status.proto"\x9f\x01\n\x04Sent\x12 \n\x02id\x18\x01 \x01(\x0b2\x14.eve.mail.Identifier\x12*\n\x08receiver\x18\x02 \x01(\x0b2\x18.eve.alliance.Identifier\x12"\n\x04mail\x18\x03 \x01(\x0b2\x14.eve.mail.Attributes\x12%\n\x0bsent_status\x18\x04 \x03(\x0e2\x10.eve.mail.StatusB>Z<github.com/ccpgames/eve-proto-go/generated/eve/alliance/mailb\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR, eve_dot_mail_dot_mail__pb2.DESCRIPTOR, eve_dot_mail_dot_status__pb2.DESCRIPTOR])
_SENT = _descriptor.Descriptor(name='Sent', full_name='eve.alliance.mail.Sent', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.alliance.mail.Sent.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='receiver', full_name='eve.alliance.mail.Sent.receiver', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='mail', full_name='eve.alliance.mail.Sent.mail', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sent_status', full_name='eve.alliance.mail.Sent.sent_status', index=3, number=4, type=14, cpp_type=8, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=125, serialized_end=284)
_SENT.fields_by_name['id'].message_type = eve_dot_mail_dot_mail__pb2._IDENTIFIER
_SENT.fields_by_name['receiver'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_SENT.fields_by_name['mail'].message_type = eve_dot_mail_dot_mail__pb2._ATTRIBUTES
_SENT.fields_by_name['sent_status'].enum_type = eve_dot_mail_dot_status__pb2._STATUS
DESCRIPTOR.message_types_by_name['Sent'] = _SENT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Sent = _reflection.GeneratedProtocolMessageType('Sent', (_message.Message,), {'DESCRIPTOR': _SENT,
 '__module__': 'eve.alliance.mail.mail_pb2'})
_sym_db.RegisterMessage(Sent)
DESCRIPTOR._options = None
