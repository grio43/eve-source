#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.cosmetic.ship.skin.firstparty import firstparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty import thirdparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/api/events.proto', package='eve.cosmetic.ship.skin.api', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/cosmetic/ship/skin/api/events.proto\x12\x1aeve.cosmetic.ship.skin.api\x1a\x1deve/character/character.proto\x1a2eve/cosmetic/ship/skin/firstparty/firstparty.proto\x1a2eve/cosmetic/ship/skin/thirdparty/thirdparty.proto\x1a\x13eve/ship/ship.proto"\xe9\x01\n\x03Set\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.Identifier\x12C\n\nfirstparty\x18\x03 \x01(\x0b2-.eve.cosmetic.ship.skin.firstparty.IdentifierH\x00\x12C\n\nthirdparty\x18\x04 \x01(\x0b2-.eve.cosmetic.ship.skin.thirdparty.IdentifierH\x00B\x06\n\x04skin"[\n\x07Cleared\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_SET = _descriptor.Descriptor(name='Set', full_name='eve.cosmetic.ship.skin.api.Set', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.cosmetic.ship.skin.api.Set.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.cosmetic.ship.skin.api.Set.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='firstparty', full_name='eve.cosmetic.ship.skin.api.Set.firstparty', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='thirdparty', full_name='eve.cosmetic.ship.skin.api.Set.thirdparty', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='skin', full_name='eve.cosmetic.ship.skin.api.Set.skin', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=228, serialized_end=461)
_CLEARED = _descriptor.Descriptor(name='Cleared', full_name='eve.cosmetic.ship.skin.api.Cleared', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.cosmetic.ship.skin.api.Cleared.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ship', full_name='eve.cosmetic.ship.skin.api.Cleared.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=463, serialized_end=554)
_SET.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SET.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_SET.fields_by_name['firstparty'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2._IDENTIFIER
_SET.fields_by_name['thirdparty'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2._IDENTIFIER
_SET.oneofs_by_name['skin'].fields.append(_SET.fields_by_name['firstparty'])
_SET.fields_by_name['firstparty'].containing_oneof = _SET.oneofs_by_name['skin']
_SET.oneofs_by_name['skin'].fields.append(_SET.fields_by_name['thirdparty'])
_SET.fields_by_name['thirdparty'].containing_oneof = _SET.oneofs_by_name['skin']
_CLEARED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CLEARED.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Set'] = _SET
DESCRIPTOR.message_types_by_name['Cleared'] = _CLEARED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Set = _reflection.GeneratedProtocolMessageType('Set', (_message.Message,), {'DESCRIPTOR': _SET,
 '__module__': 'eve.cosmetic.ship.skin.api.events_pb2'})
_sym_db.RegisterMessage(Set)
Cleared = _reflection.GeneratedProtocolMessageType('Cleared', (_message.Message,), {'DESCRIPTOR': _CLEARED,
 '__module__': 'eve.cosmetic.ship.skin.api.events_pb2'})
_sym_db.RegisterMessage(Cleared)
DESCRIPTOR._options = None
