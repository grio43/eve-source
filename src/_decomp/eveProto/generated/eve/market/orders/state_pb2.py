#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\market\orders\state_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/market/orders/state.proto', package='eve.market.orders.state', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/market/orders/state', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/market/orders/state.proto\x12\x17eve.market.orders.state*i\n\x04Flag\x12\x0b\n\x07INVALID\x10\x00\x12\x08\n\x04OPEN\x10\x01\x12\x0b\n\x07EXPIRED\x10\x02\x12\r\n\tCANCELLED\x10\x03\x12\x0b\n\x07PENDING\x10\x04\x12\x15\n\x11CHARACTER_DELETED\x10\x05\x12\n\n\x06CLOSED\x10\x06BDZBgithub.com/ccpgames/eve-proto-go/generated/eve/market/orders/stateb\x06proto3')
_FLAG = _descriptor.EnumDescriptor(name='Flag', full_name='eve.market.orders.state.Flag', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='INVALID', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='OPEN', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='EXPIRED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CANCELLED', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PENDING', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CHARACTER_DELETED', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLOSED', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=58, serialized_end=163)
_sym_db.RegisterEnumDescriptor(_FLAG)
Flag = enum_type_wrapper.EnumTypeWrapper(_FLAG)
INVALID = 0
OPEN = 1
EXPIRED = 2
CANCELLED = 3
PENDING = 4
CHARACTER_DELETED = 5
CLOSED = 6
DESCRIPTOR.enum_types_by_name['Flag'] = _FLAG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
