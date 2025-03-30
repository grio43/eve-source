#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\contract\contract_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.contract import contract_pb2 as eve_dot_contract_dot_contract__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/contract/contract.proto', package='eve.character.contract', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/contract', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/character/contract/contract.proto\x12\x16eve.character.contract\x1a\x1deve/character/character.proto\x1a\x1beve/contract/contract.proto"\x98\x01\n\x08Assigned\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12-\n\x0bcontract_id\x18\x02 \x01(\x0b2\x18.eve.contract.Identifier\x12/\n\rcontract_info\x18\x03 \x01(\x0b2\x18.eve.contract.AttributesBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/character/contractb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_contract_dot_contract__pb2.DESCRIPTOR])
_ASSIGNED = _descriptor.Descriptor(name='Assigned', full_name='eve.character.contract.Assigned', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.contract.Assigned.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='contract_id', full_name='eve.character.contract.Assigned.contract_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='contract_info', full_name='eve.character.contract.Assigned.contract_info', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=278)
_ASSIGNED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ASSIGNED.fields_by_name['contract_id'].message_type = eve_dot_contract_dot_contract__pb2._IDENTIFIER
_ASSIGNED.fields_by_name['contract_info'].message_type = eve_dot_contract_dot_contract__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Assigned'] = _ASSIGNED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Assigned = _reflection.GeneratedProtocolMessageType('Assigned', (_message.Message,), {'DESCRIPTOR': _ASSIGNED,
 '__module__': 'eve.character.contract.contract_pb2'})
_sym_db.RegisterMessage(Assigned)
DESCRIPTOR._options = None
