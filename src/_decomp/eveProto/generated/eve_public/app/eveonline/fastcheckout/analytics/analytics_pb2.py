#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\fastcheckout\analytics\analytics_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.user.commerce import purchase_pb2 as eve__public_dot_user_dot_commerce_dot_purchase__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/fastcheckout/analytics/analytics.proto', package='eve_public.app.eveonline.fastcheckout.analytics', syntax='proto3', serialized_options='ZZgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/fastcheckout/analytics', create_key=_descriptor._internal_create_key, serialized_pb='\n?eve_public/app/eveonline/fastcheckout/analytics/analytics.proto\x12/eve_public.app.eveonline.fastcheckout.analytics\x1a\'eve_public/user/commerce/purchase.proto"b\n\x07Context\x12?\n\x08purchase\x18\x01 \x01(\x0b2-.eve_public.user.commerce.purchase.Identifier\x12\x16\n\x0efeature_origin\x18\x02 \x01(\tB\\ZZgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/fastcheckout/analyticsb\x06proto3', dependencies=[eve__public_dot_user_dot_commerce_dot_purchase__pb2.DESCRIPTOR])
_CONTEXT = _descriptor.Descriptor(name='Context', full_name='eve_public.app.eveonline.fastcheckout.analytics.Context', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='purchase', full_name='eve_public.app.eveonline.fastcheckout.analytics.Context.purchase', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='feature_origin', full_name='eve_public.app.eveonline.fastcheckout.analytics.Context.feature_origin', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=157, serialized_end=255)
_CONTEXT.fields_by_name['purchase'].message_type = eve__public_dot_user_dot_commerce_dot_purchase__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Context'] = _CONTEXT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Context = _reflection.GeneratedProtocolMessageType('Context', (_message.Message,), {'DESCRIPTOR': _CONTEXT,
 '__module__': 'eve_public.app.eveonline.fastcheckout.analytics.analytics_pb2'})
_sym_db.RegisterMessage(Context)
DESCRIPTOR._options = None
