#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\inventory\container\secure\secure_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/inventory/container/secure/secure.proto', package='eve.inventory.container.secure', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/container/secure', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/inventory/container/secure/secure.proto\x12\x1eeve.inventory.container.secure*^\n\x0cPasswordType\x12\x19\n\x15PASSWORD_TYPE_INVALID\x10\x00\x12\x19\n\x15PASSWORD_TYPE_GENERAL\x10\x01\x12\x18\n\x14PASSWORD_TYPE_CONFIG\x10\x02BKZIgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/container/secureb\x06proto3')
_PASSWORDTYPE = _descriptor.EnumDescriptor(name='PasswordType', full_name='eve.inventory.container.secure.PasswordType', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PASSWORD_TYPE_INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='PASSWORD_TYPE_GENERAL', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='PASSWORD_TYPE_CONFIG', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=79, serialized_end=173)
_sym_db.RegisterEnumDescriptor(_PASSWORDTYPE)
PasswordType = enum_type_wrapper.EnumTypeWrapper(_PASSWORDTYPE)
PASSWORD_TYPE_INVALID = 0
PASSWORD_TYPE_GENERAL = 1
PASSWORD_TYPE_CONFIG = 2
DESCRIPTOR.enum_types_by_name['PasswordType'] = _PASSWORDTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
