#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\agent\agent_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/agent/agent.proto', package='eve.agent', syntax='proto3', serialized_options='Z4github.com/ccpgames/eve-proto-go/generated/eve/agent', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/agent/agent.proto\x12\teve.agent\x1a\x1deve/character/character.proto\x1a\x10eve/search.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\x1a\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t"J\n\x1aConversationOptionSelected\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"7\n\x07Greeted\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"G\n\x17MissionMilestoneReached\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"K\n\x1bMissionJournalInfoRetrieved\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"0\n\rSearchRequest\x12\x1f\n\x05query\x18\x01 \x01(\x0b2\x10.eve.SearchQuery"7\n\x0eSearchResponse\x12%\n\x06agents\x18\x01 \x03(\x0b2\x15.eve.agent.Identifier"2\n\nGetRequest\x12$\n\x05agent\x18\x01 \x01(\x0b2\x15.eve.agent.Identifier"3\n\x0bGetResponse\x12$\n\x05agent\x18\x01 \x01(\x0b2\x15.eve.agent.Attributes*\xf1\x02\n\tAgentType\x12\x1a\n\x16AGENT_TYPE_UNSPECIFIED\x10\x00\x12\x14\n\x10AGENT_TYPE_BASIC\x10\x01\x12\x17\n\x13AGENT_TYPE_TUTORIAL\x10\x02\x12\x17\n\x13AGENT_TYPE_RESEARCH\x10\x03\x12\x16\n\x12AGENT_TYPE_CONCORD\x10\x04\x12(\n$AGENT_TYPE_GENERIC_STORYLINE_MISSION\x10\x05\x12 \n\x1cAGENT_TYPE_STORYLINE_MISSION\x10\x06\x12\x1c\n\x18AGENT_TYPE_EVENT_MISSION\x10\x07\x12 \n\x1cAGENT_TYPE_FACTIONAL_WARFARE\x10\x08\x12\x17\n\x13AGENT_TYPE_EPIC_ARC\x10\t\x12\x13\n\x0fAGENT_TYPE_AURA\x10\n\x12\x15\n\x11AGENT_TYPE_CAREER\x10\x0b\x12\x17\n\x13AGENT_TYPE_HERALDRY\x10\x0c*\xd0\x02\n\rAgentDivision\x12\x18\n\x14DIVISION_UNSPECIFIED\x10\x00\x12%\n!DIVISION_RESEARCH_AND_DEVELOPMENT\x10\x01\x12\x19\n\x15DIVISION_DISTRIBUTION\x10\x02\x12\x13\n\x0fDIVISION_MINING\x10\x03\x12\x15\n\x11DIVISION_SECURITY\x10\x04\x12\x1c\n\x18DIVISION_BUSINESS_CAREER\x10\x05\x12\x1f\n\x1bDIVISION_EXPLORATION_CAREER\x10\x06\x12\x1c\n\x18DIVISION_INDUSTRY_CAREER\x10\x07\x12\x1c\n\x18DIVISION_MILITARY_CAREER\x10\x08\x12%\n!DIVISION_ADVANCED_MILITARY_CAREER\x10\t\x12\x15\n\x11DIVISION_HERALDRY\x10\nB6Z4github.com/ccpgames/eve-proto-go/generated/eve/agentb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_search__pb2.DESCRIPTOR])
_AGENTTYPE = _descriptor.EnumDescriptor(name='AgentType', full_name='eve.agent.AgentType', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='AGENT_TYPE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_BASIC', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_TUTORIAL', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_RESEARCH', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_CONCORD', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_GENERIC_STORYLINE_MISSION', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_STORYLINE_MISSION', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_EVENT_MISSION', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_FACTIONAL_WARFARE', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_EPIC_ARC', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_AURA', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_CAREER', index=11, number=11, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='AGENT_TYPE_HERALDRY', index=12, number=12, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=643, serialized_end=1012)
_sym_db.RegisterEnumDescriptor(_AGENTTYPE)
AgentType = enum_type_wrapper.EnumTypeWrapper(_AGENTTYPE)
_AGENTDIVISION = _descriptor.EnumDescriptor(name='AgentDivision', full_name='eve.agent.AgentDivision', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='DIVISION_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_RESEARCH_AND_DEVELOPMENT', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_DISTRIBUTION', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_MINING', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_SECURITY', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_BUSINESS_CAREER', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_EXPLORATION_CAREER', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_INDUSTRY_CAREER', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_MILITARY_CAREER', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_ADVANCED_MILITARY_CAREER', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='DIVISION_HERALDRY', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1015, serialized_end=1351)
_sym_db.RegisterEnumDescriptor(_AGENTDIVISION)
AgentDivision = enum_type_wrapper.EnumTypeWrapper(_AGENTDIVISION)
AGENT_TYPE_UNSPECIFIED = 0
AGENT_TYPE_BASIC = 1
AGENT_TYPE_TUTORIAL = 2
AGENT_TYPE_RESEARCH = 3
AGENT_TYPE_CONCORD = 4
AGENT_TYPE_GENERIC_STORYLINE_MISSION = 5
AGENT_TYPE_STORYLINE_MISSION = 6
AGENT_TYPE_EVENT_MISSION = 7
AGENT_TYPE_FACTIONAL_WARFARE = 8
AGENT_TYPE_EPIC_ARC = 9
AGENT_TYPE_AURA = 10
AGENT_TYPE_CAREER = 11
AGENT_TYPE_HERALDRY = 12
DIVISION_UNSPECIFIED = 0
DIVISION_RESEARCH_AND_DEVELOPMENT = 1
DIVISION_DISTRIBUTION = 2
DIVISION_MINING = 3
DIVISION_SECURITY = 4
DIVISION_BUSINESS_CAREER = 5
DIVISION_EXPLORATION_CAREER = 6
DIVISION_INDUSTRY_CAREER = 7
DIVISION_MILITARY_CAREER = 8
DIVISION_ADVANCED_MILITARY_CAREER = 9
DIVISION_HERALDRY = 10
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.agent.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.agent.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=85, serialized_end=117)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.agent.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.agent.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=119, serialized_end=145)
_CONVERSATIONOPTIONSELECTED = _descriptor.Descriptor(name='ConversationOptionSelected', full_name='eve.agent.ConversationOptionSelected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.agent.ConversationOptionSelected.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=147, serialized_end=221)
_GREETED = _descriptor.Descriptor(name='Greeted', full_name='eve.agent.Greeted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.agent.Greeted.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=223, serialized_end=278)
_MISSIONMILESTONEREACHED = _descriptor.Descriptor(name='MissionMilestoneReached', full_name='eve.agent.MissionMilestoneReached', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.agent.MissionMilestoneReached.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=280, serialized_end=351)
_MISSIONJOURNALINFORETRIEVED = _descriptor.Descriptor(name='MissionJournalInfoRetrieved', full_name='eve.agent.MissionJournalInfoRetrieved', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.agent.MissionJournalInfoRetrieved.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=353, serialized_end=428)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.agent.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='query', full_name='eve.agent.SearchRequest.query', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=430, serialized_end=478)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.agent.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='agents', full_name='eve.agent.SearchResponse.agents', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=480, serialized_end=535)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.agent.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='agent', full_name='eve.agent.GetRequest.agent', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=537, serialized_end=587)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.agent.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='agent', full_name='eve.agent.GetResponse.agent', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=589, serialized_end=640)
_CONVERSATIONOPTIONSELECTED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GREETED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MISSIONMILESTONEREACHED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MISSIONJOURNALINFORETRIEVED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SEARCHREQUEST.fields_by_name['query'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['agents'].message_type = _IDENTIFIER
_GETREQUEST.fields_by_name['agent'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['agent'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['ConversationOptionSelected'] = _CONVERSATIONOPTIONSELECTED
DESCRIPTOR.message_types_by_name['Greeted'] = _GREETED
DESCRIPTOR.message_types_by_name['MissionMilestoneReached'] = _MISSIONMILESTONEREACHED
DESCRIPTOR.message_types_by_name['MissionJournalInfoRetrieved'] = _MISSIONJOURNALINFORETRIEVED
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.enum_types_by_name['AgentType'] = _AGENTTYPE
DESCRIPTOR.enum_types_by_name['AgentDivision'] = _AGENTDIVISION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(Attributes)
ConversationOptionSelected = _reflection.GeneratedProtocolMessageType('ConversationOptionSelected', (_message.Message,), {'DESCRIPTOR': _CONVERSATIONOPTIONSELECTED,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(ConversationOptionSelected)
Greeted = _reflection.GeneratedProtocolMessageType('Greeted', (_message.Message,), {'DESCRIPTOR': _GREETED,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(Greeted)
MissionMilestoneReached = _reflection.GeneratedProtocolMessageType('MissionMilestoneReached', (_message.Message,), {'DESCRIPTOR': _MISSIONMILESTONEREACHED,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(MissionMilestoneReached)
MissionJournalInfoRetrieved = _reflection.GeneratedProtocolMessageType('MissionJournalInfoRetrieved', (_message.Message,), {'DESCRIPTOR': _MISSIONJOURNALINFORETRIEVED,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(MissionJournalInfoRetrieved)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(SearchResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.agent.agent_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
