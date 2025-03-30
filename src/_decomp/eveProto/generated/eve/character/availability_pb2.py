#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\availability_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/availability.proto', package='eve.character.availability', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/character/availability', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/character/availability.proto\x12\x1aeve.character.availability\x1a\x1deve/character/character.proto\x1a\x13eve/user/user.proto"=\n\rFreezeRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"?\n\x0fUnfreezeRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"@\n\x1aGetFrozenCharactersRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"L\n\x1bGetFrozenCharactersResponse\x12-\n\ncharacters\x18\x01 \x03(\x0b2\x19.eve.character.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/character/availabilityb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR])
_FREEZEREQUEST = _descriptor.Descriptor(name='FreezeRequest', full_name='eve.character.availability.FreezeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.availability.FreezeRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=116, serialized_end=177)
_UNFREEZEREQUEST = _descriptor.Descriptor(name='UnfreezeRequest', full_name='eve.character.availability.UnfreezeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.availability.UnfreezeRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=179, serialized_end=242)
_GETFROZENCHARACTERSREQUEST = _descriptor.Descriptor(name='GetFrozenCharactersRequest', full_name='eve.character.availability.GetFrozenCharactersRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.character.availability.GetFrozenCharactersRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=244, serialized_end=308)
_GETFROZENCHARACTERSRESPONSE = _descriptor.Descriptor(name='GetFrozenCharactersResponse', full_name='eve.character.availability.GetFrozenCharactersResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='characters', full_name='eve.character.availability.GetFrozenCharactersResponse.characters', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=310, serialized_end=386)
_FREEZEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_UNFREEZEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETFROZENCHARACTERSREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETFROZENCHARACTERSRESPONSE.fields_by_name['characters'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['FreezeRequest'] = _FREEZEREQUEST
DESCRIPTOR.message_types_by_name['UnfreezeRequest'] = _UNFREEZEREQUEST
DESCRIPTOR.message_types_by_name['GetFrozenCharactersRequest'] = _GETFROZENCHARACTERSREQUEST
DESCRIPTOR.message_types_by_name['GetFrozenCharactersResponse'] = _GETFROZENCHARACTERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
FreezeRequest = _reflection.GeneratedProtocolMessageType('FreezeRequest', (_message.Message,), {'DESCRIPTOR': _FREEZEREQUEST,
 '__module__': 'eve.character.availability_pb2'})
_sym_db.RegisterMessage(FreezeRequest)
UnfreezeRequest = _reflection.GeneratedProtocolMessageType('UnfreezeRequest', (_message.Message,), {'DESCRIPTOR': _UNFREEZEREQUEST,
 '__module__': 'eve.character.availability_pb2'})
_sym_db.RegisterMessage(UnfreezeRequest)
GetFrozenCharactersRequest = _reflection.GeneratedProtocolMessageType('GetFrozenCharactersRequest', (_message.Message,), {'DESCRIPTOR': _GETFROZENCHARACTERSREQUEST,
 '__module__': 'eve.character.availability_pb2'})
_sym_db.RegisterMessage(GetFrozenCharactersRequest)
GetFrozenCharactersResponse = _reflection.GeneratedProtocolMessageType('GetFrozenCharactersResponse', (_message.Message,), {'DESCRIPTOR': _GETFROZENCHARACTERSRESPONSE,
 '__module__': 'eve.character.availability_pb2'})
_sym_db.RegisterMessage(GetFrozenCharactersResponse)
DESCRIPTOR._options = None
