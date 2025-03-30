#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\opportunity\opportunity_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.agent import agent_pb2 as eve__public_dot_agent_dot_agent__pb2
from eveProto.generated.eve_public.dailygoal import goal_pb2 as eve__public_dot_dailygoal_dot_goal__pb2
from eveProto.generated.eve_public.dungeon import dungeon_pb2 as eve__public_dot_dungeon_dot_dungeon__pb2
from eveProto.generated.eve_public.dungeon import instance_pb2 as eve__public_dot_dungeon_dot_instance__pb2
from eveProto.generated.eve_public.epicarc import epicarc_pb2 as eve__public_dot_epicarc_dot_epicarc__pb2
from eveProto.generated.eve_public.faction import faction_pb2 as eve__public_dot_faction_dot_faction__pb2
from eveProto.generated.eve_public.freelance.project import project_pb2 as eve__public_dot_freelance_dot_project_dot_project__pb2
from eveProto.generated.eve_public.goal import goal_pb2 as eve__public_dot_goal_dot_goal__pb2
from eveProto.generated.eve_public.mission import mission_pb2 as eve__public_dot_mission_dot_mission__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/opportunity/opportunity.proto', package='eve_public.opportunity', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/opportunity', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve_public/opportunity/opportunity.proto\x12\x16eve_public.opportunity\x1a\x1ceve_public/agent/agent.proto\x1a\x1feve_public/dailygoal/goal.proto\x1a eve_public/dungeon/dungeon.proto\x1a!eve_public/dungeon/instance.proto\x1a eve_public/epicarc/epicarc.proto\x1a eve_public/faction/faction.proto\x1a*eve_public/freelance/project/project.proto\x1a\x1aeve_public/goal/goal.proto\x1a eve_public/mission/mission.proto"\xdf\x06\n\nIdentifier\x12=\n\x07dungeon\x18\x01 \x01(\x0b2*.eve_public.opportunity.Identifier.DungeonH\x00\x12+\n\x04goal\x18\x02 \x01(\x0b2\x1b.eve_public.goal.IdentifierH\x00\x12=\n\x07mission\x18\x03 \x01(\x0b2*.eve_public.opportunity.Identifier.MissionH\x00\x12Q\n\nenlistment\x18\x04 \x01(\x0b2;.eve_public.opportunity.Identifier.FactionWarfareEnlistmentH\x00\x12A\n\tstoryline\x18\x05 \x01(\x0b2,.eve_public.opportunity.Identifier.StorylineH\x00\x121\n\x07epicarc\x18\x06 \x01(\x0b2\x1e.eve_public.epicarc.IdentifierH\x00\x126\n\ndaily_goal\x18\x07 \x01(\x0b2 .eve_public.dailygoal.IdentifierH\x00\x12E\n\x11freelance_project\x18\x08 \x01(\x0b2(.eve_public.freelance.project.IdentifierH\x00\x1au\n\x07Dungeon\x12/\n\x07dungeon\x18\x01 \x01(\x0b2\x1e.eve_public.dungeon.Identifier\x129\n\x08instance\x18\x02 \x01(\x0b2\'.eve_public.dungeon.instance.Identifier\x1ag\n\x07Mission\x12/\n\x07mission\x18\x01 \x01(\x0b2\x1e.eve_public.mission.Identifier\x12+\n\x05agent\x18\x02 \x01(\x0b2\x1c.eve_public.agent.Identifier\x1aK\n\x18FactionWarfareEnlistment\x12/\n\x07faction\x18\x01 \x01(\x0b2\x1e.eve_public.faction.Identifier\x1a"\n\tStoryline\x12\x15\n\rcontent_label\x18\x01 \x01(\tB\r\n\x0bopportunityBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/opportunityb\x06proto3', dependencies=[eve__public_dot_agent_dot_agent__pb2.DESCRIPTOR,
 eve__public_dot_dailygoal_dot_goal__pb2.DESCRIPTOR,
 eve__public_dot_dungeon_dot_dungeon__pb2.DESCRIPTOR,
 eve__public_dot_dungeon_dot_instance__pb2.DESCRIPTOR,
 eve__public_dot_epicarc_dot_epicarc__pb2.DESCRIPTOR,
 eve__public_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve__public_dot_freelance_dot_project_dot_project__pb2.DESCRIPTOR,
 eve__public_dot_goal_dot_goal__pb2.DESCRIPTOR,
 eve__public_dot_mission_dot_mission__pb2.DESCRIPTOR])
