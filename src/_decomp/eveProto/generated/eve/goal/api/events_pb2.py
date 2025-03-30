#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\goal\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation.accounting import wallet_pb2 as eve_dot_corporation_dot_accounting_dot_wallet__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.corporation import office_pb2 as eve_dot_corporation_dot_office__pb2
from eveProto.generated.eve.goal import goal_pb2 as eve_dot_goal_dot_goal__pb2
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/goal/api/events.proto', package='eve.goal.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/goal/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/goal/api/events.proto\x12\x0ceve.goal.api\x1a\x1deve/character/character.proto\x1a\'eve/corporation/accounting/wallet.proto\x1a!eve/corporation/corporation.proto\x1a\x1ceve/corporation/office.proto\x1a\x13eve/goal/goal.proto\x1a eve/inventory/generic_item.proto\x1a\x11eve/isk/isk.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto"O\n\x07Created\x12 \n\x02id\x18\x01 \x01(\x0b2\x14.eve.goal.Identifier\x12"\n\x04goal\x18\x02 \x01(\x0b2\x14.eve.goal.Attributes"-\n\x07Deleted\x12"\n\x04goal\x18\x01 \x01(\x0b2\x14.eve.goal.Identifier"y\n\x06Closed\x12 \n\x02id\x18\x01 \x01(\x0b2\x14.eve.goal.Identifier\x12"\n\x04goal\x18\x02 \x01(\x0b2\x14.eve.goal.Attributes\x12)\n\x06closer\x18\x03 \x01(\x0b2\x19.eve.character.Identifier"Q\n\tCompleted\x12 \n\x02id\x18\x01 \x01(\x0b2\x14.eve.goal.Identifier\x12"\n\x04goal\x18\x02 \x01(\x0b2\x14.eve.goal.Attributes"\xc3\x02\n\x10DeliveryReceived\x129\n\nitem_moved\x18\x01 \x01(\x0b2%.eve.inventory.genericitem.Attributes\x12)\n\x06sender\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12-\n\x08receiver\x18\x03 \x01(\x0b2\x1b.eve.corporation.Identifier\x122\n\x06office\x18\x04 \x01(\x0b2".eve.corporation.office.Identifier\x12.\n\tstructure\x18\x05 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x12*\n\x07station\x18\x06 \x01(\x0b2\x17.eve.station.IdentifierH\x00B\n\n\x08location"\xce\x01\n\nIskDonated\x12*\n\x07donator\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12!\n\x06amount\x18\x02 \x01(\x0b2\x11.eve.isk.Currency\x12"\n\x04goal\x18\x03 \x01(\x0b2\x14.eve.goal.Identifier\x12I\n\x12corporation_wallet\x18\x04 \x01(\x0b2-.eve.corporation.accounting.wallet.Identifier:\x02\x18\x01"g\n\x0bNameChanged\x12 \n\x02id\x18\x01 \x01(\x0b2\x14.eve.goal.Identifier\x12(\n\x08assignee\x18\x02 \x01(\x0b2\x16.eve.goal.Organization\x12\x0c\n\x04name\x18\x03 \x01(\tB9Z7github.com/ccpgames/eve-proto-go/generated/eve/goal/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_accounting_dot_wallet__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_office__pb2.DESCRIPTOR,
 eve_dot_goal_dot_goal__pb2.DESCRIPTOR,
 eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve.goal.api.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.goal.api.Created.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='goal', full_name='eve.goal.api.Created.goal', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=312, serialized_end=391)
