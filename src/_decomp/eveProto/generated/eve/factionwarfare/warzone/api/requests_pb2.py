#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\warzone\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.factionwarfare.warzone import warzone_pb2 as eve_dot_factionwarfare_dot_warzone_dot_warzone__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/warzone/api/requests.proto', package='eve.factionwarfare.warzone.api', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/warzone/api', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve/factionwarfare/warzone/api/requests.proto\x12\x1eeve.factionwarfare.warzone.api\x1a(eve/factionwarfare/warzone/warzone.proto"\x0f\n\rGetAllRequest"J\n\x0eGetAllResponse\x128\n\x08warzones\x18\x01 \x03(\x0b2&.eve.factionwarfare.warzone.Identifier"Q\n\x16GetParticipantsRequest\x127\n\x07warzone\x18\x01 \x01(\x0b2&.eve.factionwarfare.warzone.Identifier"Y\n\x17GetParticipantsResponse\x12>\n\x0cparticipants\x18\x01 \x01(\x0b2(.eve.factionwarfare.warzone.ParticipantsBKZIgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/warzone/apib\x06proto3', dependencies=[eve_dot_factionwarfare_dot_warzone_dot_warzone__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.factionwarfare.warzone.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=123, serialized_end=138)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.factionwarfare.warzone.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='warzones', full_name='eve.factionwarfare.warzone.api.GetAllResponse.warzones', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=140, serialized_end=214)
_GETPARTICIPANTSREQUEST = _descriptor.Descriptor(name='GetParticipantsRequest', full_name='eve.factionwarfare.warzone.api.GetParticipantsRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='warzone', full_name='eve.factionwarfare.warzone.api.GetParticipantsRequest.warzone', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=216, serialized_end=297)
_GETPARTICIPANTSRESPONSE = _descriptor.Descriptor(name='GetParticipantsResponse', full_name='eve.factionwarfare.warzone.api.GetParticipantsResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='participants', full_name='eve.factionwarfare.warzone.api.GetParticipantsResponse.participants', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=299, serialized_end=388)
_GETALLRESPONSE.fields_by_name['warzones'].message_type = eve_dot_factionwarfare_dot_warzone_dot_warzone__pb2._IDENTIFIER
_GETPARTICIPANTSREQUEST.fields_by_name['warzone'].message_type = eve_dot_factionwarfare_dot_warzone_dot_warzone__pb2._IDENTIFIER
_GETPARTICIPANTSRESPONSE.fields_by_name['participants'].message_type = eve_dot_factionwarfare_dot_warzone_dot_warzone__pb2._PARTICIPANTS
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetParticipantsRequest'] = _GETPARTICIPANTSREQUEST
DESCRIPTOR.message_types_by_name['GetParticipantsResponse'] = _GETPARTICIPANTSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.factionwarfare.warzone.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.factionwarfare.warzone.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetParticipantsRequest = _reflection.GeneratedProtocolMessageType('GetParticipantsRequest', (_message.Message,), {'DESCRIPTOR': _GETPARTICIPANTSREQUEST,
 '__module__': 'eve.factionwarfare.warzone.api.requests_pb2'})
_sym_db.RegisterMessage(GetParticipantsRequest)
GetParticipantsResponse = _reflection.GeneratedProtocolMessageType('GetParticipantsResponse', (_message.Message,), {'DESCRIPTOR': _GETPARTICIPANTSRESPONSE,
 '__module__': 'eve.factionwarfare.warzone.api.requests_pb2'})
_sym_db.RegisterMessage(GetParticipantsResponse)
DESCRIPTOR._options = None
