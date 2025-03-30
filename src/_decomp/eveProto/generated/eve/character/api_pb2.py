#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.corporation import role_pb2 as eve_dot_corporation_dot_role__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/api.proto', package='eve.character.api', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/character/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x17eve/character/api.proto\x12\x11eve.character.api\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x1aeve/corporation/role.proto\x1a\x13eve/ship/ship.proto\x1a!eve/solarsystem/solarsystem.proto"\xf1\x01\n\x07Onlined\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12"\n\x04ship\x18\x03 \x01(\x0b2\x14.eve.ship.Identifier\x120\n\x0bcorporation\x18\x04 \x01(\x0b2\x1b.eve.corporation.Identifier\x12/\n\x05roles\x18\x05 \x01(\x0b2 .eve.corporation.role.CollectionB>Z<github.com/ccpgames/eve-proto-go/generated/eve/character/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_role__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_ONLINED = _descriptor.Descriptor(name='Onlined', full_name='eve.character.api.Onlined', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.api.Onlined.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.character.api.Onlined.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.character.api.Onlined.ship', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.character.api.Onlined.corporation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='roles', full_name='eve.character.api.Onlined.roles', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=197, serialized_end=438)
_ONLINED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ONLINED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_ONLINED.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_ONLINED.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_ONLINED.fields_by_name['roles'].message_type = eve_dot_corporation_dot_role__pb2._COLLECTION
DESCRIPTOR.message_types_by_name['Onlined'] = _ONLINED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Onlined = _reflection.GeneratedProtocolMessageType('Onlined', (_message.Message,), {'DESCRIPTOR': _ONLINED,
 '__module__': 'eve.character.api_pb2'})
_sym_db.RegisterMessage(Onlined)
DESCRIPTOR._options = None
