#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\struct_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='google/protobuf/struct.proto', package='google.protobuf', syntax='proto3', serialized_options='\n\x13com.google.protobufB\x0bStructProtoP\x01Z/google.golang.org/protobuf/types/known/structpb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypes', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1cgoogle/protobuf/struct.proto\x12\x0fgoogle.protobuf"\x84\x01\n\x06Struct\x123\n\x06fields\x18\x01 \x03(\x0b2#.google.protobuf.Struct.FieldsEntry\x1aE\n\x0bFieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b2\x16.google.protobuf.Value:\x028\x01"\xea\x01\n\x05Value\x120\n\nnull_value\x18\x01 \x01(\x0e2\x1a.google.protobuf.NullValueH\x00\x12\x16\n\x0cnumber_value\x18\x02 \x01(\x01H\x00\x12\x16\n\x0cstring_value\x18\x03 \x01(\tH\x00\x12\x14\n\nbool_value\x18\x04 \x01(\x08H\x00\x12/\n\x0cstruct_value\x18\x05 \x01(\x0b2\x17.google.protobuf.StructH\x00\x120\n\nlist_value\x18\x06 \x01(\x0b2\x1a.google.protobuf.ListValueH\x00B\x06\n\x04kind"3\n\tListValue\x12&\n\x06values\x18\x01 \x03(\x0b2\x16.google.protobuf.Value*\x1b\n\tNullValue\x12\x0e\n\nNULL_VALUE\x10\x00B\x7f\n\x13com.google.protobufB\x0bStructProtoP\x01Z/google.golang.org/protobuf/types/known/structpb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesb\x06proto3')
_NULLVALUE = _descriptor.EnumDescriptor(name='NullValue', full_name='google.protobuf.NullValue', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='NULL_VALUE', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=474, serialized_end=501)
_sym_db.RegisterEnumDescriptor(_NULLVALUE)
NullValue = enum_type_wrapper.EnumTypeWrapper(_NULLVALUE)
NULL_VALUE = 0
_STRUCT_FIELDSENTRY = _descriptor.Descriptor(name='FieldsEntry', full_name='google.protobuf.Struct.FieldsEntry', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='key', full_name='google.protobuf.Struct.FieldsEntry.key', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='value', full_name='google.protobuf.Struct.FieldsEntry.value', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='8\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=113, serialized_end=182)
_STRUCT = _descriptor.Descriptor(name='Struct', full_name='google.protobuf.Struct', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='fields', full_name='google.protobuf.Struct.fields', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_STRUCT_FIELDSENTRY], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=50, serialized_end=182)
_VALUE = _descriptor.Descriptor(name='Value', full_name='google.protobuf.Value', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='null_value', full_name='google.protobuf.Value.null_value', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='number_value', full_name='google.protobuf.Value.number_value', index=1, number=2, type=1, cpp_type=5, label=1, has_default_value=False, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='string_value', full_name='google.protobuf.Value.string_value', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='bool_value', full_name='google.protobuf.Value.bool_value', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='struct_value', full_name='google.protobuf.Value.struct_value', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='list_value', full_name='google.protobuf.Value.list_value', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='kind', full_name='google.protobuf.Value.kind', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=185, serialized_end=419)
_LISTVALUE = _descriptor.Descriptor(name='ListValue', full_name='google.protobuf.ListValue', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='values', full_name='google.protobuf.ListValue.values', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=421, serialized_end=472)
_STRUCT_FIELDSENTRY.fields_by_name['value'].message_type = _VALUE
_STRUCT_FIELDSENTRY.containing_type = _STRUCT
_STRUCT.fields_by_name['fields'].message_type = _STRUCT_FIELDSENTRY
_VALUE.fields_by_name['null_value'].enum_type = _NULLVALUE
_VALUE.fields_by_name['struct_value'].message_type = _STRUCT
_VALUE.fields_by_name['list_value'].message_type = _LISTVALUE
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['null_value'])
_VALUE.fields_by_name['null_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['number_value'])
_VALUE.fields_by_name['number_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['string_value'])
_VALUE.fields_by_name['string_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['bool_value'])
_VALUE.fields_by_name['bool_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['struct_value'])
_VALUE.fields_by_name['struct_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_VALUE.oneofs_by_name['kind'].fields.append(_VALUE.fields_by_name['list_value'])
_VALUE.fields_by_name['list_value'].containing_oneof = _VALUE.oneofs_by_name['kind']
_LISTVALUE.fields_by_name['values'].message_type = _VALUE
DESCRIPTOR.message_types_by_name['Struct'] = _STRUCT
DESCRIPTOR.message_types_by_name['Value'] = _VALUE
DESCRIPTOR.message_types_by_name['ListValue'] = _LISTVALUE
DESCRIPTOR.enum_types_by_name['NullValue'] = _NULLVALUE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Struct = _reflection.GeneratedProtocolMessageType('Struct', (_message.Message,), {'FieldsEntry': _reflection.GeneratedProtocolMessageType('FieldsEntry', (_message.Message,), {'DESCRIPTOR': _STRUCT_FIELDSENTRY,
                 '__module__': 'google.protobuf.struct_pb2'}),
 'DESCRIPTOR': _STRUCT,
 '__module__': 'google.protobuf.struct_pb2'})
_sym_db.RegisterMessage(Struct)
_sym_db.RegisterMessage(Struct.FieldsEntry)
Value = _reflection.GeneratedProtocolMessageType('Value', (_message.Message,), {'DESCRIPTOR': _VALUE,
 '__module__': 'google.protobuf.struct_pb2'})
_sym_db.RegisterMessage(Value)
ListValue = _reflection.GeneratedProtocolMessageType('ListValue', (_message.Message,), {'DESCRIPTOR': _LISTVALUE,
 '__module__': 'google.protobuf.struct_pb2'})
_sym_db.RegisterMessage(ListValue)
DESCRIPTOR._options = None
_STRUCT_FIELDSENTRY._options = None
