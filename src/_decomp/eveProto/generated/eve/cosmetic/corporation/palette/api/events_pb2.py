#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\corporation\palette\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.cosmetic.corporation.palette import palette_pb2 as eve_dot_cosmetic_dot_corporation_dot_palette_dot_palette__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/corporation/palette/api/events.proto', package='eve.cosmetic.corporation.palette.api', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/corporation/palette/api', create_key=_descriptor._internal_create_key, serialized_pb='\n1eve/cosmetic/corporation/palette/api/events.proto\x12$eve.cosmetic.corporation.palette.api\x1a\x1deve/character/character.proto\x1a.eve/cosmetic/corporation/palette/palette.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xee\x01\n\x03Set\x12@\n\nidentifier\x18\x01 \x01(\x0b2,.eve.cosmetic.corporation.palette.Identifier\x12@\n\nattributes\x18\x02 \x01(\x0b2,.eve.cosmetic.corporation.palette.Attributes\x120\n\rlast_modifier\x18\x03 \x01(\x0b2\x19.eve.character.Identifier\x121\n\rlast_modified\x18\x04 \x01(\x0b2\x1a.google.protobuf.TimestampBQZOgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/corporation/palette/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_cosmetic_dot_corporation_dot_palette_dot_palette__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_SET = _descriptor.Descriptor(name='Set', full_name='eve.cosmetic.corporation.palette.api.Set', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.cosmetic.corporation.palette.api.Set.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.corporation.palette.api.Set.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_modifier', full_name='eve.cosmetic.corporation.palette.api.Set.last_modifier', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_modified', full_name='eve.cosmetic.corporation.palette.api.Set.last_modified', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=204, serialized_end=442)
_SET.fields_by_name['identifier'].message_type = eve_dot_cosmetic_dot_corporation_dot_palette_dot_palette__pb2._IDENTIFIER
_SET.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_corporation_dot_palette_dot_palette__pb2._ATTRIBUTES
_SET.fields_by_name['last_modifier'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_SET.fields_by_name['last_modified'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Set'] = _SET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Set = _reflection.GeneratedProtocolMessageType('Set', (_message.Message,), {'DESCRIPTOR': _SET,
 '__module__': 'eve.cosmetic.corporation.palette.api.events_pb2'})
_sym_db.RegisterMessage(Set)
DESCRIPTOR._options = None
