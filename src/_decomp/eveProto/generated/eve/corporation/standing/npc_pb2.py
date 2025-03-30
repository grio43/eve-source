#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\standing\npc_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.agent import agent_pb2 as eve_dot_agent_dot_agent__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.standing import standing_pb2 as eve_dot_standing_dot_standing__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/standing/npc.proto', package='eve.corporation.standing.npc', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/standing/npc', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/corporation/standing/npc.proto\x12\x1ceve.corporation.standing.npc\x1a\x15eve/agent/agent.proto\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x19eve/faction/faction.proto\x1a\x1beve/standing/standing.proto"\x98\x01\n\rGetAllRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x124\n\x11requesting_member\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12\x0c\n\x04page\x18\x03 \x01(\r\x12\x11\n\tpage_size\x18\x04 \x01(\r"\xbf\x02\n\x0eGetAllResponse\x12O\n\rnpc_standings\x18\x01 \x03(\x0b28.eve.corporation.standing.npc.GetAllResponse.NpcStanding\x1a\xdb\x01\n\x0bNpcStanding\x12*\n\x07faction\x18\x01 \x01(\x0b2\x17.eve.faction.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12&\n\x05agent\x18\x03 \x01(\x0b2\x15.eve.agent.IdentifierH\x00\x12\x11\n\x07unknown\x18\x04 \x01(\x04H\x00\x12%\n\x08standing\x18\x05 \x01(\x0b2\x13.eve.standing.ValueB\n\n\x08from_npcBIZGgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/standing/npcb\x06proto3', dependencies=[eve_dot_agent_dot_agent__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_standing_dot_standing__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.corporation.standing.npc.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.standing.npc.GetAllRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='requesting_member', full_name='eve.corporation.standing.npc.GetAllRequest.requesting_member', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='page', full_name='eve.corporation.standing.npc.GetAllRequest.page', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='page_size', full_name='eve.corporation.standing.npc.GetAllRequest.page_size', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=214, serialized_end=366)
_GETALLRESPONSE_NPCSTANDING = _descriptor.Descriptor(name='NpcStanding', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.faction', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='agent', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.agent', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.unknown', index=3, number=4, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='standing', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.standing', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='from_npc', full_name='eve.corporation.standing.npc.GetAllResponse.NpcStanding.from_npc', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=469, serialized_end=688)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.corporation.standing.npc.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='npc_standings', full_name='eve.corporation.standing.npc.GetAllResponse.npc_standings', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETALLRESPONSE_NPCSTANDING], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=369, serialized_end=688)
_GETALLREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETALLREQUEST.fields_by_name['requesting_member'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETALLRESPONSE_NPCSTANDING.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_GETALLRESPONSE_NPCSTANDING.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETALLRESPONSE_NPCSTANDING.fields_by_name['agent'].message_type = eve_dot_agent_dot_agent__pb2._IDENTIFIER
_GETALLRESPONSE_NPCSTANDING.fields_by_name['standing'].message_type = eve_dot_standing_dot_standing__pb2._VALUE
_GETALLRESPONSE_NPCSTANDING.containing_type = _GETALLRESPONSE
_GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc'].fields.append(_GETALLRESPONSE_NPCSTANDING.fields_by_name['faction'])
_GETALLRESPONSE_NPCSTANDING.fields_by_name['faction'].containing_oneof = _GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc']
_GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc'].fields.append(_GETALLRESPONSE_NPCSTANDING.fields_by_name['corporation'])
_GETALLRESPONSE_NPCSTANDING.fields_by_name['corporation'].containing_oneof = _GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc']
_GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc'].fields.append(_GETALLRESPONSE_NPCSTANDING.fields_by_name['agent'])
_GETALLRESPONSE_NPCSTANDING.fields_by_name['agent'].containing_oneof = _GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc']
_GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc'].fields.append(_GETALLRESPONSE_NPCSTANDING.fields_by_name['unknown'])
_GETALLRESPONSE_NPCSTANDING.fields_by_name['unknown'].containing_oneof = _GETALLRESPONSE_NPCSTANDING.oneofs_by_name['from_npc']
_GETALLRESPONSE.fields_by_name['npc_standings'].message_type = _GETALLRESPONSE_NPCSTANDING
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.corporation.standing.npc_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'NpcStanding': _reflection.GeneratedProtocolMessageType('NpcStanding', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE_NPCSTANDING,
                 '__module__': 'eve.corporation.standing.npc_pb2'}),
 'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.corporation.standing.npc_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
_sym_db.RegisterMessage(GetAllResponse.NpcStanding)
DESCRIPTOR._options = None
