#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\mail\mail_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.mail import list_pb2 as eve_dot_mail_dot_list__pb2
from eveProto.generated.eve.mail import status_pb2 as eve_dot_mail_dot_status__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/mail/mail.proto', package='eve.mail', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/mail', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/mail/mail.proto\x12\x08eve.mail\x1a\x1beve/alliance/alliance.proto\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x13eve/mail/list.proto\x1a\x15eve/mail/status.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xcf\x01\n\nRecipients\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12,\n\x08alliance\x18\x03 \x01(\x0b2\x18.eve.alliance.IdentifierH\x00\x12)\n\x04list\x18\x04 \x01(\x0b2\x19.eve.mail.list.IdentifierH\x00B\x04\n\x02id" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xa5\x01\n\nAttributes\x12)\n\x06sender\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12\r\n\x05title\x18\x02 \x01(\t\x12-\n\tsent_date\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12(\n\nrecipients\x18\x05 \x03(\x0b2\x14.eve.mail.RecipientsJ\x04\x08\x04\x10\x05"\xc8\x01\n\x12CCPSendMailRequest\x123\n\x10sender_character\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x127\n\x14recipient_characters\x18\x02 \x03(\x0b2\x19.eve.character.Identifier\x12\x0f\n\x07subject\x18\x03 \x01(\t\x12\x0c\n\x04body\x18\x04 \x01(\t\x12%\n\x0bstatus_mask\x18\x05 \x03(\x0e2\x10.eve.mail.Status"k\n\x13CCPSendMailResponse\x12\'\n\tsuccesses\x18\x01 \x03(\x0b2\x14.eve.mail.Identifier\x12+\n\x08failures\x18\x02 \x03(\x0b2\x19.eve.character.IdentifierB5Z3github.com/ccpgames/eve-proto-go/generated/eve/mailb\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_mail_dot_list__pb2.DESCRIPTOR,
 eve_dot_mail_dot_status__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_RECIPIENTS = _descriptor.Descriptor(name='Recipients', full_name='eve.mail.Recipients', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.mail.Recipients.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.mail.Recipients.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='alliance', full_name='eve.mail.Recipients.alliance', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='list', full_name='eve.mail.Recipients.list', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='id', full_name='eve.mail.Recipients.id', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=206, serialized_end=413)
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.mail.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.mail.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=415, serialized_end=447)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.mail.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sender', full_name='eve.mail.Attributes.sender', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='title', full_name='eve.mail.Attributes.title', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sent_date', full_name='eve.mail.Attributes.sent_date', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recipients', full_name='eve.mail.Attributes.recipients', index=3, number=5, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=450, serialized_end=615)
_CCPSENDMAILREQUEST = _descriptor.Descriptor(name='CCPSendMailRequest', full_name='eve.mail.CCPSendMailRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sender_character', full_name='eve.mail.CCPSendMailRequest.sender_character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recipient_characters', full_name='eve.mail.CCPSendMailRequest.recipient_characters', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='subject', full_name='eve.mail.CCPSendMailRequest.subject', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='body', full_name='eve.mail.CCPSendMailRequest.body', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='status_mask', full_name='eve.mail.CCPSendMailRequest.status_mask', index=4, number=5, type=14, cpp_type=8, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=618, serialized_end=818)
_CCPSENDMAILRESPONSE = _descriptor.Descriptor(name='CCPSendMailResponse', full_name='eve.mail.CCPSendMailResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='successes', full_name='eve.mail.CCPSendMailResponse.successes', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='failures', full_name='eve.mail.CCPSendMailResponse.failures', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=820, serialized_end=927)
_RECIPIENTS.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_RECIPIENTS.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_RECIPIENTS.fields_by_name['alliance'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_RECIPIENTS.fields_by_name['list'].message_type = eve_dot_mail_dot_list__pb2._IDENTIFIER
_RECIPIENTS.oneofs_by_name['id'].fields.append(_RECIPIENTS.fields_by_name['character'])
_RECIPIENTS.fields_by_name['character'].containing_oneof = _RECIPIENTS.oneofs_by_name['id']
_RECIPIENTS.oneofs_by_name['id'].fields.append(_RECIPIENTS.fields_by_name['corporation'])
_RECIPIENTS.fields_by_name['corporation'].containing_oneof = _RECIPIENTS.oneofs_by_name['id']
_RECIPIENTS.oneofs_by_name['id'].fields.append(_RECIPIENTS.fields_by_name['alliance'])
_RECIPIENTS.fields_by_name['alliance'].containing_oneof = _RECIPIENTS.oneofs_by_name['id']
_RECIPIENTS.oneofs_by_name['id'].fields.append(_RECIPIENTS.fields_by_name['list'])
_RECIPIENTS.fields_by_name['list'].containing_oneof = _RECIPIENTS.oneofs_by_name['id']
_ATTRIBUTES.fields_by_name['sender'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['sent_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['recipients'].message_type = _RECIPIENTS
_CCPSENDMAILREQUEST.fields_by_name['sender_character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CCPSENDMAILREQUEST.fields_by_name['recipient_characters'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CCPSENDMAILREQUEST.fields_by_name['status_mask'].enum_type = eve_dot_mail_dot_status__pb2._STATUS
_CCPSENDMAILRESPONSE.fields_by_name['successes'].message_type = _IDENTIFIER
_CCPSENDMAILRESPONSE.fields_by_name['failures'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Recipients'] = _RECIPIENTS
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['CCPSendMailRequest'] = _CCPSENDMAILREQUEST
DESCRIPTOR.message_types_by_name['CCPSendMailResponse'] = _CCPSENDMAILRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Recipients = _reflection.GeneratedProtocolMessageType('Recipients', (_message.Message,), {'DESCRIPTOR': _RECIPIENTS,
 '__module__': 'eve.mail.mail_pb2'})
_sym_db.RegisterMessage(Recipients)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.mail.mail_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.mail.mail_pb2'})
_sym_db.RegisterMessage(Attributes)
CCPSendMailRequest = _reflection.GeneratedProtocolMessageType('CCPSendMailRequest', (_message.Message,), {'DESCRIPTOR': _CCPSENDMAILREQUEST,
 '__module__': 'eve.mail.mail_pb2'})
_sym_db.RegisterMessage(CCPSendMailRequest)
CCPSendMailResponse = _reflection.GeneratedProtocolMessageType('CCPSendMailResponse', (_message.Message,), {'DESCRIPTOR': _CCPSENDMAILRESPONSE,
 '__module__': 'eve.mail.mail_pb2'})
_sym_db.RegisterMessage(CCPSendMailResponse)
DESCRIPTOR._options = None
