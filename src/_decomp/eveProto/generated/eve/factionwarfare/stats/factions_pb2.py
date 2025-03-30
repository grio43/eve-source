#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\stats\factions_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.factionwarfare.stats import kills_pb2 as eve_dot_factionwarfare_dot_stats_dot_kills__pb2
from eveProto.generated.eve.factionwarfare.stats import victorypoints_pb2 as eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/stats/factions.proto', package='eve.factionwarfare.stats.factions', syntax='proto3', serialized_options='ZLgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/stats/factions', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/factionwarfare/stats/factions.proto\x12!eve.factionwarfare.stats.factions\x1a\x19eve/faction/faction.proto\x1a$eve/factionwarfare/stats/kills.proto\x1a,eve/factionwarfare/stats/victorypoints.proto"\xde\x01\n\x0cFactionStats\x12+\n\nfaction_id\x18\x01 \x01(\x0b2\x17.eve.faction.Identifier\x12\x14\n\x0cpilots_count\x18\x02 \x01(\r\x12\x1a\n\x12systems_controlled\x18\x03 \x01(\r\x12.\n\x05kills\x18\x04 \x01(\x0b2\x1f.eve.factionwarfare.stats.Kills\x12?\n\x0evictory_points\x18\x05 \x01(\x0b2\'.eve.factionwarfare.stats.VictoryPoints"\x0c\n\nGetRequest"U\n\x0bGetResponse\x12F\n\rfaction_stats\x18\x01 \x03(\x0b2/.eve.factionwarfare.stats.factions.FactionStatsBNZLgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/stats/factionsb\x06proto3', dependencies=[eve_dot_faction_dot_faction__pb2.DESCRIPTOR, eve_dot_factionwarfare_dot_stats_dot_kills__pb2.DESCRIPTOR, eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2.DESCRIPTOR])
_FACTIONSTATS = _descriptor.Descriptor(name='FactionStats', full_name='eve.factionwarfare.stats.factions.FactionStats', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction_id', full_name='eve.factionwarfare.stats.factions.FactionStats.faction_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='pilots_count', full_name='eve.factionwarfare.stats.factions.FactionStats.pilots_count', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='systems_controlled', full_name='eve.factionwarfare.stats.factions.FactionStats.systems_controlled', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='kills', full_name='eve.factionwarfare.stats.factions.FactionStats.kills', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='victory_points', full_name='eve.factionwarfare.stats.factions.FactionStats.victory_points', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=190, serialized_end=412)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.factionwarfare.stats.factions.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=414, serialized_end=426)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.factionwarfare.stats.factions.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction_stats', full_name='eve.factionwarfare.stats.factions.GetResponse.faction_stats', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=428, serialized_end=513)
_FACTIONSTATS.fields_by_name['faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_FACTIONSTATS.fields_by_name['kills'].message_type = eve_dot_factionwarfare_dot_stats_dot_kills__pb2._KILLS
_FACTIONSTATS.fields_by_name['victory_points'].message_type = eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2._VICTORYPOINTS
_GETRESPONSE.fields_by_name['faction_stats'].message_type = _FACTIONSTATS
DESCRIPTOR.message_types_by_name['FactionStats'] = _FACTIONSTATS
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
FactionStats = _reflection.GeneratedProtocolMessageType('FactionStats', (_message.Message,), {'DESCRIPTOR': _FACTIONSTATS,
 '__module__': 'eve.factionwarfare.stats.factions_pb2'})
_sym_db.RegisterMessage(FactionStats)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.factionwarfare.stats.factions_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.factionwarfare.stats.factions_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
