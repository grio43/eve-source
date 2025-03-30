#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\tutorial_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/tutorial.proto', package='eve.character.tutorial', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/tutorial', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/character/tutorial.proto\x12\x16eve.character.tutorial\x1a\x1deve/character/character.proto"?\n\x0fGetStateRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"@\n\x10GetStateResponse\x12,\n\x05state\x18\x01 \x01(\x0e2\x1d.eve.character.tutorial.State"?\n\x0fTutorialStarted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"A\n\x11TutorialCompleted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"?\n\x0fTutorialSkipped\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier*\x9c\x01\n\x05State\x12\x0b\n\x07INVALID\x10\x00\x12\n\n\x06LOCKED\x10\x14\x12\n\n\x06ACTIVE\x10\x15\x12\x0c\n\x08COMPLETE\x10\x16\x12\x15\n\x11SKIPPED_BY_PLAYER\x10\x17\x12\x18\n\x14SKIPPED_BY_INCEPTION\x10\x18\x12\x1b\n\x17SKIPPED_BY_ACHIEVEMENTS\x10\x19\x12\x12\n\x0eSKIPPED_BY_AGE\x10\x1aBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/tutorialb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_STATE = _descriptor.EnumDescriptor(name='State', full_name='eve.character.tutorial.State', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='LOCKED', index=1, number=20, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACTIVE', index=2, number=21, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='COMPLETE', index=3, number=22, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SKIPPED_BY_PLAYER', index=4, number=23, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SKIPPED_BY_INCEPTION', index=5, number=24, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SKIPPED_BY_ACHIEVEMENTS', index=6, number=25, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SKIPPED_BY_AGE', index=7, number=26, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=416, serialized_end=572)
_sym_db.RegisterEnumDescriptor(_STATE)
State = enum_type_wrapper.EnumTypeWrapper(_STATE)
INVALID = 0
LOCKED = 20
ACTIVE = 21
COMPLETE = 22
SKIPPED_BY_PLAYER = 23
SKIPPED_BY_INCEPTION = 24
SKIPPED_BY_ACHIEVEMENTS = 25
SKIPPED_BY_AGE = 26
_GETSTATEREQUEST = _descriptor.Descriptor(name='GetStateRequest', full_name='eve.character.tutorial.GetStateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.tutorial.GetStateRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=87, serialized_end=150)
_GETSTATERESPONSE = _descriptor.Descriptor(name='GetStateResponse', full_name='eve.character.tutorial.GetStateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='state', full_name='eve.character.tutorial.GetStateResponse.state', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=152, serialized_end=216)
_TUTORIALSTARTED = _descriptor.Descriptor(name='TutorialStarted', full_name='eve.character.tutorial.TutorialStarted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.tutorial.TutorialStarted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=218, serialized_end=281)
_TUTORIALCOMPLETED = _descriptor.Descriptor(name='TutorialCompleted', full_name='eve.character.tutorial.TutorialCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.tutorial.TutorialCompleted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=283, serialized_end=348)
_TUTORIALSKIPPED = _descriptor.Descriptor(name='TutorialSkipped', full_name='eve.character.tutorial.TutorialSkipped', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.tutorial.TutorialSkipped.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=350, serialized_end=413)
_GETSTATEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETSTATERESPONSE.fields_by_name['state'].enum_type = _STATE
_TUTORIALSTARTED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TUTORIALCOMPLETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TUTORIALSKIPPED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetStateRequest'] = _GETSTATEREQUEST
DESCRIPTOR.message_types_by_name['GetStateResponse'] = _GETSTATERESPONSE
DESCRIPTOR.message_types_by_name['TutorialStarted'] = _TUTORIALSTARTED
DESCRIPTOR.message_types_by_name['TutorialCompleted'] = _TUTORIALCOMPLETED
DESCRIPTOR.message_types_by_name['TutorialSkipped'] = _TUTORIALSKIPPED
DESCRIPTOR.enum_types_by_name['State'] = _STATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetStateRequest = _reflection.GeneratedProtocolMessageType('GetStateRequest', (_message.Message,), {'DESCRIPTOR': _GETSTATEREQUEST,
 '__module__': 'eve.character.tutorial_pb2'})
_sym_db.RegisterMessage(GetStateRequest)
GetStateResponse = _reflection.GeneratedProtocolMessageType('GetStateResponse', (_message.Message,), {'DESCRIPTOR': _GETSTATERESPONSE,
 '__module__': 'eve.character.tutorial_pb2'})
_sym_db.RegisterMessage(GetStateResponse)
TutorialStarted = _reflection.GeneratedProtocolMessageType('TutorialStarted', (_message.Message,), {'DESCRIPTOR': _TUTORIALSTARTED,
 '__module__': 'eve.character.tutorial_pb2'})
_sym_db.RegisterMessage(TutorialStarted)
TutorialCompleted = _reflection.GeneratedProtocolMessageType('TutorialCompleted', (_message.Message,), {'DESCRIPTOR': _TUTORIALCOMPLETED,
 '__module__': 'eve.character.tutorial_pb2'})
_sym_db.RegisterMessage(TutorialCompleted)
TutorialSkipped = _reflection.GeneratedProtocolMessageType('TutorialSkipped', (_message.Message,), {'DESCRIPTOR': _TUTORIALSKIPPED,
 '__module__': 'eve.character.tutorial_pb2'})
_sym_db.RegisterMessage(TutorialSkipped)
DESCRIPTOR._options = None
