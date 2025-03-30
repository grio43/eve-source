#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\warzone\warzone_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/warzone/warzone.proto', package='eve.factionwarfare.warzone', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/warzone', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/factionwarfare/warzone/warzone.proto\x12\x1aeve.factionwarfare.warzone\x1a\x19eve/faction/faction.proto\x1a!eve/solarsystem/solarsystem.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"j\n\x0cParticipants\x12)\n\x08factions\x18\x01 \x03(\x0b2\x17.eve.faction.Identifier\x12/\n\x0epirate_faction\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier"\x0b\n\tFrontline"\x0c\n\nSecondline"\n\n\x08Backline"\xb4\x02\n\rWarzoneSystem\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12)\n\x08occupier\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier\x12:\n\tfrontline\x18\x03 \x01(\x0b2%.eve.factionwarfare.warzone.FrontlineH\x00\x12<\n\nsecondline\x18\x04 \x01(\x0b2&.eve.factionwarfare.warzone.SecondlineH\x00\x128\n\x08backline\x18\x05 \x01(\x0b2$.eve.factionwarfare.warzone.BacklineH\x00B\x11\n\x0fadjacency_state"\x97\x01\n\x15WarzoneSystemResolved\x129\n\x06system\x18\x01 \x01(\x0b2).eve.factionwarfare.warzone.WarzoneSystem\x12C\n\x10adjacent_systems\x18\x02 \x03(\x0b2).eve.factionwarfare.warzone.WarzoneSystemBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/warzoneb\x06proto3', dependencies=[eve_dot_faction_dot_faction__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.factionwarfare.warzone.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.factionwarfare.warzone.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=134, serialized_end=166)
_PARTICIPANTS = _descriptor.Descriptor(name='Participants', full_name='eve.factionwarfare.warzone.Participants', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='factions', full_name='eve.factionwarfare.warzone.Participants.factions', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='pirate_faction', full_name='eve.factionwarfare.warzone.Participants.pirate_faction', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=168, serialized_end=274)
_FRONTLINE = _descriptor.Descriptor(name='Frontline', full_name='eve.factionwarfare.warzone.Frontline', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=276, serialized_end=287)
_SECONDLINE = _descriptor.Descriptor(name='Secondline', full_name='eve.factionwarfare.warzone.Secondline', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=289, serialized_end=301)
_BACKLINE = _descriptor.Descriptor(name='Backline', full_name='eve.factionwarfare.warzone.Backline', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=303, serialized_end=313)
_WARZONESYSTEM = _descriptor.Descriptor(name='WarzoneSystem', full_name='eve.factionwarfare.warzone.WarzoneSystem', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.factionwarfare.warzone.WarzoneSystem.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='occupier', full_name='eve.factionwarfare.warzone.WarzoneSystem.occupier', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='frontline', full_name='eve.factionwarfare.warzone.WarzoneSystem.frontline', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='secondline', full_name='eve.factionwarfare.warzone.WarzoneSystem.secondline', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='backline', full_name='eve.factionwarfare.warzone.WarzoneSystem.backline', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='adjacency_state', full_name='eve.factionwarfare.warzone.WarzoneSystem.adjacency_state', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=316, serialized_end=624)
_WARZONESYSTEMRESOLVED = _descriptor.Descriptor(name='WarzoneSystemResolved', full_name='eve.factionwarfare.warzone.WarzoneSystemResolved', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='system', full_name='eve.factionwarfare.warzone.WarzoneSystemResolved.system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='adjacent_systems', full_name='eve.factionwarfare.warzone.WarzoneSystemResolved.adjacent_systems', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=627, serialized_end=778)
_PARTICIPANTS.fields_by_name['factions'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_PARTICIPANTS.fields_by_name['pirate_faction'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_WARZONESYSTEM.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_WARZONESYSTEM.fields_by_name['occupier'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_WARZONESYSTEM.fields_by_name['frontline'].message_type = _FRONTLINE
_WARZONESYSTEM.fields_by_name['secondline'].message_type = _SECONDLINE
_WARZONESYSTEM.fields_by_name['backline'].message_type = _BACKLINE
_WARZONESYSTEM.oneofs_by_name['adjacency_state'].fields.append(_WARZONESYSTEM.fields_by_name['frontline'])
_WARZONESYSTEM.fields_by_name['frontline'].containing_oneof = _WARZONESYSTEM.oneofs_by_name['adjacency_state']
_WARZONESYSTEM.oneofs_by_name['adjacency_state'].fields.append(_WARZONESYSTEM.fields_by_name['secondline'])
_WARZONESYSTEM.fields_by_name['secondline'].containing_oneof = _WARZONESYSTEM.oneofs_by_name['adjacency_state']
_WARZONESYSTEM.oneofs_by_name['adjacency_state'].fields.append(_WARZONESYSTEM.fields_by_name['backline'])
_WARZONESYSTEM.fields_by_name['backline'].containing_oneof = _WARZONESYSTEM.oneofs_by_name['adjacency_state']
_WARZONESYSTEMRESOLVED.fields_by_name['system'].message_type = _WARZONESYSTEM
_WARZONESYSTEMRESOLVED.fields_by_name['adjacent_systems'].message_type = _WARZONESYSTEM
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Participants'] = _PARTICIPANTS
DESCRIPTOR.message_types_by_name['Frontline'] = _FRONTLINE
DESCRIPTOR.message_types_by_name['Secondline'] = _SECONDLINE
DESCRIPTOR.message_types_by_name['Backline'] = _BACKLINE
DESCRIPTOR.message_types_by_name['WarzoneSystem'] = _WARZONESYSTEM
DESCRIPTOR.message_types_by_name['WarzoneSystemResolved'] = _WARZONESYSTEMRESOLVED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(Identifier)
Participants = _reflection.GeneratedProtocolMessageType('Participants', (_message.Message,), {'DESCRIPTOR': _PARTICIPANTS,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(Participants)
Frontline = _reflection.GeneratedProtocolMessageType('Frontline', (_message.Message,), {'DESCRIPTOR': _FRONTLINE,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(Frontline)
Secondline = _reflection.GeneratedProtocolMessageType('Secondline', (_message.Message,), {'DESCRIPTOR': _SECONDLINE,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(Secondline)
Backline = _reflection.GeneratedProtocolMessageType('Backline', (_message.Message,), {'DESCRIPTOR': _BACKLINE,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(Backline)
WarzoneSystem = _reflection.GeneratedProtocolMessageType('WarzoneSystem', (_message.Message,), {'DESCRIPTOR': _WARZONESYSTEM,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(WarzoneSystem)
WarzoneSystemResolved = _reflection.GeneratedProtocolMessageType('WarzoneSystemResolved', (_message.Message,), {'DESCRIPTOR': _WARZONESYSTEMRESOLVED,
 '__module__': 'eve.factionwarfare.warzone.warzone_pb2'})
_sym_db.RegisterMessage(WarzoneSystemResolved)
DESCRIPTOR._options = None
