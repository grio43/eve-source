#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\role_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/role.proto', package='eve.corporation.role', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/corporation/role', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/corporation/role.proto\x12\x14eve.corporation.role"\x1a\n\nCollection\x12\x0c\n\x04mask\x18\x01 \x01(\x04*\xcc\x01\n\x04Type\x12\x10\n\x0cTYPE_INVALID\x10\x00\x12\x0f\n\x0bTYPE_AT_ALL\x10\x01\x12\x10\n\x0cTYPE_AT_BASE\x10\x02\x12\x0e\n\nTYPE_AT_HQ\x10\x03\x12\x11\n\rTYPE_AT_OTHER\x10\x04\x12\x19\n\x15TYPE_GRANTABLE_AT_ALL\x10\x05\x12\x1a\n\x16TYPE_GRANTABLE_AT_BASE\x10\x06\x12\x18\n\x14TYPE_GRANTABLE_AT_HQ\x10\x07\x12\x1b\n\x17TYPE_GRANTABLE_AT_OTHER\x10\x08BAZ?github.com/ccpgames/eve-proto-go/generated/eve/corporation/roleb\x06proto3')
_TYPE = _descriptor.EnumDescriptor(name='Type', full_name='eve.corporation.role.Type', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TYPE_INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_AT_ALL', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_AT_BASE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_AT_HQ', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_AT_OTHER', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_GRANTABLE_AT_ALL', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_GRANTABLE_AT_BASE', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_GRANTABLE_AT_HQ', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_GRANTABLE_AT_OTHER', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=81, serialized_end=285)
_sym_db.RegisterEnumDescriptor(_TYPE)
Type = enum_type_wrapper.EnumTypeWrapper(_TYPE)
TYPE_INVALID = 0
TYPE_AT_ALL = 1
TYPE_AT_BASE = 2
TYPE_AT_HQ = 3
TYPE_AT_OTHER = 4
TYPE_GRANTABLE_AT_ALL = 5
TYPE_GRANTABLE_AT_BASE = 6
TYPE_GRANTABLE_AT_HQ = 7
TYPE_GRANTABLE_AT_OTHER = 8
_COLLECTION = _descriptor.Descriptor(name='Collection', full_name='eve.corporation.role.Collection', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='mask', full_name='eve.corporation.role.Collection.mask', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=52, serialized_end=78)
DESCRIPTOR.message_types_by_name['Collection'] = _COLLECTION
DESCRIPTOR.enum_types_by_name['Type'] = _TYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Collection = _reflection.GeneratedProtocolMessageType('Collection', (_message.Message,), {'DESCRIPTOR': _COLLECTION,
 '__module__': 'eve.corporation.role_pb2'})
_sym_db.RegisterMessage(Collection)
DESCRIPTOR._options = None
