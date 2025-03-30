#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\hacking\container_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.hacking import hacking_pb2 as eve_dot_character_dot_hacking_dot_hacking__pb2
from eveProto.generated.eve.container import type_pb2 as eve_dot_container_dot_type__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/hacking/container.proto', package='eve.character.hacking.container', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/character/hacking/container', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/character/hacking/container.proto\x12\x1feve.character.hacking.container\x1a\x1deve/character/character.proto\x1a#eve/character/hacking/hacking.proto\x1a\x18eve/container/type.proto\x1a!eve/solarsystem/solarsystem.proto"\xd3\x01\n\tSucceeded\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12,\n\tcontainer\x18\x03 \x01(\x0b2\x19.eve.container.Identifier\x127\n\x0eanalyzer_group\x18\x04 \x01(\x0b2\x1f.eve.character.hacking.AnalyzerBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/character/hacking/containerb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_character_dot_hacking_dot_hacking__pb2.DESCRIPTOR,
 eve_dot_container_dot_type__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_SUCCEEDED = _descriptor.Descriptor(name='Succeeded', full_name='eve.character.hacking.container.Succeeded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.hacking.container.Succeeded.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.character.hacking.container.Succeeded.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='container', full_name='eve.character.hacking.container.Succeeded.container', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='analyzer_group', full_name='eve.character.hacking.container.Succeeded.analyzer_group', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=204, serialized_end=415)
_SUCCEEDED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SUCCEEDED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_SUCCEEDED.fields_by_name['container'].message_type = eve_dot_container_dot_type__pb2._IDENTIFIER
_SUCCEEDED.fields_by_name['analyzer_group'].message_type = eve_dot_character_dot_hacking_dot_hacking__pb2._ANALYZER
DESCRIPTOR.message_types_by_name['Succeeded'] = _SUCCEEDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Succeeded = _reflection.GeneratedProtocolMessageType('Succeeded', (_message.Message,), {'DESCRIPTOR': _SUCCEEDED,
 '__module__': 'eve.character.hacking.container_pb2'})
_sym_db.RegisterMessage(Succeeded)
DESCRIPTOR._options = None
