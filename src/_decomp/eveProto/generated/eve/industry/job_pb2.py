#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\job_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.industry.job import blueprint_copy_pb2 as eve_dot_industry_dot_job_dot_blueprint__copy__pb2
from eveProto.generated.eve.industry.job import blueprint_invention_pb2 as eve_dot_industry_dot_job_dot_blueprint__invention__pb2
from eveProto.generated.eve.industry.job import manufacturing_pb2 as eve_dot_industry_dot_job_dot_manufacturing__pb2
from eveProto.generated.eve.industry.job import reaction_pb2 as eve_dot_industry_dot_job_dot_reaction__pb2
from eveProto.generated.eve.industry.job import research_duration_pb2 as eve_dot_industry_dot_job_dot_research__duration__pb2
from eveProto.generated.eve.industry.job import research_materials_pb2 as eve_dot_industry_dot_job_dot_research__materials__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/job.proto', package='eve.industry.job', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/industry/job', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/industry/job.proto\x12\x10eve.industry.job\x1a\x1deve/character/character.proto\x1a%eve/industry/job/blueprint_copy.proto\x1a*eve/industry/job/blueprint_invention.proto\x1a$eve/industry/job/manufacturing.proto\x1a\x1feve/industry/job/reaction.proto\x1a(eve/industry/job/research_duration.proto\x1a)eve/industry/job/research_materials.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xf0\x03\n\x05Entry\x12(\n\x02id\x18\x01 \x01(\x0b2\x1c.eve.industry.job.Identifier\x12E\n\x0eblueprint_copy\x18\x02 \x01(\x0b2+.eve.industry.job.blueprint_copy.AttributesH\x00\x12O\n\x13blueprint_invention\x18\x03 \x01(\x0b20.eve.industry.job.blueprint_invention.AttributesH\x00\x12C\n\rmanufacturing\x18\x04 \x01(\x0b2*.eve.industry.job.manufacturing.AttributesH\x00\x129\n\x08reaction\x18\x05 \x01(\x0b2%.eve.industry.job.reaction.AttributesH\x00\x12K\n\x11research_duration\x18\x06 \x01(\x0b2..eve.industry.job.research_duration.AttributesH\x00\x12M\n\x12research_materials\x18\x07 \x01(\x0b2/.eve.industry.job.research_materials.AttributesH\x00B\t\n\x07details"9\n\tInstalled\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier">\n\x0eBlueprintAdded\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"=\n\rMaterialAdded\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierB=Z;github.com/ccpgames/eve-proto-go/generated/eve/industry/jobb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_blueprint__copy__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_blueprint__invention__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_manufacturing__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_reaction__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_research__duration__pb2.DESCRIPTOR,
 eve_dot_industry_dot_job_dot_research__materials__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.industry.job.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.industry.job.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=314, serialized_end=346)
_ENTRY = _descriptor.Descriptor(name='Entry', full_name='eve.industry.job.Entry', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.industry.job.Entry.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='blueprint_copy', full_name='eve.industry.job.Entry.blueprint_copy', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='blueprint_invention', full_name='eve.industry.job.Entry.blueprint_invention', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='manufacturing', full_name='eve.industry.job.Entry.manufacturing', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reaction', full_name='eve.industry.job.Entry.reaction', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='research_duration', full_name='eve.industry.job.Entry.research_duration', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='research_materials', full_name='eve.industry.job.Entry.research_materials', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='details', full_name='eve.industry.job.Entry.details', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=349, serialized_end=845)
_INSTALLED = _descriptor.Descriptor(name='Installed', full_name='eve.industry.job.Installed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.industry.job.Installed.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=847, serialized_end=904)
_BLUEPRINTADDED = _descriptor.Descriptor(name='BlueprintAdded', full_name='eve.industry.job.BlueprintAdded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.industry.job.BlueprintAdded.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=906, serialized_end=968)
_MATERIALADDED = _descriptor.Descriptor(name='MaterialAdded', full_name='eve.industry.job.MaterialAdded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.industry.job.MaterialAdded.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=970, serialized_end=1031)
_ENTRY.fields_by_name['id'].message_type = _IDENTIFIER
_ENTRY.fields_by_name['blueprint_copy'].message_type = eve_dot_industry_dot_job_dot_blueprint__copy__pb2._ATTRIBUTES
_ENTRY.fields_by_name['blueprint_invention'].message_type = eve_dot_industry_dot_job_dot_blueprint__invention__pb2._ATTRIBUTES
_ENTRY.fields_by_name['manufacturing'].message_type = eve_dot_industry_dot_job_dot_manufacturing__pb2._ATTRIBUTES
_ENTRY.fields_by_name['reaction'].message_type = eve_dot_industry_dot_job_dot_reaction__pb2._ATTRIBUTES
_ENTRY.fields_by_name['research_duration'].message_type = eve_dot_industry_dot_job_dot_research__duration__pb2._ATTRIBUTES
_ENTRY.fields_by_name['research_materials'].message_type = eve_dot_industry_dot_job_dot_research__materials__pb2._ATTRIBUTES
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['blueprint_copy'])
_ENTRY.fields_by_name['blueprint_copy'].containing_oneof = _ENTRY.oneofs_by_name['details']
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['blueprint_invention'])
_ENTRY.fields_by_name['blueprint_invention'].containing_oneof = _ENTRY.oneofs_by_name['details']
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['manufacturing'])
_ENTRY.fields_by_name['manufacturing'].containing_oneof = _ENTRY.oneofs_by_name['details']
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['reaction'])
_ENTRY.fields_by_name['reaction'].containing_oneof = _ENTRY.oneofs_by_name['details']
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['research_duration'])
_ENTRY.fields_by_name['research_duration'].containing_oneof = _ENTRY.oneofs_by_name['details']
_ENTRY.oneofs_by_name['details'].fields.append(_ENTRY.fields_by_name['research_materials'])
_ENTRY.fields_by_name['research_materials'].containing_oneof = _ENTRY.oneofs_by_name['details']
_INSTALLED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_BLUEPRINTADDED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MATERIALADDED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Entry'] = _ENTRY
DESCRIPTOR.message_types_by_name['Installed'] = _INSTALLED
DESCRIPTOR.message_types_by_name['BlueprintAdded'] = _BLUEPRINTADDED
DESCRIPTOR.message_types_by_name['MaterialAdded'] = _MATERIALADDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.industry.job_pb2'})
_sym_db.RegisterMessage(Identifier)
Entry = _reflection.GeneratedProtocolMessageType('Entry', (_message.Message,), {'DESCRIPTOR': _ENTRY,
 '__module__': 'eve.industry.job_pb2'})
_sym_db.RegisterMessage(Entry)
Installed = _reflection.GeneratedProtocolMessageType('Installed', (_message.Message,), {'DESCRIPTOR': _INSTALLED,
 '__module__': 'eve.industry.job_pb2'})
_sym_db.RegisterMessage(Installed)
BlueprintAdded = _reflection.GeneratedProtocolMessageType('BlueprintAdded', (_message.Message,), {'DESCRIPTOR': _BLUEPRINTADDED,
 '__module__': 'eve.industry.job_pb2'})
_sym_db.RegisterMessage(BlueprintAdded)
MaterialAdded = _reflection.GeneratedProtocolMessageType('MaterialAdded', (_message.Message,), {'DESCRIPTOR': _MATERIALADDED,
 '__module__': 'eve.industry.job_pb2'})
_sym_db.RegisterMessage(MaterialAdded)
DESCRIPTOR._options = None
