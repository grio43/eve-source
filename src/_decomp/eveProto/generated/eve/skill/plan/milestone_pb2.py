#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\plan\milestone_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.skill.plan import plan_pb2 as eve_dot_skill_dot_plan_dot_plan__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/plan/milestone.proto', package='eve.skill.plan.milestone', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/skill/plan/milestone', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/skill/plan/milestone.proto\x12\x18eve.skill.plan.milestone\x1a%eve/inventory/generic_item_type.proto\x1a\x19eve/skill/plan/plan.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\xd5\x01\n\nAttributes\x12.\n\nskill_plan\x18\x01 \x01(\x0b2\x1a.eve.skill.plan.Identifier\x12B\n\rtrain_to_type\x18\x02 \x01(\x0b2).eve.inventory.genericitemtype.IdentifierH\x00\x121\n\x05skill\x18\x03 \x01(\x0b2 .eve.skill.plan.SkillRequirementH\x00\x12\x13\n\x0bdescription\x18\x04 \x01(\tB\x0b\n\tmilestoneBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/skill/plan/milestoneb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR, eve_dot_skill_dot_plan_dot_plan__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.skill.plan.milestone.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.skill.plan.milestone.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=152)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.skill.plan.milestone.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skill_plan', full_name='eve.skill.plan.milestone.Attributes.skill_plan', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='train_to_type', full_name='eve.skill.plan.milestone.Attributes.train_to_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skill', full_name='eve.skill.plan.milestone.Attributes.skill', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.skill.plan.milestone.Attributes.description', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='milestone', full_name='eve.skill.plan.milestone.Attributes.milestone', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=155, serialized_end=368)
_ATTRIBUTES.fields_by_name['skill_plan'].message_type = eve_dot_skill_dot_plan_dot_plan__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['train_to_type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['skill'].message_type = eve_dot_skill_dot_plan_dot_plan__pb2._SKILLREQUIREMENT
_ATTRIBUTES.oneofs_by_name['milestone'].fields.append(_ATTRIBUTES.fields_by_name['train_to_type'])
_ATTRIBUTES.fields_by_name['train_to_type'].containing_oneof = _ATTRIBUTES.oneofs_by_name['milestone']
_ATTRIBUTES.oneofs_by_name['milestone'].fields.append(_ATTRIBUTES.fields_by_name['skill'])
_ATTRIBUTES.fields_by_name['skill'].containing_oneof = _ATTRIBUTES.oneofs_by_name['milestone']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.skill.plan.milestone_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.skill.plan.milestone_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
