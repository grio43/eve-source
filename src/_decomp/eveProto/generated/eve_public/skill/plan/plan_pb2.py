#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\skill\plan\plan_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.skill import skilltype_pb2 as eve__public_dot_skill_dot_skilltype__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/skill/plan/plan.proto', package='eve_public.skill.plan', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve_public/skill/plan', create_key=_descriptor._internal_create_key, serialized_pb='\n eve_public/skill/plan/plan.proto\x12\x15eve_public.skill.plan\x1a eve_public/skill/skilltype.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"t\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12C\n\x12skill_requirements\x18\x02 \x03(\x0b2\'.eve_public.skill.plan.SkillRequirement\x12\x13\n\x0bdescription\x18\x03 \x01(\t"W\n\x10SkillRequirement\x124\n\nskill_type\x18\x01 \x01(\x0b2 .eve_public.skilltype.Identifier\x12\r\n\x05level\x18\x02 \x01(\r"\x13\n\rGetAllRequest:\x02\x18\x01"L\n\x0eGetAllResponse\x126\n\x0bskill_plans\x18\x01 \x03(\x0b2!.eve_public.skill.plan.Identifier:\x02\x18\x01"G\n\nGetRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier:\x02\x18\x01"H\n\x0bGetResponse\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Attributes:\x02\x18\x01"J\n\rCreateRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Attributes:\x02\x18\x01"K\n\x0eCreateResponse\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier:\x02\x18\x01"\x97\x01\n\x1bSetSkillRequirementsRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier\x12=\n\x0crequirements\x18\x02 \x03(\x0b2\'.eve_public.skill.plan.SkillRequirement:\x02\x18\x01""\n\x1cSetSkillRequirementsResponse:\x02\x18\x01"Y\n\x0eSetNameRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier\x12\x0c\n\x04name\x18\x02 \x01(\t:\x02\x18\x01"\x15\n\x0fSetNameResponse:\x02\x18\x01"g\n\x15SetDescriptionRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier\x12\x13\n\x0bdescription\x18\x02 \x01(\t:\x02\x18\x01"\x1c\n\x16SetDescriptionResponse:\x02\x18\x01"J\n\rDeleteRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier:\x02\x18\x01"\x14\n\x0eDeleteResponse:\x02\x18\x01"\x16\n\x10GetActiveRequest:\x02\x18\x01"\x8a\x01\n\x11GetActiveResponse\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier\x12:\n\x0fskill_plan_info\x18\x02 \x01(\x0b2!.eve_public.skill.plan.Attributes:\x02\x18\x01"M\n\x10SetActiveRequest\x125\n\nskill_plan\x18\x01 \x01(\x0b2!.eve_public.skill.plan.Identifier:\x02\x18\x01"\x17\n\x11SetActiveResponse:\x02\x18\x01BBZ@github.com/ccpgames/eve-proto-go/generated/eve_public/skill/planb\x06proto3', dependencies=[eve__public_dot_skill_dot_skilltype__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.skill.plan.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve_public.skill.plan.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=119)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve_public.skill.plan.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve_public.skill.plan.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='skill_requirements', full_name='eve_public.skill.plan.Attributes.skill_requirements', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='description', full_name='eve_public.skill.plan.Attributes.description', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=121, serialized_end=237)
_SKILLREQUIREMENT = _descriptor.Descriptor(name='SkillRequirement', full_name='eve_public.skill.plan.SkillRequirement', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_type', full_name='eve_public.skill.plan.SkillRequirement.skill_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='level', full_name='eve_public.skill.plan.SkillRequirement.level', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=239, serialized_end=326)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve_public.skill.plan.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=328, serialized_end=347)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve_public.skill.plan.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plans', full_name='eve_public.skill.plan.GetAllResponse.skill_plans', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=349, serialized_end=425)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.skill.plan.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.GetRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=427, serialized_end=498)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.skill.plan.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.GetResponse.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=500, serialized_end=572)
_CREATEREQUEST = _descriptor.Descriptor(name='CreateRequest', full_name='eve_public.skill.plan.CreateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.CreateRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=574, serialized_end=648)
_CREATERESPONSE = _descriptor.Descriptor(name='CreateResponse', full_name='eve_public.skill.plan.CreateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.CreateResponse.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=650, serialized_end=725)
_SETSKILLREQUIREMENTSREQUEST = _descriptor.Descriptor(name='SetSkillRequirementsRequest', full_name='eve_public.skill.plan.SetSkillRequirementsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.SetSkillRequirementsRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='requirements', full_name='eve_public.skill.plan.SetSkillRequirementsRequest.requirements', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=728, serialized_end=879)
_SETSKILLREQUIREMENTSRESPONSE = _descriptor.Descriptor(name='SetSkillRequirementsResponse', full_name='eve_public.skill.plan.SetSkillRequirementsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=881, serialized_end=915)
_SETNAMEREQUEST = _descriptor.Descriptor(name='SetNameRequest', full_name='eve_public.skill.plan.SetNameRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.SetNameRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='name', full_name='eve_public.skill.plan.SetNameRequest.name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=917, serialized_end=1006)
_SETNAMERESPONSE = _descriptor.Descriptor(name='SetNameResponse', full_name='eve_public.skill.plan.SetNameResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1008, serialized_end=1029)
_SETDESCRIPTIONREQUEST = _descriptor.Descriptor(name='SetDescriptionRequest', full_name='eve_public.skill.plan.SetDescriptionRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.SetDescriptionRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='description', full_name='eve_public.skill.plan.SetDescriptionRequest.description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1031, serialized_end=1134)
_SETDESCRIPTIONRESPONSE = _descriptor.Descriptor(name='SetDescriptionResponse', full_name='eve_public.skill.plan.SetDescriptionResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1136, serialized_end=1164)
_DELETEREQUEST = _descriptor.Descriptor(name='DeleteRequest', full_name='eve_public.skill.plan.DeleteRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.DeleteRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1166, serialized_end=1240)
_DELETERESPONSE = _descriptor.Descriptor(name='DeleteResponse', full_name='eve_public.skill.plan.DeleteResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1242, serialized_end=1262)
_GETACTIVEREQUEST = _descriptor.Descriptor(name='GetActiveRequest', full_name='eve_public.skill.plan.GetActiveRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1264, serialized_end=1286)
_GETACTIVERESPONSE = _descriptor.Descriptor(name='GetActiveResponse', full_name='eve_public.skill.plan.GetActiveResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.GetActiveResponse.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='skill_plan_info', full_name='eve_public.skill.plan.GetActiveResponse.skill_plan_info', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1289, serialized_end=1427)
_SETACTIVEREQUEST = _descriptor.Descriptor(name='SetActiveRequest', full_name='eve_public.skill.plan.SetActiveRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve_public.skill.plan.SetActiveRequest.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1429, serialized_end=1506)
_SETACTIVERESPONSE = _descriptor.Descriptor(name='SetActiveResponse', full_name='eve_public.skill.plan.SetActiveResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1508, serialized_end=1531)
_ATTRIBUTES.fields_by_name['skill_requirements'].message_type = _SKILLREQUIREMENT
_SKILLREQUIREMENT.fields_by_name['skill_type'].message_type = eve__public_dot_skill_dot_skilltype__pb2._IDENTIFIER
_GETALLRESPONSE.fields_by_name['skill_plans'].message_type = _IDENTIFIER
_GETREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['skill_plan'].message_type = _ATTRIBUTES
_CREATEREQUEST.fields_by_name['skill_plan'].message_type = _ATTRIBUTES
_CREATERESPONSE.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_SETSKILLREQUIREMENTSREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_SETSKILLREQUIREMENTSREQUEST.fields_by_name['requirements'].message_type = _SKILLREQUIREMENT
_SETNAMEREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_SETDESCRIPTIONREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_DELETEREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_GETACTIVERESPONSE.fields_by_name['skill_plan'].message_type = _IDENTIFIER
_GETACTIVERESPONSE.fields_by_name['skill_plan_info'].message_type = _ATTRIBUTES
_SETACTIVEREQUEST.fields_by_name['skill_plan'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['SkillRequirement'] = _SKILLREQUIREMENT
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['CreateRequest'] = _CREATEREQUEST
DESCRIPTOR.message_types_by_name['CreateResponse'] = _CREATERESPONSE
DESCRIPTOR.message_types_by_name['SetSkillRequirementsRequest'] = _SETSKILLREQUIREMENTSREQUEST
DESCRIPTOR.message_types_by_name['SetSkillRequirementsResponse'] = _SETSKILLREQUIREMENTSRESPONSE
DESCRIPTOR.message_types_by_name['SetNameRequest'] = _SETNAMEREQUEST
DESCRIPTOR.message_types_by_name['SetNameResponse'] = _SETNAMERESPONSE
DESCRIPTOR.message_types_by_name['SetDescriptionRequest'] = _SETDESCRIPTIONREQUEST
DESCRIPTOR.message_types_by_name['SetDescriptionResponse'] = _SETDESCRIPTIONRESPONSE
DESCRIPTOR.message_types_by_name['DeleteRequest'] = _DELETEREQUEST
DESCRIPTOR.message_types_by_name['DeleteResponse'] = _DELETERESPONSE
DESCRIPTOR.message_types_by_name['GetActiveRequest'] = _GETACTIVEREQUEST
DESCRIPTOR.message_types_by_name['GetActiveResponse'] = _GETACTIVERESPONSE
DESCRIPTOR.message_types_by_name['SetActiveRequest'] = _SETACTIVEREQUEST
DESCRIPTOR.message_types_by_name['SetActiveResponse'] = _SETACTIVERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(Attributes)
SkillRequirement = _reflection.GeneratedProtocolMessageType('SkillRequirement', (_message.Message,), {'DESCRIPTOR': _SKILLREQUIREMENT,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SkillRequirement)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetResponse)
CreateRequest = _reflection.GeneratedProtocolMessageType('CreateRequest', (_message.Message,), {'DESCRIPTOR': _CREATEREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(CreateRequest)
CreateResponse = _reflection.GeneratedProtocolMessageType('CreateResponse', (_message.Message,), {'DESCRIPTOR': _CREATERESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(CreateResponse)
SetSkillRequirementsRequest = _reflection.GeneratedProtocolMessageType('SetSkillRequirementsRequest', (_message.Message,), {'DESCRIPTOR': _SETSKILLREQUIREMENTSREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetSkillRequirementsRequest)
SetSkillRequirementsResponse = _reflection.GeneratedProtocolMessageType('SetSkillRequirementsResponse', (_message.Message,), {'DESCRIPTOR': _SETSKILLREQUIREMENTSRESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetSkillRequirementsResponse)
SetNameRequest = _reflection.GeneratedProtocolMessageType('SetNameRequest', (_message.Message,), {'DESCRIPTOR': _SETNAMEREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetNameRequest)
SetNameResponse = _reflection.GeneratedProtocolMessageType('SetNameResponse', (_message.Message,), {'DESCRIPTOR': _SETNAMERESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetNameResponse)
SetDescriptionRequest = _reflection.GeneratedProtocolMessageType('SetDescriptionRequest', (_message.Message,), {'DESCRIPTOR': _SETDESCRIPTIONREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetDescriptionRequest)
SetDescriptionResponse = _reflection.GeneratedProtocolMessageType('SetDescriptionResponse', (_message.Message,), {'DESCRIPTOR': _SETDESCRIPTIONRESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetDescriptionResponse)
DeleteRequest = _reflection.GeneratedProtocolMessageType('DeleteRequest', (_message.Message,), {'DESCRIPTOR': _DELETEREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(DeleteRequest)
DeleteResponse = _reflection.GeneratedProtocolMessageType('DeleteResponse', (_message.Message,), {'DESCRIPTOR': _DELETERESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(DeleteResponse)
GetActiveRequest = _reflection.GeneratedProtocolMessageType('GetActiveRequest', (_message.Message,), {'DESCRIPTOR': _GETACTIVEREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetActiveRequest)
GetActiveResponse = _reflection.GeneratedProtocolMessageType('GetActiveResponse', (_message.Message,), {'DESCRIPTOR': _GETACTIVERESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(GetActiveResponse)
SetActiveRequest = _reflection.GeneratedProtocolMessageType('SetActiveRequest', (_message.Message,), {'DESCRIPTOR': _SETACTIVEREQUEST,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetActiveRequest)
SetActiveResponse = _reflection.GeneratedProtocolMessageType('SetActiveResponse', (_message.Message,), {'DESCRIPTOR': _SETACTIVERESPONSE,
 '__module__': 'eve_public.skill.plan.plan_pb2'})
_sym_db.RegisterMessage(SetActiveResponse)
DESCRIPTOR._options = None
_GETALLREQUEST._options = None
_GETALLRESPONSE._options = None
_GETREQUEST._options = None
_GETRESPONSE._options = None
_CREATEREQUEST._options = None
_CREATERESPONSE._options = None
_SETSKILLREQUIREMENTSREQUEST._options = None
_SETSKILLREQUIREMENTSRESPONSE._options = None
_SETNAMEREQUEST._options = None
_SETNAMERESPONSE._options = None
_SETDESCRIPTIONREQUEST._options = None
_SETDESCRIPTIONRESPONSE._options = None
_DELETEREQUEST._options = None
_DELETERESPONSE._options = None
_GETACTIVEREQUEST._options = None
_GETACTIVERESPONSE._options = None
_SETACTIVEREQUEST._options = None
_SETACTIVERESPONSE._options = None
