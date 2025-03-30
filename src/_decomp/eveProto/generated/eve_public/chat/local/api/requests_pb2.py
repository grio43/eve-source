#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\chat\local\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.chat.local import local_pb2 as eve__public_dot_chat_dot_local_dot_local__pb2
from eveProto.generated.eve_public.solarsystem import solarsystem_pb2 as eve__public_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/chat/local/api/requests.proto', package='eve_public.chat.local.api', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve_public/chat/local/api', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve_public/chat/local/api/requests.proto\x12\x19eve_public.chat.local.api\x1a!eve_public/chat/local/local.proto\x1a(eve_public/solarsystem/solarsystem.proto"\x1a\n\x18GetMembershipListRequest"\x88\x01\n\x19GetMembershipListResponse\x121\n\x07members\x18\x01 \x03(\x0b2 .eve_public.chat.local.Character\x128\n\x0csolar_system\x18\x02 \x01(\x0b2".eve_public.solarsystem.Identifier"*\n\x17BroadcastMessageRequest\x12\x0f\n\x07message\x18\x01 \x01(\t"\x1a\n\x18BroadcastMessageResponseBFZDgithub.com/ccpgames/eve-proto-go/generated/eve_public/chat/local/apib\x06proto3', dependencies=[eve__public_dot_chat_dot_local_dot_local__pb2.DESCRIPTOR, eve__public_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_GETMEMBERSHIPLISTREQUEST = _descriptor.Descriptor(name='GetMembershipListRequest', full_name='eve_public.chat.local.api.GetMembershipListRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=148, serialized_end=174)
_GETMEMBERSHIPLISTRESPONSE = _descriptor.Descriptor(name='GetMembershipListResponse', full_name='eve_public.chat.local.api.GetMembershipListResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='members', full_name='eve_public.chat.local.api.GetMembershipListResponse.members', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve_public.chat.local.api.GetMembershipListResponse.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=177, serialized_end=313)
_BROADCASTMESSAGEREQUEST = _descriptor.Descriptor(name='BroadcastMessageRequest', full_name='eve_public.chat.local.api.BroadcastMessageRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='message', full_name='eve_public.chat.local.api.BroadcastMessageRequest.message', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=315, serialized_end=357)
_BROADCASTMESSAGERESPONSE = _descriptor.Descriptor(name='BroadcastMessageResponse', full_name='eve_public.chat.local.api.BroadcastMessageResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=359, serialized_end=385)
_GETMEMBERSHIPLISTRESPONSE.fields_by_name['members'].message_type = eve__public_dot_chat_dot_local_dot_local__pb2._CHARACTER
_GETMEMBERSHIPLISTRESPONSE.fields_by_name['solar_system'].message_type = eve__public_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetMembershipListRequest'] = _GETMEMBERSHIPLISTREQUEST
DESCRIPTOR.message_types_by_name['GetMembershipListResponse'] = _GETMEMBERSHIPLISTRESPONSE
DESCRIPTOR.message_types_by_name['BroadcastMessageRequest'] = _BROADCASTMESSAGEREQUEST
DESCRIPTOR.message_types_by_name['BroadcastMessageResponse'] = _BROADCASTMESSAGERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetMembershipListRequest = _reflection.GeneratedProtocolMessageType('GetMembershipListRequest', (_message.Message,), {'DESCRIPTOR': _GETMEMBERSHIPLISTREQUEST,
 '__module__': 'eve_public.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetMembershipListRequest)
GetMembershipListResponse = _reflection.GeneratedProtocolMessageType('GetMembershipListResponse', (_message.Message,), {'DESCRIPTOR': _GETMEMBERSHIPLISTRESPONSE,
 '__module__': 'eve_public.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(GetMembershipListResponse)
BroadcastMessageRequest = _reflection.GeneratedProtocolMessageType('BroadcastMessageRequest', (_message.Message,), {'DESCRIPTOR': _BROADCASTMESSAGEREQUEST,
 '__module__': 'eve_public.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(BroadcastMessageRequest)
BroadcastMessageResponse = _reflection.GeneratedProtocolMessageType('BroadcastMessageResponse', (_message.Message,), {'DESCRIPTOR': _BROADCASTMESSAGERESPONSE,
 '__module__': 'eve_public.chat.local.api.requests_pb2'})
_sym_db.RegisterMessage(BroadcastMessageResponse)
DESCRIPTOR._options = None
