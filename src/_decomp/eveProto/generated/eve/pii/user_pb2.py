#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pii\user_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pii/user.proto', package='eve.pii.user', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/pii/user', create_key=_descriptor._internal_create_key, serialized_pb='\n\x12eve/pii/user.proto\x12\x0ceve.pii.user\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xbc\x01\n\nAttributes\x12\x11\n\tfull_name\x18\x01 \x01(\t\x12\x15\n\remail_address\x18\x02 \x01(\t\x12\x14\n\x0ccountry_code\x18\x03 \x01(\t\x12\x15\n\rlanguage_code\x18\x04 \x01(\t\x12$\n\x06gender\x18\x05 \x01(\x0e2\x14.eve.pii.user.Gender\x121\n\rdate_of_birth\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp"0\n\nGetRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"4\n\x0bGetResponse\x12%\n\x03pii\x18\x01 \x01(\x0b2\x18.eve.pii.user.Attributes*7\n\x06Gender\x12\x17\n\x13UNKNOWN_UNSPECIFIED\x10\x00\x12\n\n\x06FEMALE\x10\x01\x12\x08\n\x04MALE\x10\x02B9Z7github.com/ccpgames/eve-proto-go/generated/eve/pii/userb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GENDER = _descriptor.EnumDescriptor(name='Gender', full_name='eve.pii.user.Gender', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNKNOWN_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='FEMALE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='MALE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=385, serialized_end=440)
_sym_db.RegisterEnumDescriptor(_GENDER)
Gender = enum_type_wrapper.EnumTypeWrapper(_GENDER)
UNKNOWN_UNSPECIFIED = 0
FEMALE = 1
MALE = 2
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.pii.user.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='full_name', full_name='eve.pii.user.Attributes.full_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='email_address', full_name='eve.pii.user.Attributes.email_address', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='country_code', full_name='eve.pii.user.Attributes.country_code', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='language_code', full_name='eve.pii.user.Attributes.language_code', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='gender', full_name='eve.pii.user.Attributes.gender', index=4, number=5, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='date_of_birth', full_name='eve.pii.user.Attributes.date_of_birth', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=91, serialized_end=279)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.pii.user.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.pii.user.GetRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=281, serialized_end=329)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.pii.user.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='pii', full_name='eve.pii.user.GetResponse.pii', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=331, serialized_end=383)
_ATTRIBUTES.fields_by_name['gender'].enum_type = _GENDER
_ATTRIBUTES.fields_by_name['date_of_birth'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['pii'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.enum_types_by_name['Gender'] = _GENDER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.pii.user_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.pii.user_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.pii.user_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
