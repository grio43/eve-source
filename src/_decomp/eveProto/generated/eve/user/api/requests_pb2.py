#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve import ipaddress_pb2 as eve_dot_ipaddress__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/api/requests.proto', package='eve.user.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/user/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/user/api/requests.proto\x12\x0ceve.user.api\x1a\x13eve/ipaddress.proto\x1a\x13eve/user/user.proto"?\n\x19DeletePersonalDataRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"\x1c\n\x1aDeletePersonalDataResponse"u\n\rCreateRequest\x12\x15\n\remail_address\x18\x01 \x01(\t\x12\x14\n\x0ccountry_code\x18\x02 \x01(\t\x12"\n\nip_address\x18\x03 \x01(\x0b2\x0e.eve.IPAddress\x12\x13\n\x0bagreed_eula\x18\x04 \x01(\x08"4\n\x0eCreateResponse\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"%\n\x14GetAllByEmailRequest\x12\r\n\x05email\x18\x01 \x01(\t"<\n\x15GetAllByEmailResponse\x12#\n\x05users\x18\x01 \x03(\x0b2\x14.eve.user.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/user/apib\x06proto3', dependencies=[eve_dot_ipaddress__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR])
_DELETEPERSONALDATAREQUEST = _descriptor.Descriptor(name='DeletePersonalDataRequest', full_name='eve.user.api.DeletePersonalDataRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.api.DeletePersonalDataRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=87, serialized_end=150)
_DELETEPERSONALDATARESPONSE = _descriptor.Descriptor(name='DeletePersonalDataResponse', full_name='eve.user.api.DeletePersonalDataResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=152, serialized_end=180)
_CREATEREQUEST = _descriptor.Descriptor(name='CreateRequest', full_name='eve.user.api.CreateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='email_address', full_name='eve.user.api.CreateRequest.email_address', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='country_code', full_name='eve.user.api.CreateRequest.country_code', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ip_address', full_name='eve.user.api.CreateRequest.ip_address', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='agreed_eula', full_name='eve.user.api.CreateRequest.agreed_eula', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=182, serialized_end=299)
_CREATERESPONSE = _descriptor.Descriptor(name='CreateResponse', full_name='eve.user.api.CreateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.api.CreateResponse.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=301, serialized_end=353)
_GETALLBYEMAILREQUEST = _descriptor.Descriptor(name='GetAllByEmailRequest', full_name='eve.user.api.GetAllByEmailRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='email', full_name='eve.user.api.GetAllByEmailRequest.email', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=355, serialized_end=392)
_GETALLBYEMAILRESPONSE = _descriptor.Descriptor(name='GetAllByEmailResponse', full_name='eve.user.api.GetAllByEmailResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='users', full_name='eve.user.api.GetAllByEmailResponse.users', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=394, serialized_end=454)
_DELETEPERSONALDATAREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_CREATEREQUEST.fields_by_name['ip_address'].message_type = eve_dot_ipaddress__pb2._IPADDRESS
_CREATERESPONSE.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETALLBYEMAILRESPONSE.fields_by_name['users'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['DeletePersonalDataRequest'] = _DELETEPERSONALDATAREQUEST
DESCRIPTOR.message_types_by_name['DeletePersonalDataResponse'] = _DELETEPERSONALDATARESPONSE
DESCRIPTOR.message_types_by_name['CreateRequest'] = _CREATEREQUEST
DESCRIPTOR.message_types_by_name['CreateResponse'] = _CREATERESPONSE
DESCRIPTOR.message_types_by_name['GetAllByEmailRequest'] = _GETALLBYEMAILREQUEST
DESCRIPTOR.message_types_by_name['GetAllByEmailResponse'] = _GETALLBYEMAILRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DeletePersonalDataRequest = _reflection.GeneratedProtocolMessageType('DeletePersonalDataRequest', (_message.Message,), {'DESCRIPTOR': _DELETEPERSONALDATAREQUEST,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(DeletePersonalDataRequest)
DeletePersonalDataResponse = _reflection.GeneratedProtocolMessageType('DeletePersonalDataResponse', (_message.Message,), {'DESCRIPTOR': _DELETEPERSONALDATARESPONSE,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(DeletePersonalDataResponse)
CreateRequest = _reflection.GeneratedProtocolMessageType('CreateRequest', (_message.Message,), {'DESCRIPTOR': _CREATEREQUEST,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(CreateRequest)
CreateResponse = _reflection.GeneratedProtocolMessageType('CreateResponse', (_message.Message,), {'DESCRIPTOR': _CREATERESPONSE,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(CreateResponse)
GetAllByEmailRequest = _reflection.GeneratedProtocolMessageType('GetAllByEmailRequest', (_message.Message,), {'DESCRIPTOR': _GETALLBYEMAILREQUEST,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllByEmailRequest)
GetAllByEmailResponse = _reflection.GeneratedProtocolMessageType('GetAllByEmailResponse', (_message.Message,), {'DESCRIPTOR': _GETALLBYEMAILRESPONSE,
 '__module__': 'eve.user.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllByEmailResponse)
DESCRIPTOR._options = None
