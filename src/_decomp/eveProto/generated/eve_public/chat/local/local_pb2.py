#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\chat\local\local_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.alliance import alliance_pb2 as eve__public_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve_public.character import character_pb2 as eve__public_dot_character_dot_character__pb2
from eveProto.generated.eve_public.corporation import corporation_pb2 as eve__public_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve_public.faction import faction_pb2 as eve__public_dot_faction_dot_faction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/chat/local/local.proto', package='eve_public.chat.local', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve_public/chat/local', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve_public/chat/local/local.proto\x12\x15eve_public.chat.local\x1a"eve_public/alliance/alliance.proto\x1a$eve_public/character/character.proto\x1a(eve_public/corporation/corporation.proto\x1a eve_public/faction/faction.proto"\xfa\x02\n\tCharacter\x123\n\tcharacter\x18\x01 \x01(\x0b2 .eve_public.character.Identifier\x127\n\x0bcorporation\x18\x02 \x01(\x0b2".eve_public.corporation.Identifier\x12\x15\n\x0bno_alliance\x18\x03 \x01(\x08H\x00\x123\n\x08alliance\x18\x04 \x01(\x0b2\x1f.eve_public.alliance.IdentifierH\x00\x12\x14\n\nno_faction\x18\x05 \x01(\x08H\x01\x121\n\x07faction\x18\x06 \x01(\x0b2\x1e.eve_public.faction.IdentifierH\x01\x12=\n\x0eclassification\x18\x07 \x01(\x0e2%.eve_public.chat.local.ClassificationB\x15\n\x13alliance_membershipB\x14\n\x12faction_membership*\xe3\x01\n\x0eClassification\x12\x1e\n\x1aCLASSIFICATION_UNSPECIFIED\x10\x00\x12\x1c\n\x18CLASSIFICATION_INVISIBLE\x10\x01\x12\x1c\n\x18CLASSIFICATION_DEVELOPER\x10\x02\x12 \n\x1cCLASSIFICATION_ADMINISTRATOR\x10\x03\x12\x1d\n\x19CLASSIFICATION_GAMEMASTER\x10\x04\x12\x1c\n\x18CLASSIFICATION_VOLUNTEER\x10\x05\x12\x16\n\x12CLASSIFICATION_NPC\x10\x06BBZ@github.com/ccpgames/eve-proto-go/generated/eve_public/chat/localb\x06proto3', dependencies=[eve__public_dot_alliance_dot_alliance__pb2.DESCRIPTOR,
 eve__public_dot_character_dot_character__pb2.DESCRIPTOR,
 eve__public_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve__public_dot_faction_dot_faction__pb2.DESCRIPTOR])
_CLASSIFICATION = _descriptor.EnumDescriptor(name='Classification', full_name='eve_public.chat.local.Classification', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='CLASSIFICATION_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_INVISIBLE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_DEVELOPER', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_ADMINISTRATOR', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_GAMEMASTER', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_VOLUNTEER', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLASSIFICATION_NPC', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=592, serialized_end=819)
_sym_db.RegisterEnumDescriptor(_CLASSIFICATION)
Classification = enum_type_wrapper.EnumTypeWrapper(_CLASSIFICATION)
CLASSIFICATION_UNSPECIFIED = 0
CLASSIFICATION_INVISIBLE = 1
CLASSIFICATION_DEVELOPER = 2
CLASSIFICATION_ADMINISTRATOR = 3
CLASSIFICATION_GAMEMASTER = 4
CLASSIFICATION_VOLUNTEER = 5
CLASSIFICATION_NPC = 6
_CHARACTER = _descriptor.Descriptor(name='Character', full_name='eve_public.chat.local.Character', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve_public.chat.local.Character.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve_public.chat.local.Character.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_alliance', full_name='eve_public.chat.local.Character.no_alliance', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='alliance', full_name='eve_public.chat.local.Character.alliance', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_faction', full_name='eve_public.chat.local.Character.no_faction', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='faction', full_name='eve_public.chat.local.Character.faction', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='classification', full_name='eve_public.chat.local.Character.classification', index=6, number=7, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='alliance_membership', full_name='eve_public.chat.local.Character.alliance_membership', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='faction_membership', full_name='eve_public.chat.local.Character.faction_membership', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=211, serialized_end=589)
_CHARACTER.fields_by_name['character'].message_type = eve__public_dot_character_dot_character__pb2._IDENTIFIER
_CHARACTER.fields_by_name['corporation'].message_type = eve__public_dot_corporation_dot_corporation__pb2._IDENTIFIER
_CHARACTER.fields_by_name['alliance'].message_type = eve__public_dot_alliance_dot_alliance__pb2._IDENTIFIER
_CHARACTER.fields_by_name['faction'].message_type = eve__public_dot_faction_dot_faction__pb2._IDENTIFIER
_CHARACTER.fields_by_name['classification'].enum_type = _CLASSIFICATION
_CHARACTER.oneofs_by_name['alliance_membership'].fields.append(_CHARACTER.fields_by_name['no_alliance'])
_CHARACTER.fields_by_name['no_alliance'].containing_oneof = _CHARACTER.oneofs_by_name['alliance_membership']
_CHARACTER.oneofs_by_name['alliance_membership'].fields.append(_CHARACTER.fields_by_name['alliance'])
_CHARACTER.fields_by_name['alliance'].containing_oneof = _CHARACTER.oneofs_by_name['alliance_membership']
_CHARACTER.oneofs_by_name['faction_membership'].fields.append(_CHARACTER.fields_by_name['no_faction'])
_CHARACTER.fields_by_name['no_faction'].containing_oneof = _CHARACTER.oneofs_by_name['faction_membership']
_CHARACTER.oneofs_by_name['faction_membership'].fields.append(_CHARACTER.fields_by_name['faction'])
_CHARACTER.fields_by_name['faction'].containing_oneof = _CHARACTER.oneofs_by_name['faction_membership']
DESCRIPTOR.message_types_by_name['Character'] = _CHARACTER
DESCRIPTOR.enum_types_by_name['Classification'] = _CLASSIFICATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Character = _reflection.GeneratedProtocolMessageType('Character', (_message.Message,), {'DESCRIPTOR': _CHARACTER,
 '__module__': 'eve_public.chat.local.local_pb2'})
_sym_db.RegisterMessage(Character)
DESCRIPTOR._options = None
