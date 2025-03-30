#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\expertsystems\expertsystems_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.skill.expertsystems import expertsystems_type_pb2 as eve_dot_skill_dot_expertsystems_dot_expertsystems__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/expertsystems/expertsystems.proto', package='eve.skill.expertsystems', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/skill/expertsystems', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/skill/expertsystems/expertsystems.proto\x12\x17eve.skill.expertsystems\x1a\x1deve/character/character.proto\x1a0eve/skill/expertsystems/expertsystems_type.proto"n\n\tActivated\x123\n\x02id\x18\x01 \x01(\x0b2\'.eve.skill.expertsystemstype.Identifier\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/skill/expertsystemsb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_skill_dot_expertsystems_dot_expertsystems__type__pb2.DESCRIPTOR])
_ACTIVATED = _descriptor.Descriptor(name='Activated', full_name='eve.skill.expertsystems.Activated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.skill.expertsystems.Activated.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.skill.expertsystems.Activated.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=153, serialized_end=263)
_ACTIVATED.fields_by_name['id'].message_type = eve_dot_skill_dot_expertsystems_dot_expertsystems__type__pb2._IDENTIFIER
_ACTIVATED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Activated'] = _ACTIVATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Activated = _reflection.GeneratedProtocolMessageType('Activated', (_message.Message,), {'DESCRIPTOR': _ACTIVATED,
 '__module__': 'eve.skill.expertsystems.expertsystems_pb2'})
_sym_db.RegisterMessage(Activated)
DESCRIPTOR._options = None
