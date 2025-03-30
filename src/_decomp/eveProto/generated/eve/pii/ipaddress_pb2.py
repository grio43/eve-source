#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pii\ipaddress_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve import ipaddress_pb2 as eve_dot_ipaddress__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pii/ipaddress.proto', package='eve.pii.ipaddress', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/pii/ipaddress', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/pii/ipaddress.proto\x12\x11eve.pii.ipaddress\x1a\x13eve/ipaddress.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"?\n\nGetRequest\x121\n\nidentifier\x18\x01 \x01(\x0b2\x1d.eve.pii.ipaddress.Identifier".\n\x0bGetResponse\x12\x1f\n\x07address\x18\x01 \x01(\x0b2\x0e.eve.IPAddressB>Z<github.com/ccpgames/eve-proto-go/generated/eve/pii/ipaddressb\x06proto3', dependencies=[eve_dot_ipaddress__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.pii.ipaddress.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.pii.ipaddress.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=67, serialized_end=99)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.pii.ipaddress.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.pii.ipaddress.GetRequest.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=101, serialized_end=164)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.pii.ipaddress.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='address', full_name='eve.pii.ipaddress.GetResponse.address', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=166, serialized_end=212)
_GETREQUEST.fields_by_name['identifier'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['address'].message_type = eve_dot_ipaddress__pb2._IPADDRESS
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.pii.ipaddress_pb2'})
_sym_db.RegisterMessage(Identifier)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.pii.ipaddress_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.pii.ipaddress_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
