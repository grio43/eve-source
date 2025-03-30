#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\industry\reprocess\ore_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ore import ore_pb2 as eve_dot_ore_dot_ore__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/industry/reprocess/ore.proto', package='eve.character.industry.reprocess.ore', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve/character/industry/reprocess/ore', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve/character/industry/reprocess/ore.proto\x12$eve.character.industry.reprocess.ore\x1a\x1deve/character/character.proto\x1a\x11eve/ore/ore.proto"o\n\x0bReprocessed\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12 \n\x03ore\x18\x02 \x01(\x0b2\x13.eve.ore.Identifier\x12\x10\n\x08quantity\x18\x03 \x01(\rBQZOgithub.com/ccpgames/eve-proto-go/generated/eve/character/industry/reprocess/oreb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ore_dot_ore__pb2.DESCRIPTOR])
_REPROCESSED = _descriptor.Descriptor(name='Reprocessed', full_name='eve.character.industry.reprocess.ore.Reprocessed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.industry.reprocess.ore.Reprocessed.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ore', full_name='eve.character.industry.reprocess.ore.Reprocessed.ore', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.character.industry.reprocess.ore.Reprocessed.quantity', index=2, number=3, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=134, serialized_end=245)
_REPROCESSED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REPROCESSED.fields_by_name['ore'].message_type = eve_dot_ore_dot_ore__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Reprocessed'] = _REPROCESSED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Reprocessed = _reflection.GeneratedProtocolMessageType('Reprocessed', (_message.Message,), {'DESCRIPTOR': _REPROCESSED,
 '__module__': 'eve.character.industry.reprocess.ore_pb2'})
_sym_db.RegisterMessage(Reprocessed)
DESCRIPTOR._options = None
