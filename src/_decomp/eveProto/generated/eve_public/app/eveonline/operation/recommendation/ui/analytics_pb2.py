#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\operation\recommendation\ui\analytics_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.operation import operation_pb2 as eve__public_dot_operation_dot_operation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/operation/recommendation/ui/analytics.proto', package='eve_public.app.eveonline.operation.recommendation.ui.analytics', syntax='proto3', serialized_options='Zigithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/operation/recommendation/ui/analytics', create_key=_descriptor._internal_create_key, serialized_pb='\nDeve_public/app/eveonline/operation/recommendation/ui/analytics.proto\x12>eve_public.app.eveonline.operation.recommendation.ui.analytics\x1a$eve_public/operation/operation.proto"E\n\tDisplayed\x124\n\noperations\x18\x01 \x03(\x0b2 .eve_public.operation.Identifier:\x02\x18\x01BkZigithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/operation/recommendation/ui/analyticsb\x06proto3', dependencies=[eve__public_dot_operation_dot_operation__pb2.DESCRIPTOR])
_DISPLAYED = _descriptor.Descriptor(name='Displayed', full_name='eve_public.app.eveonline.operation.recommendation.ui.analytics.Displayed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operations', full_name='eve_public.app.eveonline.operation.recommendation.ui.analytics.Displayed.operations', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=174, serialized_end=243)
_DISPLAYED.fields_by_name['operations'].message_type = eve__public_dot_operation_dot_operation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Displayed'] = _DISPLAYED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Displayed = _reflection.GeneratedProtocolMessageType('Displayed', (_message.Message,), {'DESCRIPTOR': _DISPLAYED,
 '__module__': 'eve_public.app.eveonline.operation.recommendation.ui.analytics_pb2'})
_sym_db.RegisterMessage(Displayed)
DESCRIPTOR._options = None
_DISPLAYED._options = None
