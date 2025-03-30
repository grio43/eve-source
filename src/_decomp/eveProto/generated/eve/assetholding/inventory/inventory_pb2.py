#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\assetholding\inventory\inventory_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/assetholding/inventory/inventory.proto', package='eve.assetholding.inventory', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/inventory', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve/assetholding/inventory/inventory.proto\x12\x1aeve.assetholding.inventory\x1a eve/inventory/generic_item.proto"\xcc\x02\n\x0eSourceLocation\x123\n\x04item\x18\x01 \x01(\x0b2#.eve.inventory.genericitem.LocationH\x00\x12a\n\x16owner_current_location\x18\x02 \x01(\x0b2?.eve.assetholding.inventory.SourceLocation.OwnerCurrentLocationH\x00\x12Y\n\x12owner_home_station\x18\x03 \x01(\x0b2;.eve.assetholding.inventory.SourceLocation.OwnerHomeStationH\x00\x12\r\n\x03any\x18\x04 \x01(\x08H\x00\x1a\x16\n\x14OwnerCurrentLocation\x1a\x12\n\x10OwnerHomeStationB\x0c\n\ndefinition"\xe4\x03\n\x1aAllowedDestinationLocation\x123\n\x04item\x18\x01 \x01(\x0b2#.eve.inventory.genericitem.LocationH\x00\x12`\n\x0fsource_location\x18\x02 \x01(\x0b2E.eve.assetholding.inventory.AllowedDestinationLocation.SourceLocationH\x00\x12m\n\x16owner_current_location\x18\x03 \x01(\x0b2K.eve.assetholding.inventory.AllowedDestinationLocation.OwnerCurrentLocationH\x00\x12e\n\x12owner_home_station\x18\x04 \x01(\x0b2G.eve.assetholding.inventory.AllowedDestinationLocation.OwnerHomeStationH\x00\x12\r\n\x03any\x18\x05 \x01(\x08H\x00\x1a\x10\n\x0eSourceLocation\x1a\x16\n\x14OwnerCurrentLocation\x1a\x12\n\x10OwnerHomeStationB\x0c\n\ndefinition"\xa5\x03\n\x0eRedeemLocation\x123\n\x04item\x18\x01 \x01(\x0b2#.eve.inventory.genericitem.LocationH\x00\x12T\n\x0fsource_location\x18\x02 \x01(\x0b29.eve.assetholding.inventory.RedeemLocation.SourceLocationH\x00\x12a\n\x16owner_current_location\x18\x03 \x01(\x0b2?.eve.assetholding.inventory.RedeemLocation.OwnerCurrentLocationH\x00\x12Y\n\x12owner_home_station\x18\x04 \x01(\x0b2;.eve.assetholding.inventory.RedeemLocation.OwnerHomeStationH\x00\x1a\x10\n\x0eSourceLocation\x1a\x16\n\x14OwnerCurrentLocation\x1a\x12\n\x10OwnerHomeStationB\x0c\n\ndefinitionBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/inventoryb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR])
_SOURCELOCATION_OWNERCURRENTLOCATION = _descriptor.Descriptor(name='OwnerCurrentLocation', full_name='eve.assetholding.inventory.SourceLocation.OwnerCurrentLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=385, serialized_end=407)
_SOURCELOCATION_OWNERHOMESTATION = _descriptor.Descriptor(name='OwnerHomeStation', full_name='eve.assetholding.inventory.SourceLocation.OwnerHomeStation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=409, serialized_end=427)
_SOURCELOCATION = _descriptor.Descriptor(name='SourceLocation', full_name='eve.assetholding.inventory.SourceLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.assetholding.inventory.SourceLocation.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_current_location', full_name='eve.assetholding.inventory.SourceLocation.owner_current_location', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_home_station', full_name='eve.assetholding.inventory.SourceLocation.owner_home_station', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='any', full_name='eve.assetholding.inventory.SourceLocation.any', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_SOURCELOCATION_OWNERCURRENTLOCATION, _SOURCELOCATION_OWNERHOMESTATION], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='definition', full_name='eve.assetholding.inventory.SourceLocation.definition', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=109, serialized_end=441)
_ALLOWEDDESTINATIONLOCATION_SOURCELOCATION = _descriptor.Descriptor(name='SourceLocation', full_name='eve.assetholding.inventory.AllowedDestinationLocation.SourceLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=109, serialized_end=125)
_ALLOWEDDESTINATIONLOCATION_OWNERCURRENTLOCATION = _descriptor.Descriptor(name='OwnerCurrentLocation', full_name='eve.assetholding.inventory.AllowedDestinationLocation.OwnerCurrentLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=385, serialized_end=407)
_ALLOWEDDESTINATIONLOCATION_OWNERHOMESTATION = _descriptor.Descriptor(name='OwnerHomeStation', full_name='eve.assetholding.inventory.AllowedDestinationLocation.OwnerHomeStation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=409, serialized_end=427)
_ALLOWEDDESTINATIONLOCATION = _descriptor.Descriptor(name='AllowedDestinationLocation', full_name='eve.assetholding.inventory.AllowedDestinationLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.assetholding.inventory.AllowedDestinationLocation.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='source_location', full_name='eve.assetholding.inventory.AllowedDestinationLocation.source_location', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_current_location', full_name='eve.assetholding.inventory.AllowedDestinationLocation.owner_current_location', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_home_station', full_name='eve.assetholding.inventory.AllowedDestinationLocation.owner_home_station', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='any', full_name='eve.assetholding.inventory.AllowedDestinationLocation.any', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_ALLOWEDDESTINATIONLOCATION_SOURCELOCATION, _ALLOWEDDESTINATIONLOCATION_OWNERCURRENTLOCATION, _ALLOWEDDESTINATIONLOCATION_OWNERHOMESTATION], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='definition', full_name='eve.assetholding.inventory.AllowedDestinationLocation.definition', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=444, serialized_end=928)
_REDEEMLOCATION_SOURCELOCATION = _descriptor.Descriptor(name='SourceLocation', full_name='eve.assetholding.inventory.RedeemLocation.SourceLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=109, serialized_end=125)
_REDEEMLOCATION_OWNERCURRENTLOCATION = _descriptor.Descriptor(name='OwnerCurrentLocation', full_name='eve.assetholding.inventory.RedeemLocation.OwnerCurrentLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=385, serialized_end=407)
_REDEEMLOCATION_OWNERHOMESTATION = _descriptor.Descriptor(name='OwnerHomeStation', full_name='eve.assetholding.inventory.RedeemLocation.OwnerHomeStation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=409, serialized_end=427)
_REDEEMLOCATION = _descriptor.Descriptor(name='RedeemLocation', full_name='eve.assetholding.inventory.RedeemLocation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item', full_name='eve.assetholding.inventory.RedeemLocation.item', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='source_location', full_name='eve.assetholding.inventory.RedeemLocation.source_location', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_current_location', full_name='eve.assetholding.inventory.RedeemLocation.owner_current_location', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='owner_home_station', full_name='eve.assetholding.inventory.RedeemLocation.owner_home_station', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_REDEEMLOCATION_SOURCELOCATION, _REDEEMLOCATION_OWNERCURRENTLOCATION, _REDEEMLOCATION_OWNERHOMESTATION], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='definition', full_name='eve.assetholding.inventory.RedeemLocation.definition', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=931, serialized_end=1352)
_SOURCELOCATION_OWNERCURRENTLOCATION.containing_type = _SOURCELOCATION
_SOURCELOCATION_OWNERHOMESTATION.containing_type = _SOURCELOCATION
_SOURCELOCATION.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._LOCATION
_SOURCELOCATION.fields_by_name['owner_current_location'].message_type = _SOURCELOCATION_OWNERCURRENTLOCATION
_SOURCELOCATION.fields_by_name['owner_home_station'].message_type = _SOURCELOCATION_OWNERHOMESTATION
_SOURCELOCATION.oneofs_by_name['definition'].fields.append(_SOURCELOCATION.fields_by_name['item'])
_SOURCELOCATION.fields_by_name['item'].containing_oneof = _SOURCELOCATION.oneofs_by_name['definition']
_SOURCELOCATION.oneofs_by_name['definition'].fields.append(_SOURCELOCATION.fields_by_name['owner_current_location'])
_SOURCELOCATION.fields_by_name['owner_current_location'].containing_oneof = _SOURCELOCATION.oneofs_by_name['definition']
_SOURCELOCATION.oneofs_by_name['definition'].fields.append(_SOURCELOCATION.fields_by_name['owner_home_station'])
_SOURCELOCATION.fields_by_name['owner_home_station'].containing_oneof = _SOURCELOCATION.oneofs_by_name['definition']
_SOURCELOCATION.oneofs_by_name['definition'].fields.append(_SOURCELOCATION.fields_by_name['any'])
_SOURCELOCATION.fields_by_name['any'].containing_oneof = _SOURCELOCATION.oneofs_by_name['definition']
_ALLOWEDDESTINATIONLOCATION_SOURCELOCATION.containing_type = _ALLOWEDDESTINATIONLOCATION
_ALLOWEDDESTINATIONLOCATION_OWNERCURRENTLOCATION.containing_type = _ALLOWEDDESTINATIONLOCATION
_ALLOWEDDESTINATIONLOCATION_OWNERHOMESTATION.containing_type = _ALLOWEDDESTINATIONLOCATION
_ALLOWEDDESTINATIONLOCATION.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._LOCATION
_ALLOWEDDESTINATIONLOCATION.fields_by_name['source_location'].message_type = _ALLOWEDDESTINATIONLOCATION_SOURCELOCATION
_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_current_location'].message_type = _ALLOWEDDESTINATIONLOCATION_OWNERCURRENTLOCATION
_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_home_station'].message_type = _ALLOWEDDESTINATIONLOCATION_OWNERHOMESTATION
_ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition'].fields.append(_ALLOWEDDESTINATIONLOCATION.fields_by_name['item'])
_ALLOWEDDESTINATIONLOCATION.fields_by_name['item'].containing_oneof = _ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition']
_ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition'].fields.append(_ALLOWEDDESTINATIONLOCATION.fields_by_name['source_location'])
_ALLOWEDDESTINATIONLOCATION.fields_by_name['source_location'].containing_oneof = _ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition']
_ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition'].fields.append(_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_current_location'])
_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_current_location'].containing_oneof = _ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition']
_ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition'].fields.append(_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_home_station'])
_ALLOWEDDESTINATIONLOCATION.fields_by_name['owner_home_station'].containing_oneof = _ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition']
_ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition'].fields.append(_ALLOWEDDESTINATIONLOCATION.fields_by_name['any'])
_ALLOWEDDESTINATIONLOCATION.fields_by_name['any'].containing_oneof = _ALLOWEDDESTINATIONLOCATION.oneofs_by_name['definition']
_REDEEMLOCATION_SOURCELOCATION.containing_type = _REDEEMLOCATION
_REDEEMLOCATION_OWNERCURRENTLOCATION.containing_type = _REDEEMLOCATION
_REDEEMLOCATION_OWNERHOMESTATION.containing_type = _REDEEMLOCATION
_REDEEMLOCATION.fields_by_name['item'].message_type = eve_dot_inventory_dot_generic__item__pb2._LOCATION
_REDEEMLOCATION.fields_by_name['source_location'].message_type = _REDEEMLOCATION_SOURCELOCATION
_REDEEMLOCATION.fields_by_name['owner_current_location'].message_type = _REDEEMLOCATION_OWNERCURRENTLOCATION
_REDEEMLOCATION.fields_by_name['owner_home_station'].message_type = _REDEEMLOCATION_OWNERHOMESTATION
_REDEEMLOCATION.oneofs_by_name['definition'].fields.append(_REDEEMLOCATION.fields_by_name['item'])
_REDEEMLOCATION.fields_by_name['item'].containing_oneof = _REDEEMLOCATION.oneofs_by_name['definition']
_REDEEMLOCATION.oneofs_by_name['definition'].fields.append(_REDEEMLOCATION.fields_by_name['source_location'])
_REDEEMLOCATION.fields_by_name['source_location'].containing_oneof = _REDEEMLOCATION.oneofs_by_name['definition']
_REDEEMLOCATION.oneofs_by_name['definition'].fields.append(_REDEEMLOCATION.fields_by_name['owner_current_location'])
_REDEEMLOCATION.fields_by_name['owner_current_location'].containing_oneof = _REDEEMLOCATION.oneofs_by_name['definition']
_REDEEMLOCATION.oneofs_by_name['definition'].fields.append(_REDEEMLOCATION.fields_by_name['owner_home_station'])
_REDEEMLOCATION.fields_by_name['owner_home_station'].containing_oneof = _REDEEMLOCATION.oneofs_by_name['definition']
DESCRIPTOR.message_types_by_name['SourceLocation'] = _SOURCELOCATION
DESCRIPTOR.message_types_by_name['AllowedDestinationLocation'] = _ALLOWEDDESTINATIONLOCATION
DESCRIPTOR.message_types_by_name['RedeemLocation'] = _REDEEMLOCATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SourceLocation = _reflection.GeneratedProtocolMessageType('SourceLocation', (_message.Message,), {'OwnerCurrentLocation': _reflection.GeneratedProtocolMessageType('OwnerCurrentLocation', (_message.Message,), {'DESCRIPTOR': _SOURCELOCATION_OWNERCURRENTLOCATION,
                          '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'OwnerHomeStation': _reflection.GeneratedProtocolMessageType('OwnerHomeStation', (_message.Message,), {'DESCRIPTOR': _SOURCELOCATION_OWNERHOMESTATION,
                      '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'DESCRIPTOR': _SOURCELOCATION,
 '__module__': 'eve.assetholding.inventory.inventory_pb2'})
_sym_db.RegisterMessage(SourceLocation)
_sym_db.RegisterMessage(SourceLocation.OwnerCurrentLocation)
_sym_db.RegisterMessage(SourceLocation.OwnerHomeStation)
AllowedDestinationLocation = _reflection.GeneratedProtocolMessageType('AllowedDestinationLocation', (_message.Message,), {'SourceLocation': _reflection.GeneratedProtocolMessageType('SourceLocation', (_message.Message,), {'DESCRIPTOR': _ALLOWEDDESTINATIONLOCATION_SOURCELOCATION,
                    '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'OwnerCurrentLocation': _reflection.GeneratedProtocolMessageType('OwnerCurrentLocation', (_message.Message,), {'DESCRIPTOR': _ALLOWEDDESTINATIONLOCATION_OWNERCURRENTLOCATION,
                          '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'OwnerHomeStation': _reflection.GeneratedProtocolMessageType('OwnerHomeStation', (_message.Message,), {'DESCRIPTOR': _ALLOWEDDESTINATIONLOCATION_OWNERHOMESTATION,
                      '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'DESCRIPTOR': _ALLOWEDDESTINATIONLOCATION,
 '__module__': 'eve.assetholding.inventory.inventory_pb2'})
_sym_db.RegisterMessage(AllowedDestinationLocation)
_sym_db.RegisterMessage(AllowedDestinationLocation.SourceLocation)
_sym_db.RegisterMessage(AllowedDestinationLocation.OwnerCurrentLocation)
_sym_db.RegisterMessage(AllowedDestinationLocation.OwnerHomeStation)
RedeemLocation = _reflection.GeneratedProtocolMessageType('RedeemLocation', (_message.Message,), {'SourceLocation': _reflection.GeneratedProtocolMessageType('SourceLocation', (_message.Message,), {'DESCRIPTOR': _REDEEMLOCATION_SOURCELOCATION,
                    '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'OwnerCurrentLocation': _reflection.GeneratedProtocolMessageType('OwnerCurrentLocation', (_message.Message,), {'DESCRIPTOR': _REDEEMLOCATION_OWNERCURRENTLOCATION,
                          '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'OwnerHomeStation': _reflection.GeneratedProtocolMessageType('OwnerHomeStation', (_message.Message,), {'DESCRIPTOR': _REDEEMLOCATION_OWNERHOMESTATION,
                      '__module__': 'eve.assetholding.inventory.inventory_pb2'}),
 'DESCRIPTOR': _REDEEMLOCATION,
 '__module__': 'eve.assetholding.inventory.inventory_pb2'})
_sym_db.RegisterMessage(RedeemLocation)
_sym_db.RegisterMessage(RedeemLocation.SourceLocation)
_sym_db.RegisterMessage(RedeemLocation.OwnerCurrentLocation)
_sym_db.RegisterMessage(RedeemLocation.OwnerHomeStation)
DESCRIPTOR._options = None
