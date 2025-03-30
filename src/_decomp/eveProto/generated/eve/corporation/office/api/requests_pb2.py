#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\office\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/office/api/requests.proto', package='eve.corporation.office.api', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/office/api', create_key=_descriptor._internal_create_key, serialized_pb='\n)eve/corporation/office/api/requests.proto\x12\x1aeve.corporation.office.api\x1a!eve/corporation/corporation.proto\x1a!eve/solarsystem/solarsystem.proto"J\n\x16GetSolarSystemsRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier"M\n\x17GetSolarSystemsResponse\x122\n\rsolar_systems\x18\x01 \x03(\x0b2\x1b.eve.solarsystem.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/office/apib\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_GETSOLARSYSTEMSREQUEST = _descriptor.Descriptor(name='GetSolarSystemsRequest', full_name='eve.corporation.office.api.GetSolarSystemsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.office.api.GetSolarSystemsRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=143, serialized_end=217)
_GETSOLARSYSTEMSRESPONSE = _descriptor.Descriptor(name='GetSolarSystemsResponse', full_name='eve.corporation.office.api.GetSolarSystemsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_systems', full_name='eve.corporation.office.api.GetSolarSystemsResponse.solar_systems', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=219, serialized_end=296)
_GETSOLARSYSTEMSREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETSOLARSYSTEMSRESPONSE.fields_by_name['solar_systems'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetSolarSystemsRequest'] = _GETSOLARSYSTEMSREQUEST
DESCRIPTOR.message_types_by_name['GetSolarSystemsResponse'] = _GETSOLARSYSTEMSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetSolarSystemsRequest = _reflection.GeneratedProtocolMessageType('GetSolarSystemsRequest', (_message.Message,), {'DESCRIPTOR': _GETSOLARSYSTEMSREQUEST,
 '__module__': 'eve.corporation.office.api.requests_pb2'})
_sym_db.RegisterMessage(GetSolarSystemsRequest)
GetSolarSystemsResponse = _reflection.GeneratedProtocolMessageType('GetSolarSystemsResponse', (_message.Message,), {'DESCRIPTOR': _GETSOLARSYSTEMSRESPONSE,
 '__module__': 'eve.corporation.office.api.requests_pb2'})
_sym_db.RegisterMessage(GetSolarSystemsResponse)
DESCRIPTOR._options = None
