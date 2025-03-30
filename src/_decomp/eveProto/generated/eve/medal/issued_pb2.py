#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\medal\issued_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.medal import medal_pb2 as eve_dot_medal_dot_medal__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/medal/issued.proto', package='eve.medal.issued', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/medal/issued', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/medal/issued.proto\x12\x10eve.medal.issued\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x15eve/medal/medal.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xf4\x01\n\nAttributes\x125\n\x10issuer_character\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x129\n\x12issuer_corporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12-\n\tissued_at\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x0e\n\x06reason\x18\x04 \x01(\t\x12(\n\x06status\x18\x05 \x01(\x0e2\x18.eve.medal.issued.StatusB\x0b\n\tissuer_id"\xce\x02\n\x07Awarded\x12.\n\x05medal\x18\x01 \x01(\x0b2\x1f.eve.medal.issued.Awarded.Medal\x12-\n\nrecipients\x18\x02 \x03(\x0b2\x19.eve.character.Identifier\x125\n\x10issuer_character\x18\x03 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x129\n\x12issuer_corporation\x18\x04 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12\x0e\n\x06reason\x18\x05 \x01(\t\x1aU\n\x05Medal\x12!\n\x02id\x18\x01 \x01(\x0b2\x15.eve.medal.Identifier\x12)\n\nattributes\x18\x02 \x01(\x0b2\x15.eve.medal.AttributesB\x0b\n\tissuer_id*C\n\x06Status\x12\x12\n\x0eSTATUS_INVALID\x10\x00\x12\x11\n\rSTATUS_PUBLIC\x10\x01\x12\x12\n\x0eSTATUS_PRIVATE\x10\x02B=Z;github.com/ccpgames/eve-proto-go/generated/eve/medal/issuedb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_medal_dot_medal__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_STATUS = _descriptor.EnumDescriptor(name='Status', full_name='eve.medal.issued.Status', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='STATUS_INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='STATUS_PUBLIC', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='STATUS_PRIVATE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=750, serialized_end=817)
_sym_db.RegisterEnumDescriptor(_STATUS)
Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
STATUS_INVALID = 0
STATUS_PUBLIC = 1
STATUS_PRIVATE = 2
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.medal.issued.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='issuer_character', full_name='eve.medal.issued.Attributes.issuer_character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issuer_corporation', full_name='eve.medal.issued.Attributes.issuer_corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issued_at', full_name='eve.medal.issued.Attributes.issued_at', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reason', full_name='eve.medal.issued.Attributes.reason', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='status', full_name='eve.medal.issued.Attributes.status', index=4, number=5, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='issuer_id', full_name='eve.medal.issued.Attributes.issuer_id', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=167, serialized_end=411)
_AWARDED_MEDAL = _descriptor.Descriptor(name='Medal', full_name='eve.medal.issued.Awarded.Medal', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.medal.issued.Awarded.Medal.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.medal.issued.Awarded.Medal.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=650, serialized_end=735)
_AWARDED = _descriptor.Descriptor(name='Awarded', full_name='eve.medal.issued.Awarded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='medal', full_name='eve.medal.issued.Awarded.medal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recipients', full_name='eve.medal.issued.Awarded.recipients', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issuer_character', full_name='eve.medal.issued.Awarded.issuer_character', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issuer_corporation', full_name='eve.medal.issued.Awarded.issuer_corporation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reason', full_name='eve.medal.issued.Awarded.reason', index=4, number=5, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_AWARDED_MEDAL], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='issuer_id', full_name='eve.medal.issued.Awarded.issuer_id', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=414, serialized_end=748)
_ATTRIBUTES.fields_by_name['issuer_character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['issuer_corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['issued_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['status'].enum_type = _STATUS
_ATTRIBUTES.oneofs_by_name['issuer_id'].fields.append(_ATTRIBUTES.fields_by_name['issuer_character'])
_ATTRIBUTES.fields_by_name['issuer_character'].containing_oneof = _ATTRIBUTES.oneofs_by_name['issuer_id']
_ATTRIBUTES.oneofs_by_name['issuer_id'].fields.append(_ATTRIBUTES.fields_by_name['issuer_corporation'])
_ATTRIBUTES.fields_by_name['issuer_corporation'].containing_oneof = _ATTRIBUTES.oneofs_by_name['issuer_id']
_AWARDED_MEDAL.fields_by_name['id'].message_type = eve_dot_medal_dot_medal__pb2._IDENTIFIER
_AWARDED_MEDAL.fields_by_name['attributes'].message_type = eve_dot_medal_dot_medal__pb2._ATTRIBUTES
_AWARDED_MEDAL.containing_type = _AWARDED
_AWARDED.fields_by_name['medal'].message_type = _AWARDED_MEDAL
_AWARDED.fields_by_name['recipients'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_AWARDED.fields_by_name['issuer_character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_AWARDED.fields_by_name['issuer_corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_AWARDED.oneofs_by_name['issuer_id'].fields.append(_AWARDED.fields_by_name['issuer_character'])
_AWARDED.fields_by_name['issuer_character'].containing_oneof = _AWARDED.oneofs_by_name['issuer_id']
_AWARDED.oneofs_by_name['issuer_id'].fields.append(_AWARDED.fields_by_name['issuer_corporation'])
_AWARDED.fields_by_name['issuer_corporation'].containing_oneof = _AWARDED.oneofs_by_name['issuer_id']
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Awarded'] = _AWARDED
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.medal.issued_pb2'})
_sym_db.RegisterMessage(Attributes)
Awarded = _reflection.GeneratedProtocolMessageType('Awarded', (_message.Message,), {'Medal': _reflection.GeneratedProtocolMessageType('Medal', (_message.Message,), {'DESCRIPTOR': _AWARDED_MEDAL,
           '__module__': 'eve.medal.issued_pb2'}),
 'DESCRIPTOR': _AWARDED,
 '__module__': 'eve.medal.issued_pb2'})
_sym_db.RegisterMessage(Awarded)
_sym_db.RegisterMessage(Awarded.Medal)
DESCRIPTOR._options = None
