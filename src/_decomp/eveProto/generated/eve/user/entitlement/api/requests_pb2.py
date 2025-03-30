#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\entitlement\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.fulfillment.sale import sale_pb2 as eve_dot_fulfillment_dot_sale_dot_sale__pb2
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
from eveProto.generated.eve.user.entitlement import entitlement_pb2 as eve_dot_user_dot_entitlement_dot_entitlement__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/entitlement/api/requests.proto', package='eve.user.entitlement.api', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/user/entitlement/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/user/entitlement/api/requests.proto\x12\x18eve.user.entitlement.api\x1a\x1feve/fulfillment/sale/sale.proto\x1a\x19eve/payment/payment.proto\x1a&eve/user/entitlement/entitlement.proto\x1a\x13eve/user/user.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto">\n\x14GetAllForUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier:\x02\x18\x01"T\n\x15GetAllForUserResponse\x127\n\x0centitlements\x18\x01 \x03(\x0b2!.eve.user.entitlement.Entitlement:\x02\x18\x01"\x91\x02\n\x0cGrantRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12\x0c\n\x04name\x18\x02 \x01(\t\x121\n\x0bexpiry_date\x18\x03 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x121\n\x0cadd_duration\x18\x04 \x01(\x0b2\x19.google.protobuf.DurationH\x00\x12+\n\x0epayment_method\x18\x05 \x01(\x0e2\x13.eve.payment.Method\x12.\n\x04sale\x18\x06 \x01(\x0b2 .eve.fulfillment.sale.Identifier:\x02\x18\x01B\x08\n\x06expiry"\x13\n\rGrantResponse:\x02\x18\x01"\x7f\n\x13AddOmegatimeRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12+\n\x08duration\x18\x02 \x01(\x0b2\x19.google.protobuf.Duration\x12\x13\n\x0bdescription\x18\x03 \x01(\t:\x02\x18\x01"\x1a\n\x14AddOmegatimeResponse:\x02\x18\x01BEZCgithub.com/ccpgames/eve-proto-go/generated/eve/user/entitlement/apib\x06proto3', dependencies=[eve_dot_fulfillment_dot_sale_dot_sale__pb2.DESCRIPTOR,
 eve_dot_payment_dot_payment__pb2.DESCRIPTOR,
 eve_dot_user_dot_entitlement_dot_entitlement__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GETALLFORUSERREQUEST = _descriptor.Descriptor(name='GetAllForUserRequest', full_name='eve.user.entitlement.api.GetAllForUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.entitlement.api.GetAllForUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=255, serialized_end=317)
_GETALLFORUSERRESPONSE = _descriptor.Descriptor(name='GetAllForUserResponse', full_name='eve.user.entitlement.api.GetAllForUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlements', full_name='eve.user.entitlement.api.GetAllForUserResponse.entitlements', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=319, serialized_end=403)
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve.user.entitlement.api.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.entitlement.api.GrantRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='name', full_name='eve.user.entitlement.api.GrantRequest.name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expiry_date', full_name='eve.user.entitlement.api.GrantRequest.expiry_date', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='add_duration', full_name='eve.user.entitlement.api.GrantRequest.add_duration', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_method', full_name='eve.user.entitlement.api.GrantRequest.payment_method', index=4, number=5, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sale', full_name='eve.user.entitlement.api.GrantRequest.sale', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='expiry', full_name='eve.user.entitlement.api.GrantRequest.expiry', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=406, serialized_end=679)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve.user.entitlement.api.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=681, serialized_end=700)
_ADDOMEGATIMEREQUEST = _descriptor.Descriptor(name='AddOmegatimeRequest', full_name='eve.user.entitlement.api.AddOmegatimeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.entitlement.api.AddOmegatimeRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='duration', full_name='eve.user.entitlement.api.AddOmegatimeRequest.duration', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='description', full_name='eve.user.entitlement.api.AddOmegatimeRequest.description', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=702, serialized_end=829)
_ADDOMEGATIMERESPONSE = _descriptor.Descriptor(name='AddOmegatimeResponse', full_name='eve.user.entitlement.api.AddOmegatimeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=831, serialized_end=857)
_GETALLFORUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETALLFORUSERRESPONSE.fields_by_name['entitlements'].message_type = eve_dot_user_dot_entitlement_dot_entitlement__pb2._ENTITLEMENT
_GRANTREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GRANTREQUEST.fields_by_name['expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GRANTREQUEST.fields_by_name['add_duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_GRANTREQUEST.fields_by_name['payment_method'].enum_type = eve_dot_payment_dot_payment__pb2._METHOD
_GRANTREQUEST.fields_by_name['sale'].message_type = eve_dot_fulfillment_dot_sale_dot_sale__pb2._IDENTIFIER
_GRANTREQUEST.oneofs_by_name['expiry'].fields.append(_GRANTREQUEST.fields_by_name['expiry_date'])
_GRANTREQUEST.fields_by_name['expiry_date'].containing_oneof = _GRANTREQUEST.oneofs_by_name['expiry']
_GRANTREQUEST.oneofs_by_name['expiry'].fields.append(_GRANTREQUEST.fields_by_name['add_duration'])
_GRANTREQUEST.fields_by_name['add_duration'].containing_oneof = _GRANTREQUEST.oneofs_by_name['expiry']
_ADDOMEGATIMEREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ADDOMEGATIMEREQUEST.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
DESCRIPTOR.message_types_by_name['GetAllForUserRequest'] = _GETALLFORUSERREQUEST
DESCRIPTOR.message_types_by_name['GetAllForUserResponse'] = _GETALLFORUSERRESPONSE
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
DESCRIPTOR.message_types_by_name['AddOmegatimeRequest'] = _ADDOMEGATIMEREQUEST
DESCRIPTOR.message_types_by_name['AddOmegatimeResponse'] = _ADDOMEGATIMERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllForUserRequest = _reflection.GeneratedProtocolMessageType('GetAllForUserRequest', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERREQUEST,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllForUserRequest)
GetAllForUserResponse = _reflection.GeneratedProtocolMessageType('GetAllForUserResponse', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERRESPONSE,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllForUserResponse)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GrantResponse)
AddOmegatimeRequest = _reflection.GeneratedProtocolMessageType('AddOmegatimeRequest', (_message.Message,), {'DESCRIPTOR': _ADDOMEGATIMEREQUEST,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(AddOmegatimeRequest)
AddOmegatimeResponse = _reflection.GeneratedProtocolMessageType('AddOmegatimeResponse', (_message.Message,), {'DESCRIPTOR': _ADDOMEGATIMERESPONSE,
 '__module__': 'eve.user.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(AddOmegatimeResponse)
DESCRIPTOR._options = None
_GETALLFORUSERREQUEST._options = None
_GETALLFORUSERRESPONSE._options = None
_GRANTREQUEST._options = None
_GRANTRESPONSE._options = None
_ADDOMEGATIMEREQUEST._options = None
_ADDOMEGATIMERESPONSE._options = None
