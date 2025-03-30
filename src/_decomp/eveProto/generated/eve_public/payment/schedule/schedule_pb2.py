#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\schedule\schedule_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.store.offer import offer_pb2 as eve__public_dot_store_dot_offer_dot_offer__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/schedule/schedule.proto', package='eve_public.payment.schedule', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/schedule', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve_public/payment/schedule/schedule.proto\x12\x1beve_public.payment.schedule\x1a"eve_public/store/offer/offer.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\xae\x02\n\nAttributes\x12/\n\x04type\x18\x01 \x01(\x0e2!.eve_public.payment.schedule.Type\x120\n\x0cnext_payment\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x121\n\x05offer\x18\x03 \x01(\x0b2".eve_public.store.offer.Identifier\x12\x1f\n\x17recurring_interval_days\x18\x04 \x01(\r\x12+\n\x07created\x18\x05 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12<\n\x18last_purchase_completion\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp*,\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nTYPE_OMEGA\x10\x01BHZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/scheduleb\x06proto3', dependencies=[eve__public_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_TYPE = _descriptor.EnumDescriptor(name='Type', full_name='eve_public.payment.schedule.Type', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TYPE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='TYPE_OMEGA', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=483, serialized_end=527)
_sym_db.RegisterEnumDescriptor(_TYPE)
Type = enum_type_wrapper.EnumTypeWrapper(_TYPE)
TYPE_UNSPECIFIED = 0
TYPE_OMEGA = 1
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.payment.schedule.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve_public.payment.schedule.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=144, serialized_end=176)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve_public.payment.schedule.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve_public.payment.schedule.Attributes.type', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='next_payment', full_name='eve_public.payment.schedule.Attributes.next_payment', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve_public.payment.schedule.Attributes.offer', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recurring_interval_days', full_name='eve_public.payment.schedule.Attributes.recurring_interval_days', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='created', full_name='eve_public.payment.schedule.Attributes.created', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_purchase_completion', full_name='eve_public.payment.schedule.Attributes.last_purchase_completion', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=179, serialized_end=481)
_ATTRIBUTES.fields_by_name['type'].enum_type = _TYPE
_ATTRIBUTES.fields_by_name['next_payment'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['offer'].message_type = eve__public_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['created'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['last_purchase_completion'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['Type'] = _TYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.payment.schedule.schedule_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve_public.payment.schedule.schedule_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
