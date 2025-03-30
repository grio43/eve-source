#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\market\admin\order_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.inventory import generic_item_type_pb2 as eve_dot_inventory_dot_generic__item__type__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.market.orders import buyorder_pb2 as eve_dot_market_dot_orders_dot_buyorder__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/market/admin/order.proto', package='eve.character.market.admin.order', syntax='proto3', serialized_options='ZKgithub.com/ccpgames/eve-proto-go/generated/eve/character/market/admin/order', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/character/market/admin/order.proto\x12 eve.character.market.admin.order\x1a\x1deve/character/character.proto\x1a%eve/inventory/generic_item_type.proto\x1a\x11eve/isk/isk.proto\x1a eve/market/orders/buyorder.proto\x1a\x19eve/station/station.proto"\xed\x01\n\x0fPlaceBuyRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12(\n\x07station\x18\x02 \x01(\x0b2\x17.eve.station.Identifier\x12<\n\titem_type\x18\x03 \x01(\x0b2).eve.inventory.genericitemtype.Identifier\x12 \n\x05price\x18\x04 \x01(\x0b2\x11.eve.isk.Currency\x12\x10\n\x08quantity\x18\x05 \x01(\r\x12\x10\n\x08duration\x18\x06 \x01(\r"M\n\x10PlaceBuyResponse\x129\n\tbuy_order\x18\x01 \x01(\x0b2&.eve.market.orders.buyorder.IdentifierBMZKgithub.com/ccpgames/eve-proto-go/generated/eve/character/market/admin/orderb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__type__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_market_dot_orders_dot_buyorder__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR])
_PLACEBUYREQUEST = _descriptor.Descriptor(name='PlaceBuyRequest', full_name='eve.character.market.admin.order.PlaceBuyRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.market.admin.order.PlaceBuyRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.character.market.admin.order.PlaceBuyRequest.station', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='item_type', full_name='eve.character.market.admin.order.PlaceBuyRequest.item_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='price', full_name='eve.character.market.admin.order.PlaceBuyRequest.price', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='quantity', full_name='eve.character.market.admin.order.PlaceBuyRequest.quantity', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='duration', full_name='eve.character.market.admin.order.PlaceBuyRequest.duration', index=5, number=6, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=227, serialized_end=464)
_PLACEBUYRESPONSE = _descriptor.Descriptor(name='PlaceBuyResponse', full_name='eve.character.market.admin.order.PlaceBuyResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='buy_order', full_name='eve.character.market.admin.order.PlaceBuyResponse.buy_order', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=466, serialized_end=543)
_PLACEBUYREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_PLACEBUYREQUEST.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_PLACEBUYREQUEST.fields_by_name['item_type'].message_type = eve_dot_inventory_dot_generic__item__type__pb2._IDENTIFIER
_PLACEBUYREQUEST.fields_by_name['price'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_PLACEBUYRESPONSE.fields_by_name['buy_order'].message_type = eve_dot_market_dot_orders_dot_buyorder__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['PlaceBuyRequest'] = _PLACEBUYREQUEST
DESCRIPTOR.message_types_by_name['PlaceBuyResponse'] = _PLACEBUYRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
PlaceBuyRequest = _reflection.GeneratedProtocolMessageType('PlaceBuyRequest', (_message.Message,), {'DESCRIPTOR': _PLACEBUYREQUEST,
 '__module__': 'eve.character.market.admin.order_pb2'})
_sym_db.RegisterMessage(PlaceBuyRequest)
PlaceBuyResponse = _reflection.GeneratedProtocolMessageType('PlaceBuyResponse', (_message.Message,), {'DESCRIPTOR': _PLACEBUYRESPONSE,
 '__module__': 'eve.character.market.admin.order_pb2'})
_sym_db.RegisterMessage(PlaceBuyResponse)
DESCRIPTOR._options = None
