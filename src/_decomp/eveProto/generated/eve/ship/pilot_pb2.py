#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\pilot_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/pilot.proto', package='eve.ship', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/ship/pilot', create_key=_descriptor._internal_create_key, serialized_pb='\n\x14eve/ship/pilot.proto\x12\x08eve.ship\x1a\x1deve/character/character.proto"S\n\x05Pilot\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x12\x11\n\x07unknown\x18\x02 \x01(\x08H\x00B\x07\n\x05pilotB;Z9github.com/ccpgames/eve-proto-go/generated/eve/ship/pilotb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_PILOT = _descriptor.Descriptor(name='Pilot', full_name='eve.ship.Pilot', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.Pilot.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='unknown', full_name='eve.ship.Pilot.unknown', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='pilot', full_name='eve.ship.Pilot.pilot', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=65, serialized_end=148)
_PILOT.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PILOT.oneofs_by_name['pilot'].fields.append(_PILOT.fields_by_name['character'])
_PILOT.fields_by_name['character'].containing_oneof = _PILOT.oneofs_by_name['pilot']
_PILOT.oneofs_by_name['pilot'].fields.append(_PILOT.fields_by_name['unknown'])
_PILOT.fields_by_name['unknown'].containing_oneof = _PILOT.oneofs_by_name['pilot']
DESCRIPTOR.message_types_by_name['Pilot'] = _PILOT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Pilot = _reflection.GeneratedProtocolMessageType('Pilot', (_message.Message,), {'DESCRIPTOR': _PILOT,
 '__module__': 'eve.ship.pilot_pb2'})
_sym_db.RegisterMessage(Pilot)
DESCRIPTOR._options = None
