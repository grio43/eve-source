#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\freelance\project\corporation\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/freelance/project/corporation/api/requests.proto', package='eve.freelance.project.corporation.api', syntax='proto3', serialized_options='ZPgithub.com/ccpgames/eve-proto-go/generated/eve/freelance/project/corporation/api', create_key=_descriptor._internal_create_key, serialized_pb='\n4eve/freelance/project/corporation/api/requests.proto\x12%eve.freelance.project.corporation.api\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto"r\n\x10CanManageRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x120\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.Identifier"\'\n\x11CanManageResponse\x12\x12\n\ncan_manage\x18\x01 \x01(\x08BRZPgithub.com/ccpgames/eve-proto-go/generated/eve/freelance/project/corporation/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_CANMANAGEREQUEST = _descriptor.Descriptor(name='CanManageRequest', full_name='eve.freelance.project.corporation.api.CanManageRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.freelance.project.corporation.api.CanManageRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.freelance.project.corporation.api.CanManageRequest.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=161, serialized_end=275)
_CANMANAGERESPONSE = _descriptor.Descriptor(name='CanManageResponse', full_name='eve.freelance.project.corporation.api.CanManageResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='can_manage', full_name='eve.freelance.project.corporation.api.CanManageResponse.can_manage', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=277, serialized_end=316)
_CANMANAGEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CANMANAGEREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['CanManageRequest'] = _CANMANAGEREQUEST
DESCRIPTOR.message_types_by_name['CanManageResponse'] = _CANMANAGERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
CanManageRequest = _reflection.GeneratedProtocolMessageType('CanManageRequest', (_message.Message,), {'DESCRIPTOR': _CANMANAGEREQUEST,
 '__module__': 'eve.freelance.project.corporation.api.requests_pb2'})
_sym_db.RegisterMessage(CanManageRequest)
CanManageResponse = _reflection.GeneratedProtocolMessageType('CanManageResponse', (_message.Message,), {'DESCRIPTOR': _CANMANAGERESPONSE,
 '__module__': 'eve.freelance.project.corporation.api.requests_pb2'})
_sym_db.RegisterMessage(CanManageResponse)
DESCRIPTOR._options = None
