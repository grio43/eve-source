#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\botting_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/botting.proto', package='eve.user.botting', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/user/botting', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/user/botting.proto\x12\x10eve.user.botting\x1a\x13eve/user/user.proto"=\n\x13GetReportersRequest\x12&\n\x08reported\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"?\n\x14GetReportersResponse\x12\'\n\treporters\x18\x01 \x03(\x0b2\x14.eve.user.IdentifierB=Z;github.com/ccpgames/eve-proto-go/generated/eve/user/bottingb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETREPORTERSREQUEST = _descriptor.Descriptor(name='GetReportersRequest', full_name='eve.user.botting.GetReportersRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='reported', full_name='eve.user.botting.GetReportersRequest.reported', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=65, serialized_end=126)
_GETREPORTERSRESPONSE = _descriptor.Descriptor(name='GetReportersResponse', full_name='eve.user.botting.GetReportersResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='reporters', full_name='eve.user.botting.GetReportersResponse.reporters', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=128, serialized_end=191)
_GETREPORTERSREQUEST.fields_by_name['reported'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETREPORTERSRESPONSE.fields_by_name['reporters'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetReportersRequest'] = _GETREPORTERSREQUEST
DESCRIPTOR.message_types_by_name['GetReportersResponse'] = _GETREPORTERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetReportersRequest = _reflection.GeneratedProtocolMessageType('GetReportersRequest', (_message.Message,), {'DESCRIPTOR': _GETREPORTERSREQUEST,
 '__module__': 'eve.user.botting_pb2'})
_sym_db.RegisterMessage(GetReportersRequest)
GetReportersResponse = _reflection.GeneratedProtocolMessageType('GetReportersResponse', (_message.Message,), {'DESCRIPTOR': _GETREPORTERSRESPONSE,
 '__module__': 'eve.user.botting_pb2'})
_sym_db.RegisterMessage(GetReportersResponse)
DESCRIPTOR._options = None
