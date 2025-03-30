#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\entitlement\user\entitlement_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/entitlement/user/entitlement.proto', package='eve_public.entitlement.user.entitlement', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/user', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve_public/entitlement/user/entitlement.proto\x12\'eve_public.entitlement.user.entitlement\x1a\x1fgoogle/protobuf/timestamp.proto"L\n\x0bEntitlement\x12\x0c\n\x04name\x18\x01 \x01(\t\x12/\n\x0bexpiry_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.TimestampBHZFgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/userb\x06proto3', dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_ENTITLEMENT = _descriptor.Descriptor(name='Entitlement', full_name='eve_public.entitlement.user.entitlement.Entitlement', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve_public.entitlement.user.entitlement.Entitlement.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='expiry_date', full_name='eve_public.entitlement.user.entitlement.Entitlement.expiry_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=123, serialized_end=199)
_ENTITLEMENT.fields_by_name['expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Entitlement'] = _ENTITLEMENT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Entitlement = _reflection.GeneratedProtocolMessageType('Entitlement', (_message.Message,), {'DESCRIPTOR': _ENTITLEMENT,
 '__module__': 'eve_public.entitlement.user.entitlement_pb2'})
_sym_db.RegisterMessage(Entitlement)
DESCRIPTOR._options = None
