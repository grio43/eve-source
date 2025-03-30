#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\operation\recommendation\recommendation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.operation import operation_pb2 as eve__public_dot_operation_dot_operation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/operation/recommendation/recommendation.proto', package='eve_public.app.eveonline.operation.recommendation', syntax='proto3', serialized_options='Z\\github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/operation/recommendation', create_key=_descriptor._internal_create_key, serialized_pb='\nFeve_public/app/eveonline/operation/recommendation/recommendation.proto\x121eve_public.app.eveonline.operation.recommendation\x1a$eve_public/operation/operation.proto"?\n\x08Accepted\x123\n\toperation\x18\x01 \x01(\x0b2 .eve_public.operation.Identifier"@\n\tDismissed\x123\n\toperation\x18\x01 \x01(\x0b2 .eve_public.operation.IdentifierB^Z\\github.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/operation/recommendationb\x06proto3', dependencies=[eve__public_dot_operation_dot_operation__pb2.DESCRIPTOR])
_ACCEPTED = _descriptor.Descriptor(name='Accepted', full_name='eve_public.app.eveonline.operation.recommendation.Accepted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve_public.app.eveonline.operation.recommendation.Accepted.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=163, serialized_end=226)
_DISMISSED = _descriptor.Descriptor(name='Dismissed', full_name='eve_public.app.eveonline.operation.recommendation.Dismissed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve_public.app.eveonline.operation.recommendation.Dismissed.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=228, serialized_end=292)
_ACCEPTED.fields_by_name['operation'].message_type = eve__public_dot_operation_dot_operation__pb2._IDENTIFIER
_DISMISSED.fields_by_name['operation'].message_type = eve__public_dot_operation_dot_operation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Accepted'] = _ACCEPTED
DESCRIPTOR.message_types_by_name['Dismissed'] = _DISMISSED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Accepted = _reflection.GeneratedProtocolMessageType('Accepted', (_message.Message,), {'DESCRIPTOR': _ACCEPTED,
 '__module__': 'eve_public.app.eveonline.operation.recommendation.recommendation_pb2'})
_sym_db.RegisterMessage(Accepted)
Dismissed = _reflection.GeneratedProtocolMessageType('Dismissed', (_message.Message,), {'DESCRIPTOR': _DISMISSED,
 '__module__': 'eve_public.app.eveonline.operation.recommendation.recommendation_pb2'})
_sym_db.RegisterMessage(Dismissed)
DESCRIPTOR._options = None
