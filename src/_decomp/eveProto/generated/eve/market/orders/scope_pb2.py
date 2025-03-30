#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\market\orders\scope_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/market/orders/scope.proto', package='eve.market.orders.scope', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/market/orders/scope', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/market/orders/scope.proto\x12\x17eve.market.orders.scope"g\n\nIdentifier\x12\x15\n\x0bin_location\x18\x01 \x01(\x08H\x00\x12\x10\n\x06region\x18\x02 \x01(\x08H\x00\x12\x16\n\x0csolar_system\x18\x03 \x01(\x08H\x00\x12\x0f\n\x05jumps\x18\x04 \x01(\rH\x00B\x07\n\x05scopeBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/market/orders/scopeb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.market.orders.scope.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='in_location', full_name='eve.market.orders.scope.Identifier.in_location', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='region', full_name='eve.market.orders.scope.Identifier.region', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.market.orders.scope.Identifier.solar_system', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='jumps', full_name='eve.market.orders.scope.Identifier.jumps', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='scope', full_name='eve.market.orders.scope.Identifier.scope', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=58, serialized_end=161)
_IDENTIFIER.oneofs_by_name['scope'].fields.append(_IDENTIFIER.fields_by_name['in_location'])
_IDENTIFIER.fields_by_name['in_location'].containing_oneof = _IDENTIFIER.oneofs_by_name['scope']
_IDENTIFIER.oneofs_by_name['scope'].fields.append(_IDENTIFIER.fields_by_name['region'])
_IDENTIFIER.fields_by_name['region'].containing_oneof = _IDENTIFIER.oneofs_by_name['scope']
_IDENTIFIER.oneofs_by_name['scope'].fields.append(_IDENTIFIER.fields_by_name['solar_system'])
_IDENTIFIER.fields_by_name['solar_system'].containing_oneof = _IDENTIFIER.oneofs_by_name['scope']
_IDENTIFIER.oneofs_by_name['scope'].fields.append(_IDENTIFIER.fields_by_name['jumps'])
_IDENTIFIER.fields_by_name['jumps'].containing_oneof = _IDENTIFIER.oneofs_by_name['scope']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.market.orders.scope_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