_DELETED = _descriptor.Descriptor(name='Deleted', full_name='eve.goal.api.Deleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve.goal.api.Deleted.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=393, serialized_end=438)
_CLOSED = _descriptor.Descriptor(name='Closed', full_name='eve.goal.api.Closed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.goal.api.Closed.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='goal', full_name='eve.goal.api.Closed.goal', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='closer', full_name='eve.goal.api.Closed.closer', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=440, serialized_end=561)
_COMPLETED = _descriptor.Descriptor(name='Completed', full_name='eve.goal.api.Completed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.goal.api.Completed.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='goal', full_name='eve.goal.api.Completed.goal', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=563, serialized_end=644)
_DELIVERYRECEIVED = _descriptor.Descriptor(name='DeliveryReceived', full_name='eve.goal.api.DeliveryReceived', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item_moved', full_name='eve.goal.api.DeliveryReceived.item_moved', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sender', full_name='eve.goal.api.DeliveryReceived.sender', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='receiver', full_name='eve.goal.api.DeliveryReceived.receiver', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='office', full_name='eve.goal.api.DeliveryReceived.office', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.goal.api.DeliveryReceived.structure', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.goal.api.DeliveryReceived.station', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='location', full_name='eve.goal.api.DeliveryReceived.location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=647, serialized_end=970)
_ISKDONATED = _descriptor.Descriptor(name='IskDonated', full_name='eve.goal.api.IskDonated', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='donator', full_name='eve.goal.api.IskDonated.donator', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.goal.api.IskDonated.amount', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='goal', full_name='eve.goal.api.IskDonated.goal', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation_wallet', full_name='eve.goal.api.IskDonated.corporation_wallet', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=973, serialized_end=1179)
_NAMECHANGED = _descriptor.Descriptor(name='NameChanged', full_name='eve.goal.api.NameChanged', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.goal.api.NameChanged.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='assignee', full_name='eve.goal.api.NameChanged.assignee', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='name', full_name='eve.goal.api.NameChanged.name', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1181, serialized_end=1284)
_CREATED.fields_by_name['id'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_CREATED.fields_by_name['goal'].message_type = eve_dot_goal_dot_goal__pb2._ATTRIBUTES
_DELETED.fields_by_name['goal'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_CLOSED.fields_by_name['id'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_CLOSED.fields_by_name['goal'].message_type = eve_dot_goal_dot_goal__pb2._ATTRIBUTES
_CLOSED.fields_by_name['closer'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_COMPLETED.fields_by_name['id'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_COMPLETED.fields_by_name['goal'].message_type = eve_dot_goal_dot_goal__pb2._ATTRIBUTES
_DELIVERYRECEIVED.fields_by_name['item_moved'].message_type = eve_dot_inventory_dot_generic__item__pb2._ATTRIBUTES
_DELIVERYRECEIVED.fields_by_name['sender'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_DELIVERYRECEIVED.fields_by_name['receiver'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_DELIVERYRECEIVED.fields_by_name['office'].message_type = eve_dot_corporation_dot_office__pb2._IDENTIFIER
_DELIVERYRECEIVED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_DELIVERYRECEIVED.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_DELIVERYRECEIVED.oneofs_by_name['location'].fields.append(_DELIVERYRECEIVED.fields_by_name['structure'])
_DELIVERYRECEIVED.fields_by_name['structure'].containing_oneof = _DELIVERYRECEIVED.oneofs_by_name['location']
_DELIVERYRECEIVED.oneofs_by_name['location'].fields.append(_DELIVERYRECEIVED.fields_by_name['station'])
_DELIVERYRECEIVED.fields_by_name['station'].containing_oneof = _DELIVERYRECEIVED.oneofs_by_name['location']
_ISKDONATED.fields_by_name['donator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ISKDONATED.fields_by_name['amount'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_ISKDONATED.fields_by_name['goal'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_ISKDONATED.fields_by_name['corporation_wallet'].message_type = eve_dot_corporation_dot_accounting_dot_wallet__pb2._IDENTIFIER
_NAMECHANGED.fields_by_name['id'].message_type = eve_dot_goal_dot_goal__pb2._IDENTIFIER
_NAMECHANGED.fields_by_name['assignee'].message_type = eve_dot_goal_dot_goal__pb2._ORGANIZATION
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
DESCRIPTOR.message_types_by_name['Deleted'] = _DELETED
DESCRIPTOR.message_types_by_name['Closed'] = _CLOSED
DESCRIPTOR.message_types_by_name['Completed'] = _COMPLETED
DESCRIPTOR.message_types_by_name['DeliveryReceived'] = _DELIVERYRECEIVED
DESCRIPTOR.message_types_by_name['IskDonated'] = _ISKDONATED
DESCRIPTOR.message_types_by_name['NameChanged'] = _NAMECHANGED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(Created)
Deleted = _reflection.GeneratedProtocolMessageType('Deleted', (_message.Message,), {'DESCRIPTOR': _DELETED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(Deleted)
Closed = _reflection.GeneratedProtocolMessageType('Closed', (_message.Message,), {'DESCRIPTOR': _CLOSED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(Closed)
Completed = _reflection.GeneratedProtocolMessageType('Completed', (_message.Message,), {'DESCRIPTOR': _COMPLETED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(Completed)
DeliveryReceived = _reflection.GeneratedProtocolMessageType('DeliveryReceived', (_message.Message,), {'DESCRIPTOR': _DELIVERYRECEIVED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(DeliveryReceived)
IskDonated = _reflection.GeneratedProtocolMessageType('IskDonated', (_message.Message,), {'DESCRIPTOR': _ISKDONATED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(IskDonated)
NameChanged = _reflection.GeneratedProtocolMessageType('NameChanged', (_message.Message,), {'DESCRIPTOR': _NAMECHANGED,
 '__module__': 'eve.goal.api.events_pb2'})
_sym_db.RegisterMessage(NameChanged)
DESCRIPTOR._options = None
_ISKDONATED._options = None
