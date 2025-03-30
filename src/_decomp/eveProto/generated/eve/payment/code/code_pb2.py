#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\payment\code\code_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/payment/code/code.proto', package='eve.payment.code', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/payment/code', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/payment/code/code.proto\x12\x10eve.payment.code\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04code\x18\x01 \x01(\t"\xd7\x01\n\nAttributes\x12/\n\x0bcreate_date\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x10\n\x08reseller\x18\x02 \x01(\t\x12/\n\x04type\x18\x03 \x01(\x0b2!.eve.payment.code.Attributes.Type\x12*\n\x05group\x18\x04 \x01(\x0e2\x1b.eve.payment.code.CodeGroup\x1a)\n\x04Type\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t*I\n\tCodeGroup\x12\x15\n\x11GROUP_UNSPECIFIED\x10\x00\x12\x12\n\x0eGROUP_INTERNAL\x10\x01\x12\x11\n\rGROUP_FINANCE\x10\x02B=Z;github.com/ccpgames/eve-proto-go/generated/eve/payment/codeb\x06proto3', dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_CODEGROUP = _descriptor.EnumDescriptor(name='CodeGroup', full_name='eve.payment.code.CodeGroup', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='GROUP_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='GROUP_INTERNAL', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='GROUP_FINANCE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=328, serialized_end=401)
_sym_db.RegisterEnumDescriptor(_CODEGROUP)
CodeGroup = enum_type_wrapper.EnumTypeWrapper(_CODEGROUP)
GROUP_UNSPECIFIED = 0
GROUP_INTERNAL = 1
GROUP_FINANCE = 2
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.payment.code.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='code', full_name='eve.payment.code.Identifier.code', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=82, serialized_end=108)
_ATTRIBUTES_TYPE = _descriptor.Descriptor(name='Type', full_name='eve.payment.code.Attributes.Type', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.payment.code.Attributes.Type.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='description', full_name='eve.payment.code.Attributes.Type.description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=285, serialized_end=326)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.payment.code.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='create_date', full_name='eve.payment.code.Attributes.create_date', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reseller', full_name='eve.payment.code.Attributes.reseller', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='type', full_name='eve.payment.code.Attributes.type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='group', full_name='eve.payment.code.Attributes.group', index=3, number=4, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ATTRIBUTES_TYPE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=111, serialized_end=326)
_ATTRIBUTES_TYPE.containing_type = _ATTRIBUTES
_ATTRIBUTES.fields_by_name['create_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['type'].message_type = _ATTRIBUTES_TYPE
_ATTRIBUTES.fields_by_name['group'].enum_type = _CODEGROUP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['CodeGroup'] = _CODEGROUP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.payment.code.code_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'Type': _reflection.GeneratedProtocolMessageType('Type', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES_TYPE,
          '__module__': 'eve.payment.code.code_pb2'}),
 'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.payment.code.code_pb2'})
_sym_db.RegisterMessage(Attributes)
_sym_db.RegisterMessage(Attributes.Type)
DESCRIPTOR._options = None
