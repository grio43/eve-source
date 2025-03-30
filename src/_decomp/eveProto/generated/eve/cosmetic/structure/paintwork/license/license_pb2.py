#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\structure\paintwork\license\license_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/structure/paintwork/license/license.proto', package='eve.cosmetic.structure.paintwork.license', syntax='proto3', serialized_options='ZSgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/license', create_key=_descriptor._internal_create_key, serialized_pb='\n6eve/cosmetic/structure/paintwork/license/license.proto\x12(eve.cosmetic.structure.paintwork.license\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x1deve/structure/structure.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\xf3\x01\n\nAttributes\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x12,\n\tactivator\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12*\n\x06issued\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12+\n\x08duration\x18\x04 \x01(\x0b2\x19.google.protobuf.Duration\x12,\n\tstructure\x18\x05 \x01(\x0b2\x19.eve.structure.IdentifierBUZSgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/licenseb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.structure.paintwork.license.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.cosmetic.structure.paintwork.license.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=262, serialized_end=288)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.structure.paintwork.license.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.cosmetic.structure.paintwork.license.Attributes.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='activator', full_name='eve.cosmetic.structure.paintwork.license.Attributes.activator', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issued', full_name='eve.cosmetic.structure.paintwork.license.Attributes.issued', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='duration', full_name='eve.cosmetic.structure.paintwork.license.Attributes.duration', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.cosmetic.structure.paintwork.license.Attributes.structure', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=291, serialized_end=534)
_ATTRIBUTES.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['activator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['issued'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_ATTRIBUTES.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.structure.paintwork.license.license_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.structure.paintwork.license.license_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
