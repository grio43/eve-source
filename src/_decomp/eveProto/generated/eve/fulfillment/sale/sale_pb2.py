#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\fulfillment\sale\sale_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.accounting import transaction_pb2 as eve_dot_accounting_dot_transaction__pb2
from eveProto.generated.eve.fulfillment.offer import offer_pb2 as eve_dot_fulfillment_dot_offer_dot_offer__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/fulfillment/sale/sale.proto', package='eve.fulfillment.sale', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/fulfillment/sale', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/fulfillment/sale/sale.proto\x12\x14eve.fulfillment.sale\x1a eve/accounting/transaction.proto\x1a!eve/fulfillment/offer/offer.proto\x1a\x1fgoogle/protobuf/timestamp.proto"$\n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r:\x02\x18\x01"\xc8\x01\n\nAttributes\x12/\n\x0bcreate_date\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x120\n\x05offer\x18\x02 \x01(\x0b2!.eve.fulfillment.offer.Identifier\x12\x16\n\x0eoffer_quantity\x18\x03 \x01(\x05\x12;\n\x0btransaction\x18\x04 \x01(\x0b2&.eve.accounting.transaction.Identifier:\x02\x18\x01BAZ?github.com/ccpgames/eve-proto-go/generated/eve/fulfillment/saleb\x06proto3', dependencies=[eve_dot_accounting_dot_transaction__pb2.DESCRIPTOR, eve_dot_fulfillment_dot_offer_dot_offer__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.fulfillment.sale.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.fulfillment.sale.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=159, serialized_end=195)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.fulfillment.sale.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='create_date', full_name='eve.fulfillment.sale.Attributes.create_date', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve.fulfillment.sale.Attributes.offer', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer_quantity', full_name='eve.fulfillment.sale.Attributes.offer_quantity', index=2, number=3, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='transaction', full_name='eve.fulfillment.sale.Attributes.transaction', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=198, serialized_end=398)
_ATTRIBUTES.fields_by_name['create_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['offer'].message_type = eve_dot_fulfillment_dot_offer_dot_offer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['transaction'].message_type = eve_dot_accounting_dot_transaction__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.fulfillment.sale.sale_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.fulfillment.sale.sale_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
_IDENTIFIER._options = None
_ATTRIBUTES._options = None
