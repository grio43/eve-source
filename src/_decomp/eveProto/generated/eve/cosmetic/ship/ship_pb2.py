#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\ship_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.cosmetic.ship.logo import logo_pb2 as eve_dot_cosmetic_dot_ship_dot_logo_dot_logo__pb2
from eveProto.generated.eve.cosmetic.ship.skin.firstparty import firstparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty import thirdparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/ship.proto', package='eve.cosmetic.ship', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/cosmetic/ship/ship.proto\x12\x11eve.cosmetic.ship\x1a\x1deve/character/character.proto\x1a!eve/cosmetic/ship/logo/logo.proto\x1a2eve/cosmetic/ship/skin/firstparty/firstparty.proto\x1a2eve/cosmetic/ship/skin/thirdparty/thirdparty.proto\x1a\x13eve/ship/ship.proto"\xbc\x03\n\tActivated\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.Identifier\x120\n\x05logos\x18\x03 \x03(\x0b2!.eve.cosmetic.ship.Activated.Logo\x12/\n\x04skin\x18\x04 \x01(\x0b2!.eve.cosmetic.ship.Activated.Skin\x1aL\n\x04Logo\x12\r\n\x05index\x18\x01 \x01(\x05\x125\n\tlogo_type\x18\x02 \x01(\x0b2".eve.cosmetic.ship.logo.Attributes\x1a\xab\x01\n\x04Skin\x12C\n\nfirstparty\x18\x01 \x01(\x0b2-.eve.cosmetic.ship.skin.firstparty.IdentifierH\x00\x12C\n\nthirdparty\x18\x02 \x01(\x0b2-.eve.cosmetic.ship.skin.thirdparty.IdentifierH\x00\x12\x11\n\x07no_skin\x18\x03 \x01(\x08H\x00B\x06\n\x04skinB>Z<github.com/ccpgames/eve-proto-go/generated/eve/cosmetic/shipb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_ship_dot_logo_dot_logo__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2.DESCRIPTOR,
 eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_ACTIVATED_LOGO = _descriptor.Descriptor(name='Logo', full_name='eve.cosmetic.ship.Activated.Logo', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='index', full_name='eve.cosmetic.ship.Activated.Logo.index', index=0, number=1, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='logo_type', full_name='eve.cosmetic.ship.Activated.Logo.logo_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=437, serialized_end=513)
_ACTIVATED_SKIN = _descriptor.Descriptor(name='Skin', full_name='eve.cosmetic.ship.Activated.Skin', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='firstparty', full_name='eve.cosmetic.ship.Activated.Skin.firstparty', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='thirdparty', full_name='eve.cosmetic.ship.Activated.Skin.thirdparty', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='no_skin', full_name='eve.cosmetic.ship.Activated.Skin.no_skin', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='skin', full_name='eve.cosmetic.ship.Activated.Skin.skin', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=516, serialized_end=687)
_ACTIVATED = _descriptor.Descriptor(name='Activated', full_name='eve.cosmetic.ship.Activated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.cosmetic.ship.Activated.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.cosmetic.ship.Activated.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='logos', full_name='eve.cosmetic.ship.Activated.logos', index=2, number=3, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skin', full_name='eve.cosmetic.ship.Activated.skin', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ACTIVATED_LOGO, _ACTIVATED_SKIN], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=243, serialized_end=687)
_ACTIVATED_LOGO.fields_by_name['logo_type'].message_type = eve_dot_cosmetic_dot_ship_dot_logo_dot_logo__pb2._ATTRIBUTES
_ACTIVATED_LOGO.containing_type = _ACTIVATED
_ACTIVATED_SKIN.fields_by_name['firstparty'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_firstparty_dot_firstparty__pb2._IDENTIFIER
_ACTIVATED_SKIN.fields_by_name['thirdparty'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2._IDENTIFIER
_ACTIVATED_SKIN.containing_type = _ACTIVATED
_ACTIVATED_SKIN.oneofs_by_name['skin'].fields.append(_ACTIVATED_SKIN.fields_by_name['firstparty'])
_ACTIVATED_SKIN.fields_by_name['firstparty'].containing_oneof = _ACTIVATED_SKIN.oneofs_by_name['skin']
_ACTIVATED_SKIN.oneofs_by_name['skin'].fields.append(_ACTIVATED_SKIN.fields_by_name['thirdparty'])
_ACTIVATED_SKIN.fields_by_name['thirdparty'].containing_oneof = _ACTIVATED_SKIN.oneofs_by_name['skin']
_ACTIVATED_SKIN.oneofs_by_name['skin'].fields.append(_ACTIVATED_SKIN.fields_by_name['no_skin'])
_ACTIVATED_SKIN.fields_by_name['no_skin'].containing_oneof = _ACTIVATED_SKIN.oneofs_by_name['skin']
_ACTIVATED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ACTIVATED.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_ACTIVATED.fields_by_name['logos'].message_type = _ACTIVATED_LOGO
_ACTIVATED.fields_by_name['skin'].message_type = _ACTIVATED_SKIN
DESCRIPTOR.message_types_by_name['Activated'] = _ACTIVATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Activated = _reflection.GeneratedProtocolMessageType('Activated', (_message.Message,), {'Logo': _reflection.GeneratedProtocolMessageType('Logo', (_message.Message,), {'DESCRIPTOR': _ACTIVATED_LOGO,
          '__module__': 'eve.cosmetic.ship.ship_pb2'}),
 'Skin': _reflection.GeneratedProtocolMessageType('Skin', (_message.Message,), {'DESCRIPTOR': _ACTIVATED_SKIN,
          '__module__': 'eve.cosmetic.ship.ship_pb2'}),
 'DESCRIPTOR': _ACTIVATED,
 '__module__': 'eve.cosmetic.ship.ship_pb2'})
_sym_db.RegisterMessage(Activated)
_sym_db.RegisterMessage(Activated.Logo)
_sym_db.RegisterMessage(Activated.Skin)
DESCRIPTOR._options = None
