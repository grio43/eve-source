#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\schedule\notices_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.payment.schedule import schedule_pb2 as eve__public_dot_payment_dot_schedule_dot_schedule__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/schedule/notices.proto', package='eve_public.payment.schedule.api', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/schedule/api', create_key=_descriptor._internal_create_key, serialized_pb='\n)eve_public/payment/schedule/notices.proto\x12\x1feve_public.payment.schedule.api\x1a*eve_public/payment/schedule/schedule.proto"}\n\x0fCancelledNotice\x129\n\x08schedule\x18\x01 \x01(\x0b2\'.eve_public.payment.schedule.Identifier\x12/\n\x04type\x18\x02 \x01(\x0e2!.eve_public.payment.schedule.TypeBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/schedule/apib\x06proto3', dependencies=[eve__public_dot_payment_dot_schedule_dot_schedule__pb2.DESCRIPTOR])
_CANCELLEDNOTICE = _descriptor.Descriptor(name='CancelledNotice', full_name='eve_public.payment.schedule.api.CancelledNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='schedule', full_name='eve_public.payment.schedule.api.CancelledNotice.schedule', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='type', full_name='eve_public.payment.schedule.api.CancelledNotice.type', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=247)
_CANCELLEDNOTICE.fields_by_name['schedule'].message_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._IDENTIFIER
_CANCELLEDNOTICE.fields_by_name['type'].enum_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._TYPE
DESCRIPTOR.message_types_by_name['CancelledNotice'] = _CANCELLEDNOTICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CancelledNotice = _reflection.GeneratedProtocolMessageType('CancelledNotice', (_message.Message,), {'DESCRIPTOR': _CANCELLEDNOTICE,
 '__module__': 'eve_public.payment.schedule.notices_pb2'})
_sym_db.RegisterMessage(CancelledNotice)
DESCRIPTOR._options = None
