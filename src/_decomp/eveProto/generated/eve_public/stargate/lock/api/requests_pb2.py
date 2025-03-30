#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\stargate\lock\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.solarsystem import solarsystem_pb2 as eve__public_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve_public.stargate import stargate_pb2 as eve__public_dot_stargate_dot_stargate__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/stargate/lock/api/requests.proto', package='eve_public.stargate.lock.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/stargate/lock/api', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve_public/stargate/lock/api/requests.proto\x12\x1ceve_public.stargate.lock.api\x1a(eve_public/solarsystem/solarsystem.proto\x1a"eve_public/stargate/stargate.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x0c\n\nGetRequest"h\n\x0bGetResponse\x12-\n\x04gate\x18\x01 \x01(\x0b2\x1f.eve_public.stargate.Identifier\x12*\n\x06expiry\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp"\x1d\n\x1bGetRestrictedSystemsRequest"X\n\x1cGetRestrictedSystemsResponse\x128\n\x0csolarsystems\x18\x01 \x03(\x0b2".eve_public.solarsystem.IdentifierBIZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/stargate/lock/apib\x06proto3', dependencies=[eve__public_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR, eve__public_dot_stargate_dot_stargate__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.stargate.lock.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=188, serialized_end=200)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.stargate.lock.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='gate', full_name='eve_public.stargate.lock.api.GetResponse.gate', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='expiry', full_name='eve_public.stargate.lock.api.GetResponse.expiry', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=202, serialized_end=306)
_GETRESTRICTEDSYSTEMSREQUEST = _descriptor.Descriptor(name='GetRestrictedSystemsRequest', full_name='eve_public.stargate.lock.api.GetRestrictedSystemsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=308, serialized_end=337)
_GETRESTRICTEDSYSTEMSRESPONSE = _descriptor.Descriptor(name='GetRestrictedSystemsResponse', full_name='eve_public.stargate.lock.api.GetRestrictedSystemsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystems', full_name='eve_public.stargate.lock.api.GetRestrictedSystemsResponse.solarsystems', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=339, serialized_end=427)
_GETRESPONSE.fields_by_name['gate'].message_type = eve__public_dot_stargate_dot_stargate__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['expiry'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETRESTRICTEDSYSTEMSRESPONSE.fields_by_name['solarsystems'].message_type = eve__public_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetRestrictedSystemsRequest'] = _GETRESTRICTEDSYSTEMSREQUEST
DESCRIPTOR.message_types_by_name['GetRestrictedSystemsResponse'] = _GETRESTRICTEDSYSTEMSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.stargate.lock.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.stargate.lock.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetRestrictedSystemsRequest = _reflection.GeneratedProtocolMessageType('GetRestrictedSystemsRequest', (_message.Message,), {'DESCRIPTOR': _GETRESTRICTEDSYSTEMSREQUEST,
 '__module__': 'eve_public.stargate.lock.api.requests_pb2'})
_sym_db.RegisterMessage(GetRestrictedSystemsRequest)
GetRestrictedSystemsResponse = _reflection.GeneratedProtocolMessageType('GetRestrictedSystemsResponse', (_message.Message,), {'DESCRIPTOR': _GETRESTRICTEDSYSTEMSRESPONSE,
 '__module__': 'eve_public.stargate.lock.api.requests_pb2'})
_sym_db.RegisterMessage(GetRestrictedSystemsResponse)
DESCRIPTOR._options = None
