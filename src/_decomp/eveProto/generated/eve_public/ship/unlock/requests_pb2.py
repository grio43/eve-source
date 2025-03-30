#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\ship\unlock\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.ship import ship_type_pb2 as eve__public_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/ship/unlock/requests.proto', package='eve_public.ship.unlock', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/ship/unlock', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve_public/ship/unlock/requests.proto\x12\x16eve_public.ship.unlock\x1a\x1feve_public/ship/ship_type.proto" \n\x1eGetPendingNotificationsRequest"_\n\x1fGetPendingNotificationsResponse\x12<\n\x13unlocked_ship_types\x18\x01 \x03(\x0b2\x1f.eve_public.shiptype.Identifier"Q\n\x12ClaimRewardRequest\x12;\n\x12unlocked_ship_type\x18\x01 \x01(\x0b2\x1f.eve_public.shiptype.Identifier"\x15\n\x13ClaimRewardResponseBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/ship/unlockb\x06proto3', dependencies=[eve__public_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_GETPENDINGNOTIFICATIONSREQUEST = _descriptor.Descriptor(name='GetPendingNotificationsRequest', full_name='eve_public.ship.unlock.GetPendingNotificationsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=98, serialized_end=130)
_GETPENDINGNOTIFICATIONSRESPONSE = _descriptor.Descriptor(name='GetPendingNotificationsResponse', full_name='eve_public.ship.unlock.GetPendingNotificationsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unlocked_ship_types', full_name='eve_public.ship.unlock.GetPendingNotificationsResponse.unlocked_ship_types', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=227)
_CLAIMREWARDREQUEST = _descriptor.Descriptor(name='ClaimRewardRequest', full_name='eve_public.ship.unlock.ClaimRewardRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unlocked_ship_type', full_name='eve_public.ship.unlock.ClaimRewardRequest.unlocked_ship_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=229, serialized_end=310)
_CLAIMREWARDRESPONSE = _descriptor.Descriptor(name='ClaimRewardResponse', full_name='eve_public.ship.unlock.ClaimRewardResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=312, serialized_end=333)
_GETPENDINGNOTIFICATIONSRESPONSE.fields_by_name['unlocked_ship_types'].message_type = eve__public_dot_ship_dot_ship__type__pb2._IDENTIFIER
_CLAIMREWARDREQUEST.fields_by_name['unlocked_ship_type'].message_type = eve__public_dot_ship_dot_ship__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetPendingNotificationsRequest'] = _GETPENDINGNOTIFICATIONSREQUEST
DESCRIPTOR.message_types_by_name['GetPendingNotificationsResponse'] = _GETPENDINGNOTIFICATIONSRESPONSE
DESCRIPTOR.message_types_by_name['ClaimRewardRequest'] = _CLAIMREWARDREQUEST
DESCRIPTOR.message_types_by_name['ClaimRewardResponse'] = _CLAIMREWARDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetPendingNotificationsRequest = _reflection.GeneratedProtocolMessageType('GetPendingNotificationsRequest', (_message.Message,), {'DESCRIPTOR': _GETPENDINGNOTIFICATIONSREQUEST,
 '__module__': 'eve_public.ship.unlock.requests_pb2'})
_sym_db.RegisterMessage(GetPendingNotificationsRequest)
GetPendingNotificationsResponse = _reflection.GeneratedProtocolMessageType('GetPendingNotificationsResponse', (_message.Message,), {'DESCRIPTOR': _GETPENDINGNOTIFICATIONSRESPONSE,
 '__module__': 'eve_public.ship.unlock.requests_pb2'})
_sym_db.RegisterMessage(GetPendingNotificationsResponse)
ClaimRewardRequest = _reflection.GeneratedProtocolMessageType('ClaimRewardRequest', (_message.Message,), {'DESCRIPTOR': _CLAIMREWARDREQUEST,
 '__module__': 'eve_public.ship.unlock.requests_pb2'})
_sym_db.RegisterMessage(ClaimRewardRequest)
ClaimRewardResponse = _reflection.GeneratedProtocolMessageType('ClaimRewardResponse', (_message.Message,), {'DESCRIPTOR': _CLAIMREWARDRESPONSE,
 '__module__': 'eve_public.ship.unlock.requests_pb2'})
_sym_db.RegisterMessage(ClaimRewardResponse)
DESCRIPTOR._options = None
