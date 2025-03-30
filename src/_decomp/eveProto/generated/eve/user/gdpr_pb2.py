#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\gdpr_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/gdpr.proto', package='eve.user.gdpr', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/user/gdpr', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/user/gdpr.proto\x12\reve.user.gdpr\x1a\x13eve/user/user.proto"l\n\x14PurgeUserDataRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12,\n\x0erequester_user\x18\x02 \x01(\x0b2\x14.eve.user.Identifier:\x02\x18\x01"\x1b\n\x15PurgeUserDataResponse:\x02\x18\x01B:Z8github.com/ccpgames/eve-proto-go/generated/eve/user/gdprb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_PURGEUSERDATAREQUEST = _descriptor.Descriptor(name='PurgeUserDataRequest', full_name='eve.user.gdpr.PurgeUserDataRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.gdpr.PurgeUserDataRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='requester_user', full_name='eve.user.gdpr.PurgeUserDataRequest.requester_user', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=59, serialized_end=167)
_PURGEUSERDATARESPONSE = _descriptor.Descriptor(name='PurgeUserDataResponse', full_name='eve.user.gdpr.PurgeUserDataResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=169, serialized_end=196)
_PURGEUSERDATAREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_PURGEUSERDATAREQUEST.fields_by_name['requester_user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['PurgeUserDataRequest'] = _PURGEUSERDATAREQUEST
DESCRIPTOR.message_types_by_name['PurgeUserDataResponse'] = _PURGEUSERDATARESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
PurgeUserDataRequest = _reflection.GeneratedProtocolMessageType('PurgeUserDataRequest', (_message.Message,), {'DESCRIPTOR': _PURGEUSERDATAREQUEST,
 '__module__': 'eve.user.gdpr_pb2'})
_sym_db.RegisterMessage(PurgeUserDataRequest)
PurgeUserDataResponse = _reflection.GeneratedProtocolMessageType('PurgeUserDataResponse', (_message.Message,), {'DESCRIPTOR': _PURGEUSERDATARESPONSE,
 '__module__': 'eve.user.gdpr_pb2'})
_sym_db.RegisterMessage(PurgeUserDataResponse)
DESCRIPTOR._options = None
_PURGEUSERDATAREQUEST._options = None
_PURGEUSERDATARESPONSE._options = None
