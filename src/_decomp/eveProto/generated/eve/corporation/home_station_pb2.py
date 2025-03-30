#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\home_station_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/home_station.proto', package='eve.corporation.homestation', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/homestation', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/corporation/home_station.proto\x12\x1beve.corporation.homestation\x1a!eve/corporation/corporation.proto\x1a\x19eve/station/station.proto">\n\nGetRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier"7\n\x0bGetResponse\x12(\n\x07station\x18\x01 \x01(\x0b2\x17.eve.station.IdentifierBHZFgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/homestationb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_station_dot_station__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.corporation.homestation.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.homestation.GetRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=129, serialized_end=191)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.corporation.homestation.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station', full_name='eve.corporation.homestation.GetResponse.station', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=193, serialized_end=248)
_GETREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.corporation.home_station_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.corporation.home_station_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
