#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\license\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
from eveProto.generated.eve.user.license.grant import grant_pb2 as eve_dot_user_dot_license_dot_grant_dot_grant__pb2
from eveProto.generated.eve.user.license import license_pb2 as eve_dot_user_dot_license_dot_license__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/license/api/requests.proto', package='eve.user.license.api', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/user/license/api', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/user/license/api/requests.proto\x12\x14eve.user.license.api\x1a\x19eve/payment/payment.proto\x1a"eve/user/license/grant/grant.proto\x1a\x1eeve/user/license/license.proto\x1a\x13eve/user/user.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x8d\x02\n\x0cGrantRequest\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.Identifier\x121\n\x0bexpiry_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x121\n\x0cadd_duration\x18\x03 \x01(\x0b2\x19.google.protobuf.DurationH\x00\x12+\n\x0epayment_method\x18\x04 \x01(\x0e2\x13.eve.payment.Method\x121\n\x05grant\x18\x05 \x01(\x0b2".eve.user.license.grant.IdentifierB\x08\n\x06expiry"\x0f\n\rGrantResponse"\xca\x01\n\x14SetExpiryDateRequest\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.Identifier\x121\n\x0bexpiry_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x121\n\x0cadd_duration\x18\x03 \x01(\x0b2\x19.google.protobuf.DurationH\x00\x12\x13\n\x0bdescription\x18\x04 \x01(\tB\x08\n\x06expiry"F\n\x15SetExpiryDateResponse\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.Attributes":\n\x14GetAllForUserRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"G\n\x15GetAllForUserResponse\x12.\n\x08licenses\x18\x01 \x03(\x0b2\x1c.eve.user.license.Identifier";\n\nGetRequest\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.Identifier"<\n\x0bGetResponse\x12-\n\x07license\x18\x01 \x01(\x0b2\x1c.eve.user.license.AttributesBAZ?github.com/ccpgames/eve-proto-go/generated/eve/user/license/apib\x06proto3', dependencies=[eve_dot_payment_dot_payment__pb2.DESCRIPTOR,
 eve_dot_user_dot_license_dot_grant_dot_grant__pb2.DESCRIPTOR,
 eve_dot_user_dot_license_dot_license__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve.user.license.api.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.GrantRequest.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expiry_date', full_name='eve.user.license.api.GrantRequest.expiry_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='add_duration', full_name='eve.user.license.api.GrantRequest.add_duration', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_method', full_name='eve.user.license.api.GrantRequest.payment_method', index=3, number=4, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='grant', full_name='eve.user.license.api.GrantRequest.grant', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='expiry', full_name='eve.user.license.api.GrantRequest.expiry', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=243, serialized_end=512)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve.user.license.api.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=514, serialized_end=529)
_SETEXPIRYDATEREQUEST = _descriptor.Descriptor(name='SetExpiryDateRequest', full_name='eve.user.license.api.SetExpiryDateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.SetExpiryDateRequest.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expiry_date', full_name='eve.user.license.api.SetExpiryDateRequest.expiry_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='add_duration', full_name='eve.user.license.api.SetExpiryDateRequest.add_duration', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.user.license.api.SetExpiryDateRequest.description', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='expiry', full_name='eve.user.license.api.SetExpiryDateRequest.expiry', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=532, serialized_end=734)
_SETEXPIRYDATERESPONSE = _descriptor.Descriptor(name='SetExpiryDateResponse', full_name='eve.user.license.api.SetExpiryDateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.SetExpiryDateResponse.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=736, serialized_end=806)
_GETALLFORUSERREQUEST = _descriptor.Descriptor(name='GetAllForUserRequest', full_name='eve.user.license.api.GetAllForUserRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.license.api.GetAllForUserRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=808, serialized_end=866)
_GETALLFORUSERRESPONSE = _descriptor.Descriptor(name='GetAllForUserResponse', full_name='eve.user.license.api.GetAllForUserResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='licenses', full_name='eve.user.license.api.GetAllForUserResponse.licenses', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=868, serialized_end=939)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.user.license.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.GetRequest.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=941, serialized_end=1000)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.user.license.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.user.license.api.GetResponse.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1002, serialized_end=1062)
_GRANTREQUEST.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
_GRANTREQUEST.fields_by_name['expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GRANTREQUEST.fields_by_name['add_duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_GRANTREQUEST.fields_by_name['payment_method'].enum_type = eve_dot_payment_dot_payment__pb2._METHOD
_GRANTREQUEST.fields_by_name['grant'].message_type = eve_dot_user_dot_license_dot_grant_dot_grant__pb2._IDENTIFIER
_GRANTREQUEST.oneofs_by_name['expiry'].fields.append(_GRANTREQUEST.fields_by_name['expiry_date'])
_GRANTREQUEST.fields_by_name['expiry_date'].containing_oneof = _GRANTREQUEST.oneofs_by_name['expiry']
_GRANTREQUEST.oneofs_by_name['expiry'].fields.append(_GRANTREQUEST.fields_by_name['add_duration'])
_GRANTREQUEST.fields_by_name['add_duration'].containing_oneof = _GRANTREQUEST.oneofs_by_name['expiry']
_SETEXPIRYDATEREQUEST.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
_SETEXPIRYDATEREQUEST.fields_by_name['expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_SETEXPIRYDATEREQUEST.fields_by_name['add_duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_SETEXPIRYDATEREQUEST.oneofs_by_name['expiry'].fields.append(_SETEXPIRYDATEREQUEST.fields_by_name['expiry_date'])
_SETEXPIRYDATEREQUEST.fields_by_name['expiry_date'].containing_oneof = _SETEXPIRYDATEREQUEST.oneofs_by_name['expiry']
_SETEXPIRYDATEREQUEST.oneofs_by_name['expiry'].fields.append(_SETEXPIRYDATEREQUEST.fields_by_name['add_duration'])
_SETEXPIRYDATEREQUEST.fields_by_name['add_duration'].containing_oneof = _SETEXPIRYDATEREQUEST.oneofs_by_name['expiry']
_SETEXPIRYDATERESPONSE.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._ATTRIBUTES
_GETALLFORUSERREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETALLFORUSERRESPONSE.fields_by_name['licenses'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['license'].message_type = eve_dot_user_dot_license_dot_license__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
DESCRIPTOR.message_types_by_name['SetExpiryDateRequest'] = _SETEXPIRYDATEREQUEST
DESCRIPTOR.message_types_by_name['SetExpiryDateResponse'] = _SETEXPIRYDATERESPONSE
DESCRIPTOR.message_types_by_name['GetAllForUserRequest'] = _GETALLFORUSERREQUEST
DESCRIPTOR.message_types_by_name['GetAllForUserResponse'] = _GETALLFORUSERRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GrantResponse)
SetExpiryDateRequest = _reflection.GeneratedProtocolMessageType('SetExpiryDateRequest', (_message.Message,), {'DESCRIPTOR': _SETEXPIRYDATEREQUEST,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(SetExpiryDateRequest)
SetExpiryDateResponse = _reflection.GeneratedProtocolMessageType('SetExpiryDateResponse', (_message.Message,), {'DESCRIPTOR': _SETEXPIRYDATERESPONSE,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(SetExpiryDateResponse)
GetAllForUserRequest = _reflection.GeneratedProtocolMessageType('GetAllForUserRequest', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERREQUEST,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllForUserRequest)
GetAllForUserResponse = _reflection.GeneratedProtocolMessageType('GetAllForUserResponse', (_message.Message,), {'DESCRIPTOR': _GETALLFORUSERRESPONSE,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllForUserResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.user.license.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
