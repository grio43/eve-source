#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\corporation\corporation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.corporation import role_pb2 as eve_dot_corporation_dot_role__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/corporation/corporation.proto', package='eve.character.corporation', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/character/corporation', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/character/corporation/corporation.proto\x12\x19eve.character.corporation\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x1aeve/corporation/role.proto"\xe4\x01\n\x0bTransferred\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x125\n\x10corporation_left\x18\x02 \x01(\x0b2\x1b.eve.corporation.Identifier\x127\n\x12corporation_joined\x18\x03 \x01(\x0b2\x1b.eve.corporation.Identifier\x127\n\rroles_on_join\x18\x04 \x01(\x0b2 .eve.corporation.role.CollectionBFZDgithub.com/ccpgames/eve-proto-go/generated/eve/character/corporationb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_corporation_dot_role__pb2.DESCRIPTOR])
_TRANSFERRED = _descriptor.Descriptor(name='Transferred', full_name='eve.character.corporation.Transferred', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.corporation.Transferred.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation_left', full_name='eve.character.corporation.Transferred.corporation_left', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation_joined', full_name='eve.character.corporation.Transferred.corporation_joined', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='roles_on_join', full_name='eve.character.corporation.Transferred.roles_on_join', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=169, serialized_end=397)
_TRANSFERRED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TRANSFERRED.fields_by_name['corporation_left'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_TRANSFERRED.fields_by_name['corporation_joined'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_TRANSFERRED.fields_by_name['roles_on_join'].message_type = eve_dot_corporation_dot_role__pb2._COLLECTION
DESCRIPTOR.message_types_by_name['Transferred'] = _TRANSFERRED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Transferred = _reflection.GeneratedProtocolMessageType('Transferred', (_message.Message,), {'DESCRIPTOR': _TRANSFERRED,
 '__module__': 'eve.character.corporation.corporation_pb2'})
_sym_db.RegisterMessage(Transferred)
DESCRIPTOR._options = None
