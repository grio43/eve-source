#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\factionwarfare\systems_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.faction import faction_pb2 as eve_dot_faction_dot_faction__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/factionwarfare/systems.proto', package='eve.factionwarfare.systems', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/systems', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/factionwarfare/systems.proto\x12\x1aeve.factionwarfare.systems\x1a\x19eve/faction/faction.proto\x1a!eve/solarsystem/solarsystem.proto"\xb2\x02\n\x11SolarSystemStatus\x123\n\x0esolarsystem_id\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x121\n\x10owner_faction_id\x18\x02 \x01(\x0b2\x17.eve.faction.Identifier\x124\n\x13occupier_faction_id\x18\x03 \x01(\x0b2\x17.eve.faction.Identifier\x12E\n\x10contested_status\x18\x04 \x01(\x0e2+.eve.factionwarfare.systems.ContestedStatus\x12\x16\n\x0evictory_points\x18\x05 \x01(\x04\x12 \n\x18victory_points_threshold\x18\x06 \x01(\x04"\x0c\n\nGetRequest"R\n\x0bGetResponse\x12C\n\x0csolarsystems\x18\x01 \x03(\x0b2-.eve.factionwarfare.systems.SolarSystemStatus*S\n\x0fContestedStatus\x12\x0f\n\x0bUNCONTESTED\x10\x00\x12\r\n\tCONTESTED\x10\x01\x12\x0e\n\nVULNERABLE\x10\x02\x12\x10\n\x08CAPTURED\x10\x03\x1a\x02\x08\x01BGZEgithub.com/ccpgames/eve-proto-go/generated/eve/factionwarfare/systemsb\x06proto3', dependencies=[eve_dot_faction_dot_faction__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_CONTESTEDSTATUS = _descriptor.EnumDescriptor(name='ContestedStatus', full_name='eve.factionwarfare.systems.ContestedStatus', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='UNCONTESTED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CONTESTED', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='VULNERABLE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CAPTURED', index=3, number=3, serialized_options='\x08\x01', type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=533, serialized_end=616)
_sym_db.RegisterEnumDescriptor(_CONTESTEDSTATUS)
ContestedStatus = enum_type_wrapper.EnumTypeWrapper(_CONTESTEDSTATUS)
UNCONTESTED = 0
CONTESTED = 1
VULNERABLE = 2
CAPTURED = 3
_SOLARSYSTEMSTATUS = _descriptor.Descriptor(name='SolarSystemStatus', full_name='eve.factionwarfare.systems.SolarSystemStatus', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystem_id', full_name='eve.factionwarfare.systems.SolarSystemStatus.solarsystem_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_faction_id', full_name='eve.factionwarfare.systems.SolarSystemStatus.owner_faction_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='occupier_faction_id', full_name='eve.factionwarfare.systems.SolarSystemStatus.occupier_faction_id', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='contested_status', full_name='eve.factionwarfare.systems.SolarSystemStatus.contested_status', index=3, number=4, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='victory_points', full_name='eve.factionwarfare.systems.SolarSystemStatus.victory_points', index=4, number=5, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='victory_points_threshold', full_name='eve.factionwarfare.systems.SolarSystemStatus.victory_points_threshold', index=5, number=6, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=127, serialized_end=433)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.factionwarfare.systems.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=435, serialized_end=447)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.factionwarfare.systems.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solarsystems', full_name='eve.factionwarfare.systems.GetResponse.solarsystems', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=449, serialized_end=531)
_SOLARSYSTEMSTATUS.fields_by_name['solarsystem_id'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_SOLARSYSTEMSTATUS.fields_by_name['owner_faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_SOLARSYSTEMSTATUS.fields_by_name['occupier_faction_id'].message_type = eve_dot_faction_dot_faction__pb2._IDENTIFIER
_SOLARSYSTEMSTATUS.fields_by_name['contested_status'].enum_type = _CONTESTEDSTATUS
_GETRESPONSE.fields_by_name['solarsystems'].message_type = _SOLARSYSTEMSTATUS
DESCRIPTOR.message_types_by_name['SolarSystemStatus'] = _SOLARSYSTEMSTATUS
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.enum_types_by_name['ContestedStatus'] = _CONTESTEDSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SolarSystemStatus = _reflection.GeneratedProtocolMessageType('SolarSystemStatus', (_message.Message,), {'DESCRIPTOR': _SOLARSYSTEMSTATUS,
 '__module__': 'eve.factionwarfare.systems_pb2'})
_sym_db.RegisterMessage(SolarSystemStatus)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.factionwarfare.systems_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.factionwarfare.systems_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
_CONTESTEDSTATUS.values_by_name['CAPTURED']._options = None
