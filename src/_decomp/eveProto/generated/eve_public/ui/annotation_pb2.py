#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\ui\annotation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/ui/annotation.proto', package='eve_public.ui', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve_public/ui', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve_public/ui/annotation.proto\x12\reve_public.ui"(\n\nAnnotation\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\tB:Z8github.com/ccpgames/eve-proto-go/generated/eve_public/uib\x06proto3')
_ANNOTATION = _descriptor.Descriptor(name='Annotation', full_name='eve_public.ui.Annotation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='key', full_name='eve_public.ui.Annotation.key', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='value', full_name='eve_public.ui.Annotation.value', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=49, serialized_end=89)
DESCRIPTOR.message_types_by_name['Annotation'] = _ANNOTATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Annotation = _reflection.GeneratedProtocolMessageType('Annotation', (_message.Message,), {'DESCRIPTOR': _ANNOTATION,
 '__module__': 'eve_public.ui.annotation_pb2'})
_sym_db.RegisterMessage(Annotation)
DESCRIPTOR._options = None
