#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vendors\steam\queue\item_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.store.offer import offer_pb2 as eve_dot_store_dot_offer_dot_offer__pb2
from eveProto.generated.eve.vendors.steam.user import user_pb2 as eve_dot_vendors_dot_steam_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vendors/steam/queue/item.proto', package='eve.vendors.steam.queue.item', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/steam/queue/item', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/vendors/steam/queue/item.proto\x12\x1ceve.vendors.steam.queue.item\x1a\x1beve/store/offer/offer.proto\x1a!eve/vendors/steam/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x03"\xfa\x02\n\nAttributes\x126\n\nsteam_user\x18\x01 \x01(\x0b2".eve.vendors.steam.user.Identifier\x120\n\x0ctime_created\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x121\n\rlast_modified\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x0e\n\x06status\x18\x04 \x01(\t\x12*\n\x05offer\x18\x05 \x01(\x0b2\x1b.eve.store.offer.Identifier\x12\x12\n\noffer_name\x18\x06 \x01(\t\x12\x18\n\x10agreement_status\x18\x07 \x01(\t\x12?\n\x0cqueue_status\x18\x08 \x01(\x0e2).eve.vendors.steam.queue.item.QueueStatus\x12$\n\x1cis_reactivation_cancellation\x18\t \x01(\x08*o\n\x0bQueueStatus\x12\x08\n\x04NONE\x10\x00\x12\x07\n\x03NEW\x10\x01\x12\x0e\n\nPROCESSING\x10\x02\x12\r\n\tPROCESSED\x10\x03\x12\x16\n\x12MANUALLY_CANCELLED\x10\x04\x12\x16\n\x12CANCELLED_ON_ERROR\x10\x05BIZGgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/steam/queue/itemb\x06proto3', dependencies=[eve_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR, eve_dot_vendors_dot_steam_dot_user_dot_user__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_QUEUESTATUS = _descriptor.EnumDescriptor(name='QueueStatus', full_name='eve.vendors.steam.queue.item.QueueStatus', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='NONE', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='NEW', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PROCESSING', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PROCESSED', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='MANUALLY_CANCELLED', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CANCELLED_ON_ERROR', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=580, serialized_end=691)
_sym_db.RegisterEnumDescriptor(_QUEUESTATUS)
QueueStatus = enum_type_wrapper.EnumTypeWrapper(_QUEUESTATUS)
NONE = 0
NEW = 1
PROCESSING = 2
PROCESSED = 3
MANUALLY_CANCELLED = 4
CANCELLED_ON_ERROR = 5
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.vendors.steam.queue.item.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.vendors.steam.queue.item.Identifier.sequential', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=165, serialized_end=197)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.vendors.steam.queue.item.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='steam_user', full_name='eve.vendors.steam.queue.item.Attributes.steam_user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='time_created', full_name='eve.vendors.steam.queue.item.Attributes.time_created', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_modified', full_name='eve.vendors.steam.queue.item.Attributes.last_modified', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='status', full_name='eve.vendors.steam.queue.item.Attributes.status', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve.vendors.steam.queue.item.Attributes.offer', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer_name', full_name='eve.vendors.steam.queue.item.Attributes.offer_name', index=5, number=6, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='agreement_status', full_name='eve.vendors.steam.queue.item.Attributes.agreement_status', index=6, number=7, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='queue_status', full_name='eve.vendors.steam.queue.item.Attributes.queue_status', index=7, number=8, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='is_reactivation_cancellation', full_name='eve.vendors.steam.queue.item.Attributes.is_reactivation_cancellation', index=8, number=9, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=200, serialized_end=578)
_ATTRIBUTES.fields_by_name['steam_user'].message_type = eve_dot_vendors_dot_steam_dot_user_dot_user__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['time_created'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['last_modified'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['offer'].message_type = eve_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['queue_status'].enum_type = _QUEUESTATUS
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['QueueStatus'] = _QUEUESTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.vendors.steam.queue.item_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.vendors.steam.queue.item_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
