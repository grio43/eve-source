#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\combat_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/combat.proto', package='eve.factionwarfare.combat', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/combat', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/factionwarfare/combat.proto\x12\x19eve.factionwarfare.combat\x1a\x1deve/character/character.proto"9\n\x0cShipExploded\x12)\n\x06killer\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierBFZDgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/combatb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_SHIPEXPLODED = _descriptor.Descriptor(name='ShipExploded', full_name='eve.factionwarfare.combat.ShipExploded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='killer', full_name='eve.factionwarfare.combat.ShipExploded.killer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=150)
_SHIPEXPLODED.fields_by_name['killer'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ShipExploded'] = _SHIPEXPLODED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ShipExploded = _reflection.GeneratedProtocolMessageType('ShipExploded', (_message.Message,), {'DESCRIPTOR': _SHIPEXPLODED,
 '__module__': 'eve.factionwarfare.combat_pb2'})
_sym_db.RegisterMessage(ShipExploded)
DESCRIPTOR._options = None
