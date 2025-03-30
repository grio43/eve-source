#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\ownership_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/ownership.proto', package='eve.ship.ownership', syntax='proto3', serialized_options='Z=github.com/ccpgames/eve-proto-go/generated/eve/ship/ownership', create_key=_descriptor._internal_create_key, serialized_pb='\n\x18eve/ship/ownership.proto\x12\x12eve.ship.ownership\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x19eve/faction/faction.proto"\x89\x01\n\x05Owner\x12,\n\x06player\x18\x01 \x01(\x0b2\x1a.eve.ship.ownership.PlayerH\x00\x122\n\tnonplayer\x18\x02 \x01(\x0b2\x1d.eve.ship.ownership.NonPlayerH\x00\x12\x11\n\x07unknown\x18\x03 \x01(\x08H\x00B\x0b\n\townership"y\n\x06Player\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00B\x0b\n\townership"D\n\tNonPlayer\x12*\n\x07faction\x18\x01 \x01(\x0b2\x17.eve.faction.IdentifierH\x00B\x0b\n\townershipB?Z=github.com/ccpgames/eve-proto-go/generated/eve/ship/ownershipb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_faction_dot_faction__pb2.DESCRIPTOR])
_OWNER = _descriptor.Descriptor(name='Owner', full_name='eve.ship.ownership.Owner', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='player', full_name='eve.ship.ownership.Owner.player', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nonplayer', full_name='eve.ship.ownership.Owner.nonplayer', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='unknown', full_name='eve.ship.ownership.Owner.unknown', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='ownership', full_name='eve.ship.ownership.Owner.ownership', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=142, serialized_end=279)
_PLAYER = _descriptor.Descriptor(name='Player', full_name='eve.ship.ownership.Player', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.ownership.Player.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.ship.ownership.Player.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='ownership', full_name='eve.ship.ownership.Player.ownership', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=281, serialized_end=402)
_NONPLAYER = _descriptor.Descriptor(name='NonPlayer', full_name='eve.ship.ownership.NonPlayer', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='faction', full_name='eve.ship.ownership.NonPlayer.faction', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='ownership', full_name='eve.ship.ownership.NonPlayer.ownership', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=404, serialized_end=472)
_OWNER.fields_by_name['player'].message_type = _PLAYER
_OWNER.fields_by_name['nonplayer'].message_type = _NONPLAYER
_OWNER.oneofs_by_name['ownership'].fields.append(_OWNER.fields_by_name['player'])
_OWNER.fields_by_name['player'].containing_oneof = _OWNER.oneofs_by_name['ownership']
_OWNER.oneofs_by_name['ownership'].fields.append(_OWNER.fields_by_name['nonplayer'])
_OWNER.fields_by_name['nonplayer'].containing_oneof = _OWNER.oneofs_by_name['ownership']
_OWNER.oneofs_by_name['ownership'].fields.append(_OWNER.fields_by_name['unknown'])
_OWNER.fields_by_name['unknown'].containing_oneof = _OWNER.oneofs_by_name['ownership']
_PLAYER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PLAYER.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_PLAYER.oneofs_by_name['ownership'].fields.append(_PLAYER.fields_by_name['character'])
_PLAYER.fields_by_name['character'].containing_oneof = _PLAYER.oneofs_by_name['ownership']
_PLAYER.oneofs_by_name['ownership'].fields.append(_PLAYER.fields_by_name['corporation'])
_PLAYER.fields_by_name['corporation'].containing_oneof = _PLAYER.oneofs_by_name['ownership']
_NONPLAYER.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_NONPLAYER.oneofs_by_name['ownership'].fields.append(_NONPLAYER.fields_by_name['faction'])
_NONPLAYER.fields_by_name['faction'].containing_oneof = _NONPLAYER.oneofs_by_name['ownership']
DESCRIPTOR.message_types_by_name['Owner'] = _OWNER
DESCRIPTOR.message_types_by_name['Player'] = _PLAYER
DESCRIPTOR.message_types_by_name['NonPlayer'] = _NONPLAYER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Owner = _reflection.GeneratedProtocolMessageType('Owner', (_message.Message,), {'DESCRIPTOR': _OWNER,
 '__module__': 'eve.ship.ownership_pb2'})
_sym_db.RegisterMessage(Owner)
Player = _reflection.GeneratedProtocolMessageType('Player', (_message.Message,), {'DESCRIPTOR': _PLAYER,
 '__module__': 'eve.ship.ownership_pb2'})
_sym_db.RegisterMessage(Player)
NonPlayer = _reflection.GeneratedProtocolMessageType('NonPlayer', (_message.Message,), {'DESCRIPTOR': _NONPLAYER,
 '__module__': 'eve.ship.ownership_pb2'})
_sym_db.RegisterMessage(NonPlayer)
DESCRIPTOR._options = None
