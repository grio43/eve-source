#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\schedule\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.payment.schedule import schedule_pb2 as eve__public_dot_payment_dot_schedule_dot_schedule__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/schedule/requests.proto', package='eve_public.payment.schedule.api', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/schedule/api', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve_public/payment/schedule/requests.proto\x12\x1feve_public.payment.schedule.api\x1a*eve_public/payment/schedule/schedule.proto"G\n\nGetRequest\x129\n\x08schedule\x18\x01 \x01(\x0b2\'.eve_public.payment.schedule.Identifier"J\n\x0bGetResponse\x12;\n\nattributes\x18\x01 \x01(\x0b2\'.eve_public.payment.schedule.Attributes"I\n\x16GetActiveByTypeRequest\x12/\n\x04type\x18\x01 \x01(\x0e2!.eve_public.payment.schedule.Type"T\n\x17GetActiveByTypeResponse\x129\n\x08schedule\x18\x01 \x01(\x0b2\'.eve_public.payment.schedule.IdentifierBLZJgithub.com/ccpgames/eve-proto-go/generated/eve_public/payment/schedule/apib\x06proto3', dependencies=[eve__public_dot_payment_dot_schedule_dot_schedule__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.payment.schedule.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='schedule', full_name='eve_public.payment.schedule.api.GetRequest.schedule', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=123, serialized_end=194)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.payment.schedule.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve_public.payment.schedule.api.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=196, serialized_end=270)
_GETACTIVEBYTYPEREQUEST = _descriptor.Descriptor(name='GetActiveByTypeRequest', full_name='eve_public.payment.schedule.api.GetActiveByTypeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve_public.payment.schedule.api.GetActiveByTypeRequest.type', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=272, serialized_end=345)
_GETACTIVEBYTYPERESPONSE = _descriptor.Descriptor(name='GetActiveByTypeResponse', full_name='eve_public.payment.schedule.api.GetActiveByTypeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='schedule', full_name='eve_public.payment.schedule.api.GetActiveByTypeResponse.schedule', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=347, serialized_end=431)
_GETREQUEST.fields_by_name['schedule'].message_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._ATTRIBUTES
_GETACTIVEBYTYPEREQUEST.fields_by_name['type'].enum_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._TYPE
_GETACTIVEBYTYPERESPONSE.fields_by_name['schedule'].message_type = eve__public_dot_payment_dot_schedule_dot_schedule__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetActiveByTypeRequest'] = _GETACTIVEBYTYPEREQUEST
DESCRIPTOR.message_types_by_name['GetActiveByTypeResponse'] = _GETACTIVEBYTYPERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.payment.schedule.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.payment.schedule.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetActiveByTypeRequest = _reflection.GeneratedProtocolMessageType('GetActiveByTypeRequest', (_message.Message,), {'DESCRIPTOR': _GETACTIVEBYTYPEREQUEST,
 '__module__': 'eve_public.payment.schedule.requests_pb2'})
_sym_db.RegisterMessage(GetActiveByTypeRequest)
GetActiveByTypeResponse = _reflection.GeneratedProtocolMessageType('GetActiveByTypeResponse', (_message.Message,), {'DESCRIPTOR': _GETACTIVEBYTYPERESPONSE,
 '__module__': 'eve_public.payment.schedule.requests_pb2'})
_sym_db.RegisterMessage(GetActiveByTypeResponse)
DESCRIPTOR._options = None
