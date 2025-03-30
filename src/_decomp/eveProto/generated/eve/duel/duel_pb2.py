#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\duel\duel_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/duel/duel.proto', package='eve.duel', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/duel', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/duel/duel.proto\x12\x08eve.duel\x1a\x1deve/character/character.proto"n\n\x0fChallengeIssued\x12-\n\nchallenger\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12,\n\trecipient\x18\x02 \x01(\x0b2\x19.eve.character.Identifier"p\n\x11ChallengeAccepted\x12-\n\nchallenger\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12,\n\trecipient\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierB5Z3github.com/ccpgames/eve-proto-go/generated/eve/duelb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_CHALLENGEISSUED = _descriptor.Descriptor(name='ChallengeIssued', full_name='eve.duel.ChallengeIssued', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='challenger', full_name='eve.duel.ChallengeIssued.challenger', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='recipient', full_name='eve.duel.ChallengeIssued.recipient', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=64, serialized_end=174)
_CHALLENGEACCEPTED = _descriptor.Descriptor(name='ChallengeAccepted', full_name='eve.duel.ChallengeAccepted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='challenger', full_name='eve.duel.ChallengeAccepted.challenger', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='recipient', full_name='eve.duel.ChallengeAccepted.recipient', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=176, serialized_end=288)
_CHALLENGEISSUED.fields_by_name['challenger'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CHALLENGEISSUED.fields_by_name['recipient'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CHALLENGEACCEPTED.fields_by_name['challenger'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CHALLENGEACCEPTED.fields_by_name['recipient'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ChallengeIssued'] = _CHALLENGEISSUED
DESCRIPTOR.message_types_by_name['ChallengeAccepted'] = _CHALLENGEACCEPTED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ChallengeIssued = _reflection.GeneratedProtocolMessageType('ChallengeIssued', (_message.Message,), {'DESCRIPTOR': _CHALLENGEISSUED,
 '__module__': 'eve.duel.duel_pb2'})
_sym_db.RegisterMessage(ChallengeIssued)
ChallengeAccepted = _reflection.GeneratedProtocolMessageType('ChallengeAccepted', (_message.Message,), {'DESCRIPTOR': _CHALLENGEACCEPTED,
 '__module__': 'eve.duel.duel_pb2'})
_sym_db.RegisterMessage(ChallengeAccepted)
DESCRIPTOR._options = None