_IDENTIFIER_DUNGEON = _descriptor.Descriptor(name='Dungeon', full_name='eve_public.opportunity.Identifier.Dungeon', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='dungeon', full_name='eve_public.opportunity.Identifier.Dungeon.dungeon', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='instance', full_name='eve_public.opportunity.Identifier.Dungeon.instance', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=888, serialized_end=1005)
_IDENTIFIER_MISSION = _descriptor.Descriptor(name='Mission', full_name='eve_public.opportunity.Identifier.Mission', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='mission', full_name='eve_public.opportunity.Identifier.Mission.mission', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='agent', full_name='eve_public.opportunity.Identifier.Mission.agent', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1007, serialized_end=1110)
_IDENTIFIER_FACTIONWARFAREENLISTMENT = _descriptor.Descriptor(name='FactionWarfareEnlistment', full_name='eve_public.opportunity.Identifier.FactionWarfareEnlistment', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction', full_name='eve_public.opportunity.Identifier.FactionWarfareEnlistment.faction', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1112, serialized_end=1187)
_IDENTIFIER_STORYLINE = _descriptor.Descriptor(name='Storyline', full_name='eve_public.opportunity.Identifier.Storyline', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='content_label', full_name='eve_public.opportunity.Identifier.Storyline.content_label', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1189, serialized_end=1223)
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.opportunity.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='dungeon', full_name='eve_public.opportunity.Identifier.dungeon', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='goal', full_name='eve_public.opportunity.Identifier.goal', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='mission', full_name='eve_public.opportunity.Identifier.mission', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='enlistment', full_name='eve_public.opportunity.Identifier.enlistment', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='storyline', full_name='eve_public.opportunity.Identifier.storyline', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='epicarc', full_name='eve_public.opportunity.Identifier.epicarc', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='daily_goal', full_name='eve_public.opportunity.Identifier.daily_goal', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='freelance_project', full_name='eve_public.opportunity.Identifier.freelance_project', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_IDENTIFIER_DUNGEON,
 _IDENTIFIER_MISSION,
 _IDENTIFIER_FACTIONWARFAREENLISTMENT,
 _IDENTIFIER_STORYLINE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='opportunity', full_name='eve_public.opportunity.Identifier.opportunity', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=375, serialized_end=1238)
_IDENTIFIER_DUNGEON.fields_by_name['dungeon'].message_type = eve__public_dot_dungeon_dot_dungeon__pb2._IDENTIFIER
_IDENTIFIER_DUNGEON.fields_by_name['instance'].message_type = eve__public_dot_dungeon_dot_instance__pb2._IDENTIFIER
_IDENTIFIER_DUNGEON.containing_type = _IDENTIFIER
_IDENTIFIER_MISSION.fields_by_name['mission'].message_type = eve__public_dot_mission_dot_mission__pb2._IDENTIFIER
_IDENTIFIER_MISSION.fields_by_name['agent'].message_type = eve__public_dot_agent_dot_agent__pb2._IDENTIFIER
_IDENTIFIER_MISSION.containing_type = _IDENTIFIER
_IDENTIFIER_FACTIONWARFAREENLISTMENT.fields_by_name['faction'].message_type = eve__public_dot_faction_dot_faction__pb2._IDENTIFIER
_IDENTIFIER_FACTIONWARFAREENLISTMENT.containing_type = _IDENTIFIER
_IDENTIFIER_STORYLINE.containing_type = _IDENTIFIER
_IDENTIFIER.fields_by_name['dungeon'].message_type = _IDENTIFIER_DUNGEON
_IDENTIFIER.fields_by_name['goal'].message_type = eve__public_dot_goal_dot_goal__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['mission'].message_type = _IDENTIFIER_MISSION
_IDENTIFIER.fields_by_name['enlistment'].message_type = _IDENTIFIER_FACTIONWARFAREENLISTMENT
_IDENTIFIER.fields_by_name['storyline'].message_type = _IDENTIFIER_STORYLINE
_IDENTIFIER.fields_by_name['epicarc'].message_type = eve__public_dot_epicarc_dot_epicarc__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['daily_goal'].message_type = eve__public_dot_dailygoal_dot_goal__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['freelance_project'].message_type = eve__public_dot_freelance_dot_project_dot_project__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['dungeon'])
_IDENTIFIER.fields_by_name['dungeon'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['goal'])
_IDENTIFIER.fields_by_name['goal'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['mission'])
_IDENTIFIER.fields_by_name['mission'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['enlistment'])
_IDENTIFIER.fields_by_name['enlistment'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['storyline'])
_IDENTIFIER.fields_by_name['storyline'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['epicarc'])
_IDENTIFIER.fields_by_name['epicarc'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['daily_goal'])
_IDENTIFIER.fields_by_name['daily_goal'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
_IDENTIFIER.oneofs_by_name['opportunity'].fields.append(_IDENTIFIER.fields_by_name['freelance_project'])
_IDENTIFIER.fields_by_name['freelance_project'].containing_oneof = _IDENTIFIER.oneofs_by_name['opportunity']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'Dungeon': _reflection.GeneratedProtocolMessageType('Dungeon', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER_DUNGEON,
             '__module__': 'eve_public.opportunity.opportunity_pb2'}),
 'Mission': _reflection.GeneratedProtocolMessageType('Mission', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER_MISSION,
             '__module__': 'eve_public.opportunity.opportunity_pb2'}),
 'FactionWarfareEnlistment': _reflection.GeneratedProtocolMessageType('FactionWarfareEnlistment', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER_FACTIONWARFAREENLISTMENT,
                              '__module__': 'eve_public.opportunity.opportunity_pb2'}),
 'Storyline': _reflection.GeneratedProtocolMessageType('Storyline', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER_STORYLINE,
               '__module__': 'eve_public.opportunity.opportunity_pb2'}),
 'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.opportunity.opportunity_pb2'})
_sym_db.RegisterMessage(Identifier)
_sym_db.RegisterMessage(Identifier.Dungeon)
_sym_db.RegisterMessage(Identifier.Mission)
_sym_db.RegisterMessage(Identifier.FactionWarfareEnlistment)
_sym_db.RegisterMessage(Identifier.Storyline)
DESCRIPTOR._options = None
