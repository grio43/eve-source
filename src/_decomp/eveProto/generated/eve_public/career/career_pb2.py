#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\career\career_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/career/career.proto', package='eve_public.career', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve_public/career', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve_public/career/career.proto\x12\x11eve_public.career*\x84\x01\n\x04Path\x12\x16\n\x12CAREER_UNSPECIFIED\x10\x00\x12\x16\n\x12CAREER_EXPLORATION\x10\x01\x12\x18\n\x14CAREER_INDUSTRIALIST\x10\x02\x12\x13\n\x0fCAREER_ENFORCER\x10\x03\x12\x1d\n\x19CAREER_SOLDIER_OF_FORTUNE\x10\x04B>Z<github.com/ccpgames/eve-proto-go/generated/eve_public/careerb\x06proto3')
_PATH = _descriptor.EnumDescriptor(name='Path', full_name='eve_public.career.Path', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='CAREER_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CAREER_EXPLORATION', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CAREER_INDUSTRIALIST', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CAREER_ENFORCER', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CAREER_SOLDIER_OF_FORTUNE', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=54, serialized_end=186)
_sym_db.RegisterEnumDescriptor(_PATH)
Path = enum_type_wrapper.EnumTypeWrapper(_PATH)
CAREER_UNSPECIFIED = 0
CAREER_EXPLORATION = 1
CAREER_INDUSTRIALIST = 2
CAREER_ENFORCER = 3
CAREER_SOLDIER_OF_FORTUNE = 4
DESCRIPTOR.enum_types_by_name['Path'] = _PATH
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
