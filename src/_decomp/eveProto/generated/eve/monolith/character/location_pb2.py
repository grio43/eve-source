#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\monolith\character\location_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/monolith/character/location.proto', package='eve.monolith.character.location', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/monolith/character/location', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/monolith/character/location.proto\x12\x1feve.monolith.character.location\x1a\x1deve/character/character.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto":\n\nGetRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"\xbb\x01\n\x0bGetResponse\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12\x12\n\x08in_space\x18\x02 \x01(\x08H\x00\x12*\n\x07station\x18\x03 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\x04 \x01(\x0b2\x19.eve.structure.IdentifierH\x00B\t\n\x07detailsBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/monolith/character/locationb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.monolith.character.location.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.monolith.character.location.GetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=198, serialized_end=256)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.monolith.character.location.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.monolith.character.location.GetResponse.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='in_space', full_name='eve.monolith.character.location.GetResponse.in_space', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.monolith.character.location.GetResponse.station', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.monolith.character.location.GetResponse.structure', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='details', full_name='eve.monolith.character.location.GetResponse.details', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=259, serialized_end=446)
_GETREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_GETRESPONSE.oneofs_by_name['details'].fields.append(_GETRESPONSE.fields_by_name['in_space'])
_GETRESPONSE.fields_by_name['in_space'].containing_oneof = _GETRESPONSE.oneofs_by_name['details']
_GETRESPONSE.oneofs_by_name['details'].fields.append(_GETRESPONSE.fields_by_name['station'])
_GETRESPONSE.fields_by_name['station'].containing_oneof = _GETRESPONSE.oneofs_by_name['details']
_GETRESPONSE.oneofs_by_name['details'].fields.append(_GETRESPONSE.fields_by_name['structure'])
_GETRESPONSE.fields_by_name['structure'].containing_oneof = _GETRESPONSE.oneofs_by_name['details']
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.monolith.character.location_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.monolith.character.location_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
