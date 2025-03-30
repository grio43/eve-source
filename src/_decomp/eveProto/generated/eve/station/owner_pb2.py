#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\station\owner_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/station/owner.proto', package='eve.station.owner', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/station/owner', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/station/owner.proto\x12\x11eve.station.owner\x1a!eve/corporation/corporation.proto\x1a\x19eve/station/station.proto"B\n\x16GetStationOwnerRequest\x12(\n\x07station\x18\x01 \x01(\x0b2\x17.eve.station.Identifier"K\n\x17GetStationOwnerResponse\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.IdentifierB>Z<github.com/ccpgames/eve-proto-go/generated/eve/station/ownerb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_station_dot_station__pb2.DESCRIPTOR])
_GETSTATIONOWNERREQUEST = _descriptor.Descriptor(name='GetStationOwnerRequest', full_name='eve.station.owner.GetStationOwnerRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station', full_name='eve.station.owner.GetStationOwnerRequest.station', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=108, serialized_end=174)
_GETSTATIONOWNERRESPONSE = _descriptor.Descriptor(name='GetStationOwnerResponse', full_name='eve.station.owner.GetStationOwnerResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.station.owner.GetStationOwnerResponse.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=176, serialized_end=251)
_GETSTATIONOWNERREQUEST.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_GETSTATIONOWNERRESPONSE.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetStationOwnerRequest'] = _GETSTATIONOWNERREQUEST
DESCRIPTOR.message_types_by_name['GetStationOwnerResponse'] = _GETSTATIONOWNERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetStationOwnerRequest = _reflection.GeneratedProtocolMessageType('GetStationOwnerRequest', (_message.Message,), {'DESCRIPTOR': _GETSTATIONOWNERREQUEST,
 '__module__': 'eve.station.owner_pb2'})
_sym_db.RegisterMessage(GetStationOwnerRequest)
GetStationOwnerResponse = _reflection.GeneratedProtocolMessageType('GetStationOwnerResponse', (_message.Message,), {'DESCRIPTOR': _GETSTATIONOWNERRESPONSE,
 '__module__': 'eve.station.owner_pb2'})
_sym_db.RegisterMessage(GetStationOwnerResponse)
DESCRIPTOR._options = None
