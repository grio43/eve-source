#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\field_mask_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='google/protobuf/field_mask.proto', package='google.protobuf', syntax='proto3', serialized_options='\n\x13com.google.protobufB\x0eFieldMaskProtoP\x01Z2google.golang.org/protobuf/types/known/fieldmaskpb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypes', create_key=_descriptor._internal_create_key, serialized_pb='\n google/protobuf/field_mask.proto\x12\x0fgoogle.protobuf"\x1a\n\tFieldMask\x12\r\n\x05paths\x18\x01 \x03(\tB\x85\x01\n\x13com.google.protobufB\x0eFieldMaskProtoP\x01Z2google.golang.org/protobuf/types/known/fieldmaskpb\xf8\x01\x01\xa2\x02\x03GPB\xaa\x02\x1eGoogle.Protobuf.WellKnownTypesb\x06proto3')
_FIELDMASK = _descriptor.Descriptor(name='FieldMask', full_name='google.protobuf.FieldMask', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='paths', full_name='google.protobuf.FieldMask.paths', index=0, number=1, type=9, cpp_type=9, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=53, serialized_end=79)
DESCRIPTOR.message_types_by_name['FieldMask'] = _FIELDMASK
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
FieldMask = _reflection.GeneratedProtocolMessageType('FieldMask', (_message.Message,), {'DESCRIPTOR': _FIELDMASK,
 '__module__': 'google.protobuf.field_mask_pb2'})
_sym_db.RegisterMessage(FieldMask)
DESCRIPTOR._options = None
