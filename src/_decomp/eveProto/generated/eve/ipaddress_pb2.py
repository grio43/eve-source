#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ipaddress_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ipaddress.proto', package='eve', syntax='proto3', serialized_options='Z.github.com/ccpgames/eve-proto-go/generated/eve', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/ipaddress.proto\x12\x03eve"2\n\tIPAddress\x12\x0c\n\x02v4\x18\x01 \x01(\x07H\x00\x12\x0c\n\x02v6\x18\x02 \x01(\x0cH\x00B\t\n\x07versionB0Z.github.com/ccpgames/eve-proto-go/generated/eveb\x06proto3')
_IPADDRESS = _descriptor.Descriptor(name='IPAddress', full_name='eve.IPAddress', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='v4', full_name='eve.IPAddress.v4', index=0, number=1, type=7, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='v6', full_name='eve.IPAddress.v6', index=1, number=2, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='version', full_name='eve.IPAddress.version', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=28, serialized_end=78)
_IPADDRESS.oneofs_by_name['version'].fields.append(_IPADDRESS.fields_by_name['v4'])
_IPADDRESS.fields_by_name['v4'].containing_oneof = _IPADDRESS.oneofs_by_name['version']
_IPADDRESS.oneofs_by_name['version'].fields.append(_IPADDRESS.fields_by_name['v6'])
_IPADDRESS.fields_by_name['v6'].containing_oneof = _IPADDRESS.oneofs_by_name['version']
DESCRIPTOR.message_types_by_name['IPAddress'] = _IPADDRESS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
IPAddress = _reflection.GeneratedProtocolMessageType('IPAddress', (_message.Message,), {'DESCRIPTOR': _IPADDRESS,
 '__module__': 'eve.ipaddress_pb2'})
_sym_db.RegisterMessage(IPAddress)
DESCRIPTOR._options = None
