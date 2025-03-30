#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\securitystatus_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.securitystatus import securitystatus_pb2 as eve_dot_securitystatus_dot_securitystatus__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/securitystatus.proto', package='eve.character.securitystatus', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/character/securitystatus', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/character/securitystatus.proto\x12\x1ceve.character.securitystatus\x1a\x1deve/character/character.proto\x1a\'eve/securitystatus/securitystatus.proto":\n\nGetRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"M\n\x0bGetResponse\x128\n\x15security_status_value\x18\x02 \x01(\x0b2\x19.eve.securitystatus.ValueJ\x04\x08\x01\x10\x02BIZGgithub.com/ccpgames/eve-proto-go/generated/eve/character/securitystatusb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_securitystatus_dot_securitystatus__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.character.securitystatus.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.securitystatus.GetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=140, serialized_end=198)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.character.securitystatus.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='security_status_value', full_name='eve.character.securitystatus.GetResponse.security_status_value', index=0, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=200, serialized_end=277)
_GETREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['security_status_value'].message_type = eve_dot_securitystatus_dot_securitystatus__pb2._VALUE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.character.securitystatus_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.character.securitystatus_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
