#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\blueprint_location_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/blueprint_location.proto', package='eve.industry.blueprintlocation', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve/industry/blueprintlocation', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/industry/blueprint_location.proto\x12\x1eeve.industry.blueprintlocation\x1a eve/inventory/generic_item.proto\x1a\x13eve/ship/ship.proto\x1a\x19eve/station/station.proto"\xc1\x01\n\nIdentifier\x12-\n\nstation_id\x18\x01 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12\'\n\x07ship_id\x18\x02 \x01(\x0b2\x14.eve.ship.IdentifierH\x00\x128\n\x07item_id\x18\x03 \x01(\x0b2%.eve.inventory.genericitem.IdentifierH\x00\x12\x15\n\rlocation_flag\x18\x04 \x01(\rB\n\n\x08locationBKZIgithub.com/ccpgames/eve-proto-go/generated/eve/industry/blueprintlocationb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__pb2.DESCRIPTOR, eve_dot_station_dot_station__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.industry.blueprintlocation.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='station_id', full_name='eve.industry.blueprintlocation.Identifier.station_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship_id', full_name='eve.industry.blueprintlocation.Identifier.ship_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='item_id', full_name='eve.industry.blueprintlocation.Identifier.item_id', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='location_flag', full_name='eve.industry.blueprintlocation.Identifier.location_flag', index=3, number=4, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='location', full_name='eve.industry.blueprintlocation.Identifier.location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=156, serialized_end=349)
_IDENTIFIER.fields_by_name['station_id'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['ship_id'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['item_id'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['location'].fields.append(_IDENTIFIER.fields_by_name['station_id'])
_IDENTIFIER.fields_by_name['station_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['location']
_IDENTIFIER.oneofs_by_name['location'].fields.append(_IDENTIFIER.fields_by_name['ship_id'])
_IDENTIFIER.fields_by_name['ship_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['location']
_IDENTIFIER.oneofs_by_name['location'].fields.append(_IDENTIFIER.fields_by_name['item_id'])
_IDENTIFIER.fields_by_name['item_id'].containing_oneof = _IDENTIFIER.oneofs_by_name['location']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.industry.blueprint_location_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
