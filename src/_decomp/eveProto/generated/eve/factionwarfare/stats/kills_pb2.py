#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\stats\kills_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/stats/kills.proto', package='eve.factionwarfare.stats', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/stats', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/factionwarfare/stats/kills.proto\x12\x18eve.factionwarfare.stats"<\n\x05Kills\x12\x11\n\tyesterday\x18\x01 \x01(\x04\x12\x11\n\tlast_week\x18\x02 \x01(\x04\x12\r\n\x05total\x18\x03 \x01(\x04BEZCgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/statsb\x06proto3')
_KILLS = _descriptor.Descriptor(name='Kills', full_name='eve.factionwarfare.stats.Kills', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='yesterday', full_name='eve.factionwarfare.stats.Kills.yesterday', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='last_week', full_name='eve.factionwarfare.stats.Kills.last_week', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='total', full_name='eve.factionwarfare.stats.Kills.total', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=66, serialized_end=126)
DESCRIPTOR.message_types_by_name['Kills'] = _KILLS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Kills = _reflection.GeneratedProtocolMessageType('Kills', (_message.Message,), {'DESCRIPTOR': _KILLS,
 '__module__': 'eve.factionwarfare.stats.kills_pb2'})
_sym_db.RegisterMessage(Kills)
DESCRIPTOR._options = None
