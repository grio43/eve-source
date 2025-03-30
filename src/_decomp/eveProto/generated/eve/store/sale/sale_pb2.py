#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\store\sale\sale_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.accounting import transaction_pb2 as eve_dot_accounting_dot_transaction__pb2
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
from eveProto.generated.eve.store.offer import offer_pb2 as eve_dot_store_dot_offer_dot_offer__pb2
from eveProto.generated.eve.store import store_pb2 as eve_dot_store_dot_store__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/store/sale/sale.proto', package='eve.store.sale', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/store/sale', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/store/sale/sale.proto\x12\x0eeve.store.sale\x1a eve/accounting/transaction.proto\x1a\x19eve/payment/payment.proto\x1a\x1beve/store/offer/offer.proto\x1a\x15eve/store/store.proto\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xdc\x02\n\nAttributes\x12&\n\x06amount\x18\x01 \x01(\x0b2\x12.eve.payment.MoneyB\x02\x18\x01\x12+\n\x0epayment_method\x18\x02 \x01(\x0e2\x13.eve.payment.Method\x12*\n\x05offer\x18\x03 \x01(\x0b2\x1b.eve.store.offer.Identifier\x12\x16\n\x0eoffer_quantity\x18\x04 \x01(\x05\x12/\n\x0bcreate_date\x18\x05 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12?\n\x0btransaction\x18\x06 \x01(\x0b2&.eve.accounting.transaction.IdentifierB\x02\x18\x01\x12\x1f\n\x05price\x18\x07 \x01(\x0b2\x10.eve.store.Price\x12"\n\x04user\x18\x08 \x01(\x0b2\x14.eve.user.IdentifierB;Z9github.com/ccpgames/eve-proto-go/generated/eve/store/saleb\x06proto3', dependencies=[eve_dot_accounting_dot_transaction__pb2.DESCRIPTOR,
 eve_dot_payment_dot_payment__pb2.DESCRIPTOR,
 eve_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR,
 eve_dot_store_dot_store__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.store.sale.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.store.sale.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=212, serialized_end=244)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.store.sale.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.store.sale.Attributes.amount', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_method', full_name='eve.store.sale.Attributes.payment_method', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve.store.sale.Attributes.offer', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer_quantity', full_name='eve.store.sale.Attributes.offer_quantity', index=3, number=4, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='create_date', full_name='eve.store.sale.Attributes.create_date', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='transaction', full_name='eve.store.sale.Attributes.transaction', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='price', full_name='eve.store.sale.Attributes.price', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user', full_name='eve.store.sale.Attributes.user', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=247, serialized_end=595)
_ATTRIBUTES.fields_by_name['amount'].message_type = eve_dot_payment_dot_payment__pb2._MONEY
_ATTRIBUTES.fields_by_name['payment_method'].enum_type = eve_dot_payment_dot_payment__pb2._METHOD
_ATTRIBUTES.fields_by_name['offer'].message_type = eve_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['create_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['transaction'].message_type = eve_dot_accounting_dot_transaction__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['price'].message_type = eve_dot_store_dot_store__pb2._PRICE
_ATTRIBUTES.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.store.sale.sale_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.store.sale.sale_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
_ATTRIBUTES.fields_by_name['amount']._options = None
_ATTRIBUTES.fields_by_name['transaction']._options = None
