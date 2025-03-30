#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\module\module_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.module import module_type_pb2 as eve_dot_module_dot_module__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/module/module.proto', package='eve.module', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/module', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/module/module.proto\x12\neve.module\x1a\x1ceve/module/module_type.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"6\n\nAttributes\x12(\n\x04type\x18\x01 \x01(\x0b2\x1a.eve.moduletype.IdentifierB7Z5github.com/ccpgames/eve-proto-go/generated/eve/moduleb\x06proto3', dependencies=[eve_dot_module_dot_module__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.module.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.module.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=69, serialized_end=101)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.module.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.module.Attributes.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=103, serialized_end=157)
_ATTRIBUTES.fields_by_name['type'].message_type = eve_dot_module_dot_module__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.module.module_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.module.module_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
