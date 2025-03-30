#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\station\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.station import station_pb2 as eve__public_dot_station_dot_station__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/station/api/requests.proto', package='eve_public.station.api', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/station/api', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve_public/station/api/requests.proto\x12\x16eve_public.station.api\x1a eve_public/station/station.proto"=\n\nGetRequest\x12/\n\x07station\x18\x01 \x01(\x0b2\x1e.eve_public.station.Identifier">\n\x0bGetResponse\x12/\n\x07station\x18\x01 \x01(\x0b2\x1e.eve_public.station.AttributesBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/station/apib\x06proto3', dependencies=[eve__public_dot_station_dot_station__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.station.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station', full_name='eve_public.station.api.GetRequest.station', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=99, serialized_end=160)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.station.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station', full_name='eve_public.station.api.GetResponse.station', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=162, serialized_end=224)
_GETREQUEST.fields_by_name['station'].message_type = eve__public_dot_station_dot_station__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['station'].message_type = eve__public_dot_station_dot_station__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.station.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.station.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
