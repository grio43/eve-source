#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\sovereignty\skyhook\workforce_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/sovereignty/skyhook/workforce.proto', package='eve_public.sovereignty.skyhook', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/skyhook', create_key=_descriptor._internal_create_key, serialized_pb='\n.eve_public/sovereignty/skyhook/workforce.proto\x12\x1eeve_public.sovereignty.skyhook":\n\tWorkforce\x12\x10\n\x06amount\x18\x01 \x01(\x04H\x00\x12\x0e\n\x04none\x18\x02 \x01(\x08H\x00B\x0b\n\tavailableBKZIgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/skyhookb\x06proto3')
_WORKFORCE = _descriptor.Descriptor(name='Workforce', full_name='eve_public.sovereignty.skyhook.Workforce', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve_public.sovereignty.skyhook.Workforce.amount', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='none', full_name='eve_public.sovereignty.skyhook.Workforce.none', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='available', full_name='eve_public.sovereignty.skyhook.Workforce.available', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=82, serialized_end=140)
_WORKFORCE.oneofs_by_name['available'].fields.append(_WORKFORCE.fields_by_name['amount'])
_WORKFORCE.fields_by_name['amount'].containing_oneof = _WORKFORCE.oneofs_by_name['available']
_WORKFORCE.oneofs_by_name['available'].fields.append(_WORKFORCE.fields_by_name['none'])
_WORKFORCE.fields_by_name['none'].containing_oneof = _WORKFORCE.oneofs_by_name['available']
DESCRIPTOR.message_types_by_name['Workforce'] = _WORKFORCE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Workforce = _reflection.GeneratedProtocolMessageType('Workforce', (_message.Message,), {'DESCRIPTOR': _WORKFORCE,
 '__module__': 'eve_public.sovereignty.skyhook.workforce_pb2'})
_sym_db.RegisterMessage(Workforce)
DESCRIPTOR._options = None
