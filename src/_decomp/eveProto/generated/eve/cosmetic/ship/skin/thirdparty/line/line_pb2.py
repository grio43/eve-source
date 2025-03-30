#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\line\line_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/line/line.proto', package='eve.cosmetic.ship.skin.thirdparty.line', syntax='proto3', serialized_options='ZQgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/line', create_key=_descriptor._internal_create_key, serialized_pb='\n1eve/cosmetic/ship/skin/thirdparty/line/line.proto\x12&eve.cosmetic.ship.skin.thirdparty.line\x1a\x1deve/character/character.proto"\x19\n\nIdentifier\x12\x0b\n\x03hex\x18\x01 \x01(\t"F\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12*\n\x07creator\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierBSZQgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/lineb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.ship.skin.thirdparty.line.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='hex', full_name='eve.cosmetic.ship.skin.thirdparty.line.Identifier.hex', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=124, serialized_end=149)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.ship.skin.thirdparty.line.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.cosmetic.ship.skin.thirdparty.line.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='creator', full_name='eve.cosmetic.ship.skin.thirdparty.line.Attributes.creator', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=151, serialized_end=221)
_ATTRIBUTES.fields_by_name['creator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.line.line_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.line.line_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
