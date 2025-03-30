#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\dungeon\api\trigger_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.dungeon import instance_pb2 as eve_dot_dungeon_dot_instance__pb2
from eveProto.generated.eve.dungeon import trigger_pb2 as eve_dot_dungeon_dot_trigger__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/dungeon/api/trigger.proto', package='eve.dungeon.api', syntax='proto3', serialized_options='Z:github.com/ccpgames/eve-proto-go/generated/eve/dungeon/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/dungeon/api/trigger.proto\x12\x0feve.dungeon.api\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x1aeve/dungeon/instance.proto\x1a\x19eve/dungeon/trigger.proto\x1a\x19eve/faction/faction.proto\x1a eve/inventory/generic_item.proto\x1a!eve/solarsystem/solarsystem.proto"\xc4\x03\n\x14TriggerInputReceived\x12%\n\x07trigger\x18\x01 \x01(\x0b2\x14.eve.dungeon.Trigger\x12:\n\x10dungeon_instance\x18\x02 \x01(\x0b2 .eve.dungeon.instance.Identifier\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12/\n\x0ccontributors\x18\x04 \x03(\x0b2\x19.eve.character.Identifier\x12\x11\n\x07unknown\x18\x05 \x01(\x08H\x00\x125\n\x04item\x18\x06 \x01(\x0b2%.eve.inventory.genericitem.IdentifierH\x00\x12.\n\tcharacter\x18\x07 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x08 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12*\n\x07faction\x18\t \x01(\x0b2\x17.eve.faction.IdentifierH\x00B\x0b\n\tactivator"\xe7\x01\n\x15TriggerEventActivated\x120\n\rtrigger_event\x18\x01 \x01(\x0b2\x19.eve.dungeon.TriggerEvent\x12:\n\x10dungeon_instance\x18\x02 \x01(\x0b2 .eve.dungeon.instance.Identifier\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12-\n\ncharacters\x18\x04 \x03(\x0b2\x19.eve.character.IdentifierB<Z:github.com/ccpgames/eve-proto-go/generated/eve/dungeon/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_dungeon_dot_instance__pb2.DESCRIPTOR,
 eve_dot_dungeon_dot_trigger__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_TRIGGERINPUTRECEIVED = _descriptor.Descriptor(name='TriggerInputReceived', full_name='eve.dungeon.api.TriggerInputReceived', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='trigger', full_name='eve.dungeon.api.TriggerInputReceived.trigger', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='dungeon_instance', full_name='eve.dungeon.api.TriggerInputReceived.dungeon_instance', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.dungeon.api.TriggerInputReceived.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='contributors', full_name='eve.dungeon.api.TriggerInputReceived.contributors', index=3, number=4, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown', full_name='eve.dungeon.api.TriggerInputReceived.unknown', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='item', full_name='eve.dungeon.api.TriggerInputReceived.item', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.dungeon.api.TriggerInputReceived.character', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.dungeon.api.TriggerInputReceived.corporation', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='faction', full_name='eve.dungeon.api.TriggerInputReceived.faction', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='activator', full_name='eve.dungeon.api.TriggerInputReceived.activator', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=268, serialized_end=720)
_TRIGGEREVENTACTIVATED = _descriptor.Descriptor(name='TriggerEventActivated', full_name='eve.dungeon.api.TriggerEventActivated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='trigger_event', full_name='eve.dungeon.api.TriggerEventActivated.trigger_event', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='dungeon_instance', full_name='eve.dungeon.api.TriggerEventActivated.dungeon_instance', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.dungeon.api.TriggerEventActivated.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='characters', full_name='eve.dungeon.api.TriggerEventActivated.characters', index=3, number=4, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=723, serialized_end=954)
_TRIGGERINPUTRECEIVED.fields_by_name['trigger'].message_type = eve_dot_dungeon_dot_trigger__pb2._TRIGGER
_TRIGGERINPUTRECEIVED.fields_by_name['dungeon_instance'].message_type = eve_dot_dungeon_dot_instance__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['contributors'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.fields_by_name['faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_TRIGGERINPUTRECEIVED.oneofs_by_name['activator'].fields.append(_TRIGGERINPUTRECEIVED.fields_by_name['unknown'])
_TRIGGERINPUTRECEIVED.fields_by_name['unknown'].containing_oneof = _TRIGGERINPUTRECEIVED.oneofs_by_name['activator']
_TRIGGERINPUTRECEIVED.oneofs_by_name['activator'].fields.append(_TRIGGERINPUTRECEIVED.fields_by_name['item'])
_TRIGGERINPUTRECEIVED.fields_by_name['item'].containing_oneof = _TRIGGERINPUTRECEIVED.oneofs_by_name['activator']
_TRIGGERINPUTRECEIVED.oneofs_by_name['activator'].fields.append(_TRIGGERINPUTRECEIVED.fields_by_name['character'])
_TRIGGERINPUTRECEIVED.fields_by_name['character'].containing_oneof = _TRIGGERINPUTRECEIVED.oneofs_by_name['activator']
_TRIGGERINPUTRECEIVED.oneofs_by_name['activator'].fields.append(_TRIGGERINPUTRECEIVED.fields_by_name['corporation'])
_TRIGGERINPUTRECEIVED.fields_by_name['corporation'].containing_oneof = _TRIGGERINPUTRECEIVED.oneofs_by_name['activator']
_TRIGGERINPUTRECEIVED.oneofs_by_name['activator'].fields.append(_TRIGGERINPUTRECEIVED.fields_by_name['faction'])
_TRIGGERINPUTRECEIVED.fields_by_name['faction'].containing_oneof = _TRIGGERINPUTRECEIVED.oneofs_by_name['activator']
_TRIGGEREVENTACTIVATED.fields_by_name['trigger_event'].message_type = eve_dot_dungeon_dot_trigger__pb2._TRIGGEREVENT
_TRIGGEREVENTACTIVATED.fields_by_name['dungeon_instance'].message_type = eve_dot_dungeon_dot_instance__pb2._IDENTIFIER
_TRIGGEREVENTACTIVATED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_TRIGGEREVENTACTIVATED.fields_by_name['characters'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['TriggerInputReceived'] = _TRIGGERINPUTRECEIVED
DESCRIPTOR.message_types_by_name['TriggerEventActivated'] = _TRIGGEREVENTACTIVATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
TriggerInputReceived = _reflection.GeneratedProtocolMessageType('TriggerInputReceived', (_message.Message,), {'DESCRIPTOR': _TRIGGERINPUTRECEIVED,
 '__module__': 'eve.dungeon.api.trigger_pb2'})
_sym_db.RegisterMessage(TriggerInputReceived)
TriggerEventActivated = _reflection.GeneratedProtocolMessageType('TriggerEventActivated', (_message.Message,), {'DESCRIPTOR': _TRIGGEREVENTACTIVATED,
 '__module__': 'eve.dungeon.api.trigger_pb2'})
_sym_db.RegisterMessage(TriggerEventActivated)
DESCRIPTOR._options = None
