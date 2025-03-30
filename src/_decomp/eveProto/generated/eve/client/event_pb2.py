#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\client\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.client import host_pb2 as eve_dot_client_dot_host__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/client/event.proto', package='eve.client.event', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/client/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/client/event.proto\x12\x10eve.client.event\x1a\x15eve/client/host.proto\x1a\x13eve/user/user.proto"\xa4\x01\n\tConnected\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12\x12\n\nsession_id\x18\x02 \x01(\t\x12)\n\x04host\x18\x03 \x01(\x0b2\x1b.eve.client.host.Identifier\x124\n\x0fhost_attributes\x18\x04 \x01(\x0b2\x1b.eve.client.host.AttributesB=Z;github.com/ccpgames/eve-proto-go/generated/eve/client/eventb\x06proto3', dependencies=[eve_dot_client_dot_host__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR])
_CONNECTED = _descriptor.Descriptor(name='Connected', full_name='eve.client.event.Connected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.client.event.Connected.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='session_id', full_name='eve.client.event.Connected.session_id', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='host', full_name='eve.client.event.Connected.host', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='host_attributes', full_name='eve.client.event.Connected.host_attributes', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=89, serialized_end=253)
_CONNECTED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_CONNECTED.fields_by_name['host'].message_type = eve_dot_client_dot_host__pb2._IDENTIFIER
_CONNECTED.fields_by_name['host_attributes'].message_type = eve_dot_client_dot_host__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Connected'] = _CONNECTED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Connected = _reflection.GeneratedProtocolMessageType('Connected', (_message.Message,), {'DESCRIPTOR': _CONNECTED,
 '__module__': 'eve.client.event_pb2'})
_sym_db.RegisterMessage(Connected)
DESCRIPTOR._options = None
