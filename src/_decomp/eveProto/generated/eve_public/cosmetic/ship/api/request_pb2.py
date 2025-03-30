#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\ship\api\request_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.cosmetic.ship import ship_pb2 as eve__public_dot_cosmetic_dot_ship_dot_ship__pb2
from eveProto.generated.eve_public.ship import ship_pb2 as eve__public_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/ship/api/request.proto', package='eve_public.cosmetic.ship.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve_public/cosmetic/ship/api/request.proto\x12\x1ceve_public.cosmetic.ship.api\x1a#eve_public/cosmetic/ship/ship.proto\x1a\x1aeve_public/ship/ship.proto"\x17\n\x15GetAllInBubbleRequest"I\n\x16GetAllInBubbleResponse\x12/\n\x06states\x18\x01 \x03(\x0b2\x1f.eve_public.cosmetic.ship.State"7\n\nGetRequest\x12)\n\x04ship\x18\x01 \x01(\x0b2\x1b.eve_public.ship.Identifier"=\n\x0bGetResponse\x12.\n\x05state\x18\x01 \x01(\x0b2\x1f.eve_public.cosmetic.ship.StateBIZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/apib\x06proto3', dependencies=[eve__public_dot_cosmetic_dot_ship_dot_ship__pb2.DESCRIPTOR, eve__public_dot_ship_dot_ship__pb2.DESCRIPTOR])
_GETALLINBUBBLEREQUEST = _descriptor.Descriptor(name='GetAllInBubbleRequest', full_name='eve_public.cosmetic.ship.api.GetAllInBubbleRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=141, serialized_end=164)
_GETALLINBUBBLERESPONSE = _descriptor.Descriptor(name='GetAllInBubbleResponse', full_name='eve_public.cosmetic.ship.api.GetAllInBubbleResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='states', full_name='eve_public.cosmetic.ship.api.GetAllInBubbleResponse.states', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=166, serialized_end=239)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.cosmetic.ship.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship', full_name='eve_public.cosmetic.ship.api.GetRequest.ship', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=241, serialized_end=296)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.cosmetic.ship.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='state', full_name='eve_public.cosmetic.ship.api.GetResponse.state', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=298, serialized_end=359)
_GETALLINBUBBLERESPONSE.fields_by_name['states'].message_type = eve__public_dot_cosmetic_dot_ship_dot_ship__pb2._STATE
_GETREQUEST.fields_by_name['ship'].message_type = eve__public_dot_ship_dot_ship__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['state'].message_type = eve__public_dot_cosmetic_dot_ship_dot_ship__pb2._STATE
DESCRIPTOR.message_types_by_name['GetAllInBubbleRequest'] = _GETALLINBUBBLEREQUEST
DESCRIPTOR.message_types_by_name['GetAllInBubbleResponse'] = _GETALLINBUBBLERESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllInBubbleRequest = _reflection.GeneratedProtocolMessageType('GetAllInBubbleRequest', (_message.Message,), {'DESCRIPTOR': _GETALLINBUBBLEREQUEST,
 '__module__': 'eve_public.cosmetic.ship.api.request_pb2'})
_sym_db.RegisterMessage(GetAllInBubbleRequest)
GetAllInBubbleResponse = _reflection.GeneratedProtocolMessageType('GetAllInBubbleResponse', (_message.Message,), {'DESCRIPTOR': _GETALLINBUBBLERESPONSE,
 '__module__': 'eve_public.cosmetic.ship.api.request_pb2'})
_sym_db.RegisterMessage(GetAllInBubbleResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.cosmetic.ship.api.request_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.cosmetic.ship.api.request_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
