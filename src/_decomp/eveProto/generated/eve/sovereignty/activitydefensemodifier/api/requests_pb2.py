#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\activitydefensemodifier\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/activitydefensemodifier/api/requests.proto', package='eve.sovereignty.activitydefensemodifier.api', syntax='proto3', serialized_options='ZVgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/activitydefensemodifier/api', create_key=_descriptor._internal_create_key, serialized_pb='\n:eve/sovereignty/activitydefensemodifier/api/requests.proto\x12+eve.sovereignty.activitydefensemodifier.api\x1a!eve/solarsystem/solarsystem.proto"C\n\x0fGetLevelRequest\x120\n\x0bsolarsystem\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier"!\n\x10GetLevelResponse\x12\r\n\x05level\x18\x01 \x01(\x04BXZVgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/activitydefensemodifier/apib\x06proto3', dependencies=[eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_GETLEVELREQUEST = _descriptor.Descriptor(name='GetLevelRequest', full_name='eve.sovereignty.activitydefensemodifier.api.GetLevelRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystem', full_name='eve.sovereignty.activitydefensemodifier.api.GetLevelRequest.solarsystem', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=142, serialized_end=209)
_GETLEVELRESPONSE = _descriptor.Descriptor(name='GetLevelResponse', full_name='eve.sovereignty.activitydefensemodifier.api.GetLevelResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='level', full_name='eve.sovereignty.activitydefensemodifier.api.GetLevelResponse.level', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=211, serialized_end=244)
_GETLEVELREQUEST.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetLevelRequest'] = _GETLEVELREQUEST
DESCRIPTOR.message_types_by_name['GetLevelResponse'] = _GETLEVELRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetLevelRequest = _reflection.GeneratedProtocolMessageType('GetLevelRequest', (_message.Message,), {'DESCRIPTOR': _GETLEVELREQUEST,
 '__module__': 'eve.sovereignty.activitydefensemodifier.api.requests_pb2'})
_sym_db.RegisterMessage(GetLevelRequest)
GetLevelResponse = _reflection.GeneratedProtocolMessageType('GetLevelResponse', (_message.Message,), {'DESCRIPTOR': _GETLEVELRESPONSE,
 '__module__': 'eve.sovereignty.activitydefensemodifier.api.requests_pb2'})
_sym_db.RegisterMessage(GetLevelResponse)
DESCRIPTOR._options = None
