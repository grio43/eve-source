#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\character_attributes_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/character_attributes.proto', package='eve.skill.characterattributes', syntax='proto3', serialized_options='ZHgithub.com/ccpgames/eve-proto-go/generated/eve/skill/characterattributes', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/skill/character_attributes.proto\x12\x1deve.skill.characterattributes\x1a\x1fgoogle/protobuf/timestamp.proto"g\n\x06Values\x12\x14\n\x0cintelligence\x18\x01 \x01(\r\x12\x10\n\x08charisma\x18\x02 \x01(\r\x12\x12\n\nperception\x18\x03 \x01(\r\x12\x0e\n\x06memory\x18\x04 \x01(\r\x12\x11\n\twillpower\x18\x05 \x01(\r"\x9a\x02\n\x06Remaps\x12\x1e\n\x16bonus_remaps_available\x18\x01 \x01(\r\x126\n\x10last_remapped_at\x18\x02 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12\x1d\n\x13no_last_remapped_at\x18\x03 \x01(\x08H\x00\x12?\n\x19accrued_remap_cooldown_at\x18\x04 \x01(\x0b2\x1a.google.protobuf.TimestampH\x01\x12&\n\x1cno_accrued_remap_cooldown_at\x18\x05 \x01(\x08H\x01B\x11\n\x0flast_remap_dateB\x1d\n\x1baccrued_remap_cooldown_date*|\n\x04Type\x12\x10\n\x0cTYPE_INVALID\x10\x00\x12\x15\n\x11TYPE_INTELLIGENCE\x10\x01\x12\x11\n\rTYPE_CHARISMA\x10\x02\x12\x13\n\x0fTYPE_PERCEPTION\x10\x03\x12\x0f\n\x0bTYPE_MEMORY\x10\x04\x12\x12\n\x0eTYPE_WILLPOWER\x10\x05BJZHgithub.com/ccpgames/eve-proto-go/generated/eve/skill/characterattributesb\x06proto3', dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_TYPE = _descriptor.EnumDescriptor(name='Type', full_name='eve.skill.characterattributes.Type', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TYPE_INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_INTELLIGENCE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_CHARISMA', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_PERCEPTION', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_MEMORY', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_WILLPOWER', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=494, serialized_end=618)
_sym_db.RegisterEnumDescriptor(_TYPE)
Type = enum_type_wrapper.EnumTypeWrapper(_TYPE)
TYPE_INVALID = 0
TYPE_INTELLIGENCE = 1
TYPE_CHARISMA = 2
TYPE_PERCEPTION = 3
TYPE_MEMORY = 4
TYPE_WILLPOWER = 5
_VALUES = _descriptor.Descriptor(name='Values', full_name='eve.skill.characterattributes.Values', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='intelligence', full_name='eve.skill.characterattributes.Values.intelligence', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='charisma', full_name='eve.skill.characterattributes.Values.charisma', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='perception', full_name='eve.skill.characterattributes.Values.perception', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='memory', full_name='eve.skill.characterattributes.Values.memory', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='willpower', full_name='eve.skill.characterattributes.Values.willpower', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=104, serialized_end=207)
_REMAPS = _descriptor.Descriptor(name='Remaps', full_name='eve.skill.characterattributes.Remaps', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='bonus_remaps_available', full_name='eve.skill.characterattributes.Remaps.bonus_remaps_available', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_remapped_at', full_name='eve.skill.characterattributes.Remaps.last_remapped_at', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_last_remapped_at', full_name='eve.skill.characterattributes.Remaps.no_last_remapped_at', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='accrued_remap_cooldown_at', full_name='eve.skill.characterattributes.Remaps.accrued_remap_cooldown_at', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_accrued_remap_cooldown_at', full_name='eve.skill.characterattributes.Remaps.no_accrued_remap_cooldown_at', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='last_remap_date', full_name='eve.skill.characterattributes.Remaps.last_remap_date', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='accrued_remap_cooldown_date', full_name='eve.skill.characterattributes.Remaps.accrued_remap_cooldown_date', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=210, serialized_end=492)
_REMAPS.fields_by_name['last_remapped_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_REMAPS.fields_by_name['accrued_remap_cooldown_at'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_REMAPS.oneofs_by_name['last_remap_date'].fields.append(_REMAPS.fields_by_name['last_remapped_at'])
_REMAPS.fields_by_name['last_remapped_at'].containing_oneof = _REMAPS.oneofs_by_name['last_remap_date']
_REMAPS.oneofs_by_name['last_remap_date'].fields.append(_REMAPS.fields_by_name['no_last_remapped_at'])
_REMAPS.fields_by_name['no_last_remapped_at'].containing_oneof = _REMAPS.oneofs_by_name['last_remap_date']
_REMAPS.oneofs_by_name['accrued_remap_cooldown_date'].fields.append(_REMAPS.fields_by_name['accrued_remap_cooldown_at'])
_REMAPS.fields_by_name['accrued_remap_cooldown_at'].containing_oneof = _REMAPS.oneofs_by_name['accrued_remap_cooldown_date']
_REMAPS.oneofs_by_name['accrued_remap_cooldown_date'].fields.append(_REMAPS.fields_by_name['no_accrued_remap_cooldown_at'])
_REMAPS.fields_by_name['no_accrued_remap_cooldown_at'].containing_oneof = _REMAPS.oneofs_by_name['accrued_remap_cooldown_date']
DESCRIPTOR.message_types_by_name['Values'] = _VALUES
DESCRIPTOR.message_types_by_name['Remaps'] = _REMAPS
DESCRIPTOR.enum_types_by_name['Type'] = _TYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Values = _reflection.GeneratedProtocolMessageType('Values', (_message.Message,), {'DESCRIPTOR': _VALUES,
 '__module__': 'eve.skill.character_attributes_pb2'})
_sym_db.RegisterMessage(Values)
Remaps = _reflection.GeneratedProtocolMessageType('Remaps', (_message.Message,), {'DESCRIPTOR': _REMAPS,
 '__module__': 'eve.skill.character_attributes_pb2'})
_sym_db.RegisterMessage(Remaps)
DESCRIPTOR._options = None
