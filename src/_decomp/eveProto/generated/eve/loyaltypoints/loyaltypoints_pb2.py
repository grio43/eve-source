#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\loyaltypoints\loyaltypoints_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/loyaltypoints/loyaltypoints.proto', package='eve.loyaltypoints', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/loyaltypoints', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/loyaltypoints/loyaltypoints.proto\x12\x11eve.loyaltypoints\x1a!eve/corporation/corporation.proto"W\n\x08Currency\x12\x0e\n\x06amount\x18\x01 \x01(\x04\x12;\n\x16associated_corporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.Identifier*_\n\x0fTransactionType\x12 \n\x1cTRANSACTION_TYPE_UNSPECIFIED\x10\x00\x12&\n"TRANSACTION_TYPE_DAILY_GOAL_REWARD\x10\x01\x1a\x02\x18\x01B>Z<github.com/ccpgames/eve-proto-go/generated/eve/loyaltypointsb\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_TRANSACTIONTYPE = _descriptor.EnumDescriptor(name='TransactionType', full_name='eve.loyaltypoints.TransactionType', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TRANSACTION_TYPE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='TRANSACTION_TYPE_DAILY_GOAL_REWARD', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options='\x18\x01', serialized_start=184, serialized_end=279)
_sym_db.RegisterEnumDescriptor(_TRANSACTIONTYPE)
TransactionType = enum_type_wrapper.EnumTypeWrapper(_TRANSACTIONTYPE)
TRANSACTION_TYPE_UNSPECIFIED = 0
TRANSACTION_TYPE_DAILY_GOAL_REWARD = 1
_CURRENCY = _descriptor.Descriptor(name='Currency', full_name='eve.loyaltypoints.Currency', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.loyaltypoints.Currency.amount', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='associated_corporation', full_name='eve.loyaltypoints.Currency.associated_corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=95, serialized_end=182)
_CURRENCY.fields_by_name['associated_corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Currency'] = _CURRENCY
DESCRIPTOR.enum_types_by_name['TransactionType'] = _TRANSACTIONTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Currency = _reflection.GeneratedProtocolMessageType('Currency', (_message.Message,), {'DESCRIPTOR': _CURRENCY,
 '__module__': 'eve.loyaltypoints.loyaltypoints_pb2'})
_sym_db.RegisterMessage(Currency)
DESCRIPTOR._options = None
_TRANSACTIONTYPE._options = None
