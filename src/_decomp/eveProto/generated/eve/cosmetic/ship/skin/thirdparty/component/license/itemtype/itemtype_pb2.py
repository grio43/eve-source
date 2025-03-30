#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\component\license\itemtype\itemtype_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.component.license import license_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_license__pb2
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/component/license/itemtype/itemtype.proto', package='eve.cosmetic.ship.skin.thirdparty.component.license.itemtype', syntax='proto3', serialized_options='Zggithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/itemtype', create_key=_descriptor._internal_create_key, serialized_pb='\nKeve/cosmetic/ship/skin/thirdparty/component/license/itemtype/itemtype.proto\x12<eve.cosmetic.ship.skin.thirdparty.component.license.itemtype\x1aAeve/cosmetic/ship/skin/thirdparty/component/license/license.proto\x1a%eve/inventory/generic_item_type.proto"E\n\nIdentifier\x127\n\x04item\x18\x01 \x01(\x0b2).eve.inventory.genericitemtype.Identifier"X\n\nAttributes\x12J\n\x07license\x18\x01 \x01(\x0b29.eve.cosmetic.ship.skin.thirdparty.component.license.KindBiZggithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/itemtypeb\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_license__pb2.DESCRIPTOR, eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.Identifier.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=247, serialized_end=316)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.Attributes.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=318, serialized_end=406)
_IDENTIFIER.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['license'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_license__pb2._KIND
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.itemtype_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.component.license.itemtype.itemtype_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
