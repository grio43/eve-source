#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\client\connection_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/client/connection.proto', package='', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/client/connection', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/client/connection.proto\x1a\x13eve/user/user.proto"7\n\x11DisconnectRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.IdentifierBBZ@github.com/ccpgames/eve-proto-go/generated/eve/client/connectionb\x06proto3', dependencies=[eve_dot_user_dot_user__pb2.DESCRIPTOR])
_DISCONNECTREQUEST = _descriptor.Descriptor(name='DisconnectRequest', full_name='DisconnectRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='DisconnectRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=52, serialized_end=107)
_DISCONNECTREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['DisconnectRequest'] = _DISCONNECTREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DisconnectRequest = _reflection.GeneratedProtocolMessageType('DisconnectRequest', (_message.Message,), {'DESCRIPTOR': _DISCONNECTREQUEST,
 '__module__': 'eve.client.connection_pb2'})
_sym_db.RegisterMessage(DisconnectRequest)
DESCRIPTOR._options = None
