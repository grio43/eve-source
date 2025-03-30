#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\sovereignty\mercenaryden\mercenaryden_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.character import character_pb2 as eve__public_dot_character_dot_character__pb2
from eveProto.generated.eve_public.planet import planet_pb2 as eve__public_dot_planet_dot_planet__pb2
from eveProto.generated.eve_public.planet.skyhook import skyhook_pb2 as eve__public_dot_planet_dot_skyhook_dot_skyhook__pb2
from eveProto.generated.eve_public.solarsystem import solarsystem_pb2 as eve__public_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve_public.sovereignty.mercenaryden import mercenaryden_type_pb2 as eve__public_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/sovereignty/mercenaryden/mercenaryden.proto', package='eve_public.sovereignty.mercenaryden', syntax='proto3', serialized_options='ZNgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/mercenaryden', create_key=_descriptor._internal_create_key, serialized_pb='\n6eve_public/sovereignty/mercenaryden/mercenaryden.proto\x12#eve_public.sovereignty.mercenaryden\x1a$eve_public/character/character.proto\x1a\x1eeve_public/planet/planet.proto\x1a\'eve_public/planet/skyhook/skyhook.proto\x1a(eve_public/solarsystem/solarsystem.proto\x1a;eve_public/sovereignty/mercenaryden/mercenaryden_type.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"\xa1\x02\n\nAttributes\x12/\n\x05owner\x18\x01 \x01(\x0b2 .eve_public.character.Identifier\x126\n\x07skyhook\x18\x02 \x01(\x0b2%.eve_public.planet.skyhook.Identifier\x128\n\x0csolar_system\x18\x03 \x01(\x0b2".eve_public.solarsystem.Identifier\x12-\n\x06planet\x18\x04 \x01(\x0b2\x1d.eve_public.planet.Identifier\x12A\n\x04type\x18\x05 \x01(\x0b23.eve_public.sovereignty.mercenarydentype.IdentifierBPZNgithub.com/ccpgames/eve-proto-go/generated/eve_public/sovereignty/mercenarydenb\x06proto3', dependencies=[eve__public_dot_character_dot_character__pb2.DESCRIPTOR,
 eve__public_dot_planet_dot_planet__pb2.DESCRIPTOR,
 eve__public_dot_planet_dot_skyhook_dot_skyhook__pb2.DESCRIPTOR,
 eve__public_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve__public_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.sovereignty.mercenaryden.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve_public.sovereignty.mercenaryden.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=309, serialized_end=341)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve_public.sovereignty.mercenaryden.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='owner', full_name='eve_public.sovereignty.mercenaryden.Attributes.owner', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skyhook', full_name='eve_public.sovereignty.mercenaryden.Attributes.skyhook', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve_public.sovereignty.mercenaryden.Attributes.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='planet', full_name='eve_public.sovereignty.mercenaryden.Attributes.planet', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='type', full_name='eve_public.sovereignty.mercenaryden.Attributes.type', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=344, serialized_end=633)
_ATTRIBUTES.fields_by_name['owner'].message_type = eve__public_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['skyhook'].message_type = eve__public_dot_planet_dot_skyhook_dot_skyhook__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['solar_system'].message_type = eve__public_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['planet'].message_type = eve__public_dot_planet_dot_planet__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['type'].message_type = eve__public_dot_sovereignty_dot_mercenaryden_dot_mercenaryden__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.sovereignty.mercenaryden.mercenaryden_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve_public.sovereignty.mercenaryden.mercenaryden_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
