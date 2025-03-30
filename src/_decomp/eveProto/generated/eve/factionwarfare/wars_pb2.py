#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\wars_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/wars.proto', package='eve.factionwarfare.wars', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/wars', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/factionwarfare/wars.proto\x12\x17eve.factionwarfare.wars\x1a\x19eve/faction/faction.proto"g\n\x03War\x12+\n\nfaction_id\x18\x01 \x01(\x0b2\x17.eve.faction.Identifier\x123\n\x12against_faction_id\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier"\x0c\n\nGetRequest"9\n\x0bGetResponse\x12*\n\x04wars\x18\x01 \x03(\x0b2\x1c.eve.factionwarfare.wars.WarBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/warsb\x06proto3', dependencies=[eve_dot_faction_dot_faction__pb2.DESCRIPTOR])
_WAR = _descriptor.Descriptor(name='War', full_name='eve.factionwarfare.wars.War', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction_id', full_name='eve.factionwarfare.wars.War.faction_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='against_faction_id', full_name='eve.factionwarfare.wars.War.against_faction_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=85, serialized_end=188)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.factionwarfare.wars.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=190, serialized_end=202)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.factionwarfare.wars.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='wars', full_name='eve.factionwarfare.wars.GetResponse.wars', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=204, serialized_end=261)
_WAR.fields_by_name['faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_WAR.fields_by_name['against_faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['wars'].message_type = _WAR
DESCRIPTOR.message_types_by_name['War'] = _WAR
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
War = _reflection.GeneratedProtocolMessageType('War', (_message.Message,), {'DESCRIPTOR': _WAR,
 '__module__': 'eve.factionwarfare.wars_pb2'})
_sym_db.RegisterMessage(War)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.factionwarfare.wars_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.factionwarfare.wars_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
