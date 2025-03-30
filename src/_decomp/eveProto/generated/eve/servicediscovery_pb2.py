#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\servicediscovery_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/servicediscovery.proto', package='eve.servicediscovery', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/servicediscovery', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/servicediscovery.proto\x12\x14eve.servicediscovery"\x17\n\x15GetImageServerRequest"%\n\x16GetImageServerResponse\x12\x0b\n\x03url\x18\x01 \x01(\tBAZ?github.com/ccpgames/eve-proto-go/generated/eve/servicediscoveryb\x06proto3')
_GETIMAGESERVERREQUEST = _descriptor.Descriptor(name='GetImageServerRequest', full_name='eve.servicediscovery.GetImageServerRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=52, serialized_end=75)
_GETIMAGESERVERRESPONSE = _descriptor.Descriptor(name='GetImageServerResponse', full_name='eve.servicediscovery.GetImageServerResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='url', full_name='eve.servicediscovery.GetImageServerResponse.url', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=77, serialized_end=114)
DESCRIPTOR.message_types_by_name['GetImageServerRequest'] = _GETIMAGESERVERREQUEST
DESCRIPTOR.message_types_by_name['GetImageServerResponse'] = _GETIMAGESERVERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetImageServerRequest = _reflection.GeneratedProtocolMessageType('GetImageServerRequest', (_message.Message,), {'DESCRIPTOR': _GETIMAGESERVERREQUEST,
 '__module__': 'eve.servicediscovery_pb2'})
_sym_db.RegisterMessage(GetImageServerRequest)
GetImageServerResponse = _reflection.GeneratedProtocolMessageType('GetImageServerResponse', (_message.Message,), {'DESCRIPTOR': _GETIMAGESERVERRESPONSE,
 '__module__': 'eve.servicediscovery_pb2'})
_sym_db.RegisterMessage(GetImageServerResponse)
DESCRIPTOR._options = None
