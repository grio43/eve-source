#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\stats\corporation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.factionwarfare.stats import kills_pb2 as eve_dot_factionwarfare_dot_stats_dot_kills__pb2
from eveProto.generated.eve.factionwarfare.stats import victorypoints_pb2 as eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/stats/corporation.proto', package='eve.factionwarfare.stats.corporation', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/stats/corporation', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve/factionwarfare/stats/corporation.proto\x12$eve.factionwarfare.stats.corporation\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x19eve/faction/faction.proto\x1a$eve/factionwarfare/stats/kills.proto\x1a,eve/factionwarfare/stats/victorypoints.proto\x1a\x1fgoogle/protobuf/timestamp.proto"z\n\nGetRequest\x123\n\x0ecorporation_id\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x127\n\x14requesting_member_id\x18\x02 \x01(\x0b2\x19.eve.character.Identifier"\x8b\x02\n\x0bGetResponse\x12+\n\nfaction_id\x18\x01 \x01(\x0b2\x17.eve.faction.Identifier\x126\n\x12enlisting_datetime\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x14\n\x0cpilots_count\x18\x03 \x01(\r\x12.\n\x05kills\x18\x04 \x01(\x0b2\x1f.eve.factionwarfare.stats.Kills\x12?\n\x0evictory_points\x18\x05 \x01(\x0b2\'.eve.factionwarfare.stats.VictoryPoints\x12\x10\n\x08enlisted\x18\x06 \x01(\x08BQZOgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/stats/corporationb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_factionwarfare_dot_stats_dot_kills__pb2.DESCRIPTOR,
 eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.factionwarfare.stats.corporation.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation_id', full_name='eve.factionwarfare.stats.corporation.GetRequest.corporation_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='requesting_member_id', full_name='eve.factionwarfare.stats.corporation.GetRequest.requesting_member_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=294, serialized_end=416)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.factionwarfare.stats.corporation.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction_id', full_name='eve.factionwarfare.stats.corporation.GetResponse.faction_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='enlisting_datetime', full_name='eve.factionwarfare.stats.corporation.GetResponse.enlisting_datetime', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='pilots_count', full_name='eve.factionwarfare.stats.corporation.GetResponse.pilots_count', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='kills', full_name='eve.factionwarfare.stats.corporation.GetResponse.kills', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='victory_points', full_name='eve.factionwarfare.stats.corporation.GetResponse.victory_points', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='enlisted', full_name='eve.factionwarfare.stats.corporation.GetResponse.enlisted', index=5, number=6, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=419, serialized_end=686)
_GETREQUEST.fields_by_name['corporation_id'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['requesting_member_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['enlisting_datetime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETRESPONSE.fields_by_name['kills'].message_type = eve_dot_factionwarfare_dot_stats_dot_kills__pb2._KILLS
_GETRESPONSE.fields_by_name['victory_points'].message_type = eve_dot_factionwarfare_dot_stats_dot_victorypoints__pb2._VICTORYPOINTS
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.factionwarfare.stats.corporation_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.factionwarfare.stats.corporation_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
