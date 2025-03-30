#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\character\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.skill import skill_type_pb2 as eve_dot_skill_dot_skill__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/character/api/requests.proto', package='eve.skill.character.api', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/skill/character/api', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/skill/character/api/requests.proto\x12\x17eve.skill.character.api\x1a\x1deve/character/character.proto\x1a\x1aeve/skill/skill_type.proto"i\n\x0fGetLevelRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12(\n\x05skill\x18\x02 \x01(\x0b2\x19.eve.skilltype.Identifier"!\n\x10GetLevelResponse\x12\r\n\x05level\x18\x01 \x01(\rBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/skill/character/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_skill_dot_skill__type__pb2.DESCRIPTOR])
_GETLEVELREQUEST = _descriptor.Descriptor(name='GetLevelRequest', full_name='eve.skill.character.api.GetLevelRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.skill.character.api.GetLevelRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='skill', full_name='eve.skill.character.api.GetLevelRequest.skill', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=231)
_GETLEVELRESPONSE = _descriptor.Descriptor(name='GetLevelResponse', full_name='eve.skill.character.api.GetLevelResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='level', full_name='eve.skill.character.api.GetLevelResponse.level', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=233, serialized_end=266)
_GETLEVELREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETLEVELREQUEST.fields_by_name['skill'].message_type = eve_dot_skill_dot_skill__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetLevelRequest'] = _GETLEVELREQUEST
DESCRIPTOR.message_types_by_name['GetLevelResponse'] = _GETLEVELRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetLevelRequest = _reflection.GeneratedProtocolMessageType('GetLevelRequest', (_message.Message,), {'DESCRIPTOR': _GETLEVELREQUEST,
 '__module__': 'eve.skill.character.api.requests_pb2'})
_sym_db.RegisterMessage(GetLevelRequest)
GetLevelResponse = _reflection.GeneratedProtocolMessageType('GetLevelResponse', (_message.Message,), {'DESCRIPTOR': _GETLEVELRESPONSE,
 '__module__': 'eve.skill.character.api.requests_pb2'})
_sym_db.RegisterMessage(GetLevelResponse)
DESCRIPTOR._options = None
