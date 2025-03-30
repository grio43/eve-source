#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\activity_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/activity.proto', package='eve.industry.activity', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/industry/activity', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/industry/activity.proto\x12\x15eve.industry.activity"N\n\x05Index\x121\n\x08activity\x18\x01 \x01(\x0e2\x1f.eve.industry.activity.Activity\x12\x12\n\ncost_index\x18\x02 \x01(\x02*~\n\x08Activity\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x11\n\rMANUFACTURING\x10\x01\x12\x11\n\rRESEARCH_TIME\x10\x03\x12\x15\n\x11RESEARCH_MATERIAL\x10\x04\x12\x0b\n\x07COPYING\x10\x05\x12\r\n\tINVENTION\x10\x08\x12\x0c\n\x08REACTION\x10\tBBZ@github.com/ccpgames/eve-proto-go/generated/eve/industry/activityb\x06proto3')
_ACTIVITY = _descriptor.EnumDescriptor(name='Activity', full_name='eve.industry.activity.Activity', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNKNOWN', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='MANUFACTURING', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='RESEARCH_TIME', index=2, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='RESEARCH_MATERIAL', index=3, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='COPYING', index=4, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='INVENTION', index=5, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='REACTION', index=6, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=134, serialized_end=260)
_sym_db.RegisterEnumDescriptor(_ACTIVITY)
Activity = enum_type_wrapper.EnumTypeWrapper(_ACTIVITY)
UNKNOWN = 0
MANUFACTURING = 1
RESEARCH_TIME = 3
RESEARCH_MATERIAL = 4
COPYING = 5
INVENTION = 8
REACTION = 9
_INDEX = _descriptor.Descriptor(name='Index', full_name='eve.industry.activity.Index', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='activity', full_name='eve.industry.activity.Index.activity', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='cost_index', full_name='eve.industry.activity.Index.cost_index', index=1, number=2, type=2, cpp_type=6, label=1, has_default_value=False, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=54, serialized_end=132)
_INDEX.fields_by_name['activity'].enum_type = _ACTIVITY
DESCRIPTOR.message_types_by_name['Index'] = _INDEX
DESCRIPTOR.enum_types_by_name['Activity'] = _ACTIVITY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Index = _reflection.GeneratedProtocolMessageType('Index', (_message.Message,), {'DESCRIPTOR': _INDEX,
 '__module__': 'eve.industry.activity_pb2'})
_sym_db.RegisterMessage(Index)
DESCRIPTOR._options = None
