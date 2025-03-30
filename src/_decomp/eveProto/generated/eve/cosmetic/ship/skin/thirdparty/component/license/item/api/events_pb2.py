#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\component\license\item\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.component.license.item import item_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_item_dot_item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/component/license/item/api/events.proto', package='eve.cosmetic.ship.skin.thirdparty.component.license.item.api', syntax='proto3', serialized_options='Zggithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/item/api', create_key=_descriptor._internal_create_key, serialized_pb='\nIeve/cosmetic/ship/skin/thirdparty/component/license/item/api/events.proto\x12<eve.cosmetic.ship.skin.thirdparty.component.license.item.api\x1aCeve/cosmetic/ship/skin/thirdparty/component/license/item/item.proto"^\n\x08Consumed\x12R\n\x04item\x18\x01 \x01(\x0b2D.eve.cosmetic.ship.skin.thirdparty.component.license.item.IdentifierBiZggithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/item/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_item_dot_item__pb2.DESCRIPTOR])
_CONSUMED = _descriptor.Descriptor(name='Consumed', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.item.api.Consumed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.item.api.Consumed.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=208, serialized_end=302)
_CONSUMED.fields_by_name['item'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_item_dot_item__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Consumed'] = _CONSUMED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Consumed = _reflection.GeneratedProtocolMessageType('Consumed', (_message.Message,), {'DESCRIPTOR': _CONSUMED,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.component.license.item.api.events_pb2'})
_sym_db.RegisterMessage(Consumed)
DESCRIPTOR._options = None
