#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\market\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/market/api/api.proto', package='eve.cosmetic.market.api', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/api', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/cosmetic/market/api/api.proto\x12\x17eve.cosmetic.market.api\x1a\x1deve/character/character.proto"P\n GetSkillBasedTaxReductionRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"C\n!GetSkillBasedTaxReductionResponse\x12\x1e\n\x16reduction_basis_points\x18\x01 \x01(\x04BDZBgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_GETSKILLBASEDTAXREDUCTIONREQUEST = _descriptor.Descriptor(name='GetSkillBasedTaxReductionRequest', full_name='eve.cosmetic.market.api.GetSkillBasedTaxReductionRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.cosmetic.market.api.GetSkillBasedTaxReductionRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=173)
_GETSKILLBASEDTAXREDUCTIONRESPONSE = _descriptor.Descriptor(name='GetSkillBasedTaxReductionResponse', full_name='eve.cosmetic.market.api.GetSkillBasedTaxReductionResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='reduction_basis_points', full_name='eve.cosmetic.market.api.GetSkillBasedTaxReductionResponse.reduction_basis_points', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=175, serialized_end=242)
_GETSKILLBASEDTAXREDUCTIONREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetSkillBasedTaxReductionRequest'] = _GETSKILLBASEDTAXREDUCTIONREQUEST
DESCRIPTOR.message_types_by_name['GetSkillBasedTaxReductionResponse'] = _GETSKILLBASEDTAXREDUCTIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetSkillBasedTaxReductionRequest = _reflection.GeneratedProtocolMessageType('GetSkillBasedTaxReductionRequest', (_message.Message,), {'DESCRIPTOR': _GETSKILLBASEDTAXREDUCTIONREQUEST,
 '__module__': 'eve.cosmetic.market.api.api_pb2'})
_sym_db.RegisterMessage(GetSkillBasedTaxReductionRequest)
GetSkillBasedTaxReductionResponse = _reflection.GeneratedProtocolMessageType('GetSkillBasedTaxReductionResponse', (_message.Message,), {'DESCRIPTOR': _GETSKILLBASEDTAXREDUCTIONRESPONSE,
 '__module__': 'eve.cosmetic.market.api.api_pb2'})
_sym_db.RegisterMessage(GetSkillBasedTaxReductionResponse)
DESCRIPTOR._options = None
