#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\notification\sender_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/notification/sender.proto', package='eve.notification.sender', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/notification/sender', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/notification/sender.proto\x12\x17eve.notification.sender\x1a\x1beve/alliance/alliance.proto\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x19eve/faction/faction.proto"\xfd\x01\n\nIdentifier\x121\n\x0ccharacter_id\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x125\n\x0ecorporation_id\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12/\n\x0balliance_id\x18\x03 \x01(\x0b2\x18.eve.alliance.IdentifierH\x00\x12-\n\nfaction_id\x18\x04 \x01(\x0b2\x17.eve.faction.IdentifierH\x00\x12\x1b\n\x11unknown_sender_id\x18\x05 \x01(\rH\x00B\x08\n\x06senderBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/notification/senderb\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.notification.sender.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character_id', full_name='eve.notification.sender.Identifier.character_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation_id', full_name='eve.notification.sender.Identifier.corporation_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='alliance_id', full_name='eve.notification.sender.Identifier.alliance_id', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='faction_id', full_name='eve.notification.sender.Identifier.faction_id', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown_sender_id', full_name='eve.notification.sender.Identifier.unknown_sender_id', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='sender', full_name='eve.notification.sender.Identifier.sender', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=181, serialized_end=434)
_IDENTIFIER.fields_by_name['character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['corporation_id'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['alliance_id'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['sender'].fields.append(_IDENTIFIER.fields_by_name['character_id'])
_IDENTIFIER.fields_by_name['character_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['sender']
_IDENTIFIER.oneofs_by_name['sender'].fields.append(_IDENTIFIER.fields_by_name['corporation_id'])
_IDENTIFIER.fields_by_name['corporation_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['sender']
_IDENTIFIER.oneofs_by_name['sender'].fields.append(_IDENTIFIER.fields_by_name['alliance_id'])
_IDENTIFIER.fields_by_name['alliance_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['sender']
_IDENTIFIER.oneofs_by_name['sender'].fields.append(_IDENTIFIER.fields_by_name['faction_id'])
_IDENTIFIER.fields_by_name['faction_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['sender']
_IDENTIFIER.oneofs_by_name['sender'].fields.append(_IDENTIFIER.fields_by_name['unknown_sender_id'])
_IDENTIFIER.fields_by_name['unknown_sender_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['sender']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.notification.sender_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
