#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\npc\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/npc/event.proto', package='eve.npc.event', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/npc/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/npc/event.proto\x12\reve.npc.event\x1a\x1deve/character/character.proto\x1a\x19eve/faction/faction.proto\x1a\x11eve/isk/isk.proto\x1a!eve/solarsystem/solarsystem.proto"\xc5\x01\n\nBountyPaid\x12,\n\trecipient\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12/\n\x0etarget_faction\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier\x12%\n\nnet_income\x18\x03 \x01(\x0b2\x11.eve.isk.Currency\x121\n\x0csolar_system\x18\x04 \x01(\x0b2\x1b.eve.solarsystem.IdentifierB:Z8github.com/ccpgames/eve-proto-go/generated/eve/npc/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_faction_dot_faction__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_BOUNTYPAID = _descriptor.Descriptor(name='BountyPaid', full_name='eve.npc.event.BountyPaid', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='recipient', full_name='eve.npc.event.BountyPaid.recipient', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='target_faction', full_name='eve.npc.event.BountyPaid.target_faction', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='net_income', full_name='eve.npc.event.BountyPaid.net_income', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.npc.event.BountyPaid.solar_system', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=151, serialized_end=348)
_BOUNTYPAID.fields_by_name['recipient'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_BOUNTYPAID.fields_by_name['target_faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_BOUNTYPAID.fields_by_name['net_income'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_BOUNTYPAID.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['BountyPaid'] = _BOUNTYPAID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
BountyPaid = _reflection.GeneratedProtocolMessageType('BountyPaid', (_message.Message,), {'DESCRIPTOR': _BOUNTYPAID,
 '__module__': 'eve.npc.event_pb2'})
_sym_db.RegisterMessage(BountyPaid)
DESCRIPTOR._options = None
