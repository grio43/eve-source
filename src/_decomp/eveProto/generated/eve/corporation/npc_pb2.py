#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\npc_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/npc.proto', package='eve.corporation.npc', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/corporation/npc', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/corporation/npc.proto\x12\x13eve.corporation.npc\x1a!eve/corporation/corporation.proto"\x0f\n\rGetAllRequest"C\n\x0eGetAllResponse\x121\n\x0ccorporations\x18\x01 \x03(\x0b2\x1b.eve.corporation.Identifier"K\n\x17IsNPCCorporationRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier"*\n\x18IsNPCCorporationResponse\x12\x0e\n\x06is_npc\x18\x01 \x01(\x08B@Z>github.com/ccpgames/eve-proto-go/generated/eve/corporation/npcb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.corporation.npc.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=85, serialized_end=100)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.corporation.npc.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporations', full_name='eve.corporation.npc.GetAllResponse.corporations', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=102, serialized_end=169)
_ISNPCCORPORATIONREQUEST = _descriptor.Descriptor(name='IsNPCCorporationRequest', full_name='eve.corporation.npc.IsNPCCorporationRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.npc.IsNPCCorporationRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=171, serialized_end=246)
_ISNPCCORPORATIONRESPONSE = _descriptor.Descriptor(name='IsNPCCorporationResponse', full_name='eve.corporation.npc.IsNPCCorporationResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='is_npc', full_name='eve.corporation.npc.IsNPCCorporationResponse.is_npc', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=248, serialized_end=290)
_GETALLRESPONSE.fields_by_name['corporations'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ISNPCCORPORATIONREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['IsNPCCorporationRequest'] = _ISNPCCORPORATIONREQUEST
DESCRIPTOR.message_types_by_name['IsNPCCorporationResponse'] = _ISNPCCORPORATIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.corporation.npc_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.corporation.npc_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
IsNPCCorporationRequest = _reflection.GeneratedProtocolMessageType('IsNPCCorporationRequest', (_message.Message,), {'DESCRIPTOR': _ISNPCCORPORATIONREQUEST,
 '__module__': 'eve.corporation.npc_pb2'})
_sym_db.RegisterMessage(IsNPCCorporationRequest)
IsNPCCorporationResponse = _reflection.GeneratedProtocolMessageType('IsNPCCorporationResponse', (_message.Message,), {'DESCRIPTOR': _ISNPCCORPORATIONRESPONSE,
 '__module__': 'eve.corporation.npc_pb2'})
_sym_db.RegisterMessage(IsNPCCorporationResponse)
DESCRIPTOR._options = None
