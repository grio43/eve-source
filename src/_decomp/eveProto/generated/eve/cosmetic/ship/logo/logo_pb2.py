#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\logo\logo_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/logo/logo.proto', package='eve.cosmetic.ship.logo', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/logo', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/cosmetic/ship/logo/logo.proto\x12\x16eve.cosmetic.ship.logo\x1a\x1deve/character/character.proto\x1a\x13eve/ship/ship.proto"m\n\nIdentifier\x12"\n\x04ship\x18\x01 \x01(\x0b2\x14.eve.ship.Identifier\x12\r\n\x05index\x18\x02 \x01(\x05\x12,\n\tcharacter\x18\x03 \x01(\x0b2\x19.eve.character.Identifier"\x8b\x01\n\nAttributes\x124\n\x08alliance\x18\x01 \x01(\x0b2 .eve.cosmetic.ship.logo.AllianceH\x00\x12:\n\x0bcorporation\x18\x02 \x01(\x0b2#.eve.cosmetic.ship.logo.CorporationH\x00B\x0b\n\tlogo_type"\n\n\x08Alliance"\r\n\x0bCorporation"9\n\x07Cleared\x12.\n\x02id\x18\x01 \x01(\x0b2".eve.cosmetic.ship.logo.Identifier"s\n\tDisplayed\x12.\n\x02id\x18\x01 \x01(\x0b2".eve.cosmetic.ship.logo.Identifier\x126\n\nattributes\x18\x02 \x01(\x0b2".eve.cosmetic.ship.logo.AttributesBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/logob\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.ship.logo.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship', full_name='eve.cosmetic.ship.logo.Identifier.ship', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='index', full_name='eve.cosmetic.ship.logo.Identifier.index', index=1, number=2, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.cosmetic.ship.logo.Identifier.character', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=113, serialized_end=222)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.ship.logo.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.cosmetic.ship.logo.Attributes.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.cosmetic.ship.logo.Attributes.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='logo_type', full_name='eve.cosmetic.ship.logo.Attributes.logo_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=225, serialized_end=364)
_ALLIANCE = _descriptor.Descriptor(name='Alliance', full_name='eve.cosmetic.ship.logo.Alliance', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=366, serialized_end=376)
_CORPORATION = _descriptor.Descriptor(name='Corporation', full_name='eve.cosmetic.ship.logo.Corporation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=378, serialized_end=391)
_CLEARED = _descriptor.Descriptor(name='Cleared', full_name='eve.cosmetic.ship.logo.Cleared', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.cosmetic.ship.logo.Cleared.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=393, serialized_end=450)
_DISPLAYED = _descriptor.Descriptor(name='Displayed', full_name='eve.cosmetic.ship.logo.Displayed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.cosmetic.ship.logo.Displayed.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.ship.logo.Displayed.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=452, serialized_end=567)
_IDENTIFIER.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['alliance'].message_type = _ALLIANCE
_ATTRIBUTES.fields_by_name['corporation'].message_type = _CORPORATION
_ATTRIBUTES.oneofs_by_name['logo_type'].fields.append(_ATTRIBUTES.fields_by_name['alliance'])
_ATTRIBUTES.fields_by_name['alliance'].containing_oneof = _ATTRIBUTES.oneofs_by_name['logo_type']
_ATTRIBUTES.oneofs_by_name['logo_type'].fields.append(_ATTRIBUTES.fields_by_name['corporation'])
_ATTRIBUTES.fields_by_name['corporation'].containing_oneof = _ATTRIBUTES.oneofs_by_name['logo_type']
_CLEARED.fields_by_name['id'].message_type = _IDENTIFIER
_DISPLAYED.fields_by_name['id'].message_type = _IDENTIFIER
_DISPLAYED.fields_by_name['attributes'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Alliance'] = _ALLIANCE
DESCRIPTOR.message_types_by_name['Corporation'] = _CORPORATION
DESCRIPTOR.message_types_by_name['Cleared'] = _CLEARED
DESCRIPTOR.message_types_by_name['Displayed'] = _DISPLAYED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Attributes)
Alliance = _reflection.GeneratedProtocolMessageType('Alliance', (_message.Message,), {'DESCRIPTOR': _ALLIANCE,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Alliance)
Corporation = _reflection.GeneratedProtocolMessageType('Corporation', (_message.Message,), {'DESCRIPTOR': _CORPORATION,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Corporation)
Cleared = _reflection.GeneratedProtocolMessageType('Cleared', (_message.Message,), {'DESCRIPTOR': _CLEARED,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Cleared)
Displayed = _reflection.GeneratedProtocolMessageType('Displayed', (_message.Message,), {'DESCRIPTOR': _DISPLAYED,
 '__module__': 'eve.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Displayed)
DESCRIPTOR._options = None
