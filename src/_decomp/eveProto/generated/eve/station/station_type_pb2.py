#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\station\station_type_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.race import race_pb2 as eve_dot_race_dot_race__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/station/station_type.proto', package='eve.stationtype', syntax='proto3', serialized_options='Z:github.com/ccpgames/eve-proto-go/generated/eve/stationtype', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/station/station_type.proto\x12\x0feve.stationtype\x1a\x13eve/race/race.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"0\n\nAttributes\x12"\n\x04race\x18\x01 \x01(\x0b2\x14.eve.race.Identifier"?\n\nGetRequest\x121\n\x0cstation_type\x18\x01 \x01(\x0b2\x1b.eve.stationtype.Identifier">\n\x0bGetResponse\x12/\n\nattributes\x18\x01 \x01(\x0b2\x1b.eve.stationtype.AttributesB<Z:github.com/ccpgames/eve-proto-go/generated/eve/stationtypeb\x06proto3', dependencies=[eve_dot_race_dot_race__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.stationtype.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.stationtype.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=72, serialized_end=104)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.stationtype.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='race', full_name='eve.stationtype.Attributes.race', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=106, serialized_end=154)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.stationtype.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station_type', full_name='eve.stationtype.GetRequest.station_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=156, serialized_end=219)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.stationtype.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.stationtype.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=221, serialized_end=283)
_ATTRIBUTES.fields_by_name['race'].message_type = eve_dot_race_dot_race__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['station_type'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.station.station_type_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.station.station_type_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.station.station_type_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.station.station_type_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
