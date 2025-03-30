#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pvp\pvp_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.membership import membership_pb2 as eve_dot_character_dot_membership_dot_membership__pb2
from eveProto.generated.eve.ship import classification_pb2 as eve_dot_ship_dot_classification__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pvp/pvp.proto', package='eve.pvp', syntax='proto3', serialized_options='Z2github.com/ccpgames/eve-proto-go/generated/eve/pvp', create_key=_descriptor._internal_create_key, serialized_pb='\n\x11eve/pvp/pvp.proto\x12\x07eve.pvp\x1a\x1deve/character/character.proto\x1a)eve/character/membership/membership.proto\x1a\x1deve/ship/classification.proto\x1a\x13eve/ship/ship.proto\x1a\x18eve/ship/ship_type.proto"\xff\x01\n\x0bParticipant\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.Identifier\x12+\n\tship_type\x18\x03 \x01(\x0b2\x18.eve.shiptype.Identifier\x127\n\nship_class\x18\x04 \x01(\x0b2#.eve.ship.classification.Identifier\x128\n\nmembership\x18\x05 \x01(\x0b2$.eve.character.membership.AttributesB4Z2github.com/ccpgames/eve-proto-go/generated/eve/pvpb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_character_dot_membership_dot_membership__pb2.DESCRIPTOR,
 eve_dot_ship_dot_classification__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_PARTICIPANT = _descriptor.Descriptor(name='Participant', full_name='eve.pvp.Participant', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.pvp.Participant.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.pvp.Participant.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship_type', full_name='eve.pvp.Participant.ship_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship_class', full_name='eve.pvp.Participant.ship_class', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='membership', full_name='eve.pvp.Participant.membership', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=183, serialized_end=438)
_PARTICIPANT.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PARTICIPANT.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_PARTICIPANT.fields_by_name['ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_PARTICIPANT.fields_by_name['ship_class'].message_type = eve_dot_ship_dot_classification__pb2._IDENTIFIER
_PARTICIPANT.fields_by_name['membership'].message_type = eve_dot_character_dot_membership_dot_membership__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Participant'] = _PARTICIPANT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Participant = _reflection.GeneratedProtocolMessageType('Participant', (_message.Message,), {'DESCRIPTOR': _PARTICIPANT,
 '__module__': 'eve.pvp.pvp_pb2'})
_sym_db.RegisterMessage(Participant)
DESCRIPTOR._options = None
