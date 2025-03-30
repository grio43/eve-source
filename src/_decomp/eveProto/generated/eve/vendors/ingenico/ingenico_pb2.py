#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vendors\ingenico\ingenico_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vendors/ingenico/ingenico.proto', package='eve.vendors.ingenico', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/vendors/ingenico', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/vendors/ingenico/ingenico.proto\x12\x14eve.vendors.ingenico\x1a\x1fgoogle/protobuf/timestamp.proto"6\n\x06Update\x12,\n\x08received\x18\x01 \x01(\x0b2\x1a.google.protobuf.TimestampBAZ?github.com/ccpgames/eve-proto-go/generated/eve/vendors/ingenicob\x06proto3', dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_UPDATE = _descriptor.Descriptor(name='Update', full_name='eve.vendors.ingenico.Update', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='received', full_name='eve.vendors.ingenico.Update.received', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=94, serialized_end=148)
_UPDATE.fields_by_name['received'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Update'] = _UPDATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Update = _reflection.GeneratedProtocolMessageType('Update', (_message.Message,), {'DESCRIPTOR': _UPDATE,
 '__module__': 'eve.vendors.ingenico.ingenico_pb2'})
_sym_db.RegisterMessage(Update)
DESCRIPTOR._options = None
