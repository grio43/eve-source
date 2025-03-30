#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\loyaltypoints\wallet\assetholding\operation\operation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.loyaltypoints.wallet import wallet_pb2 as eve_dot_loyaltypoints_dot_wallet_dot_wallet__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/loyaltypoints/wallet/assetholding/operation/operation.proto', package='eve.loyaltypoints.wallet.assetholding.operation', syntax='proto3', serialized_options='ZZgithub.com/ccpgames/eve-proto-go/generated/eve/loyaltypoints/wallet/assetholding/operation', create_key=_descriptor._internal_create_key, serialized_pb='\n?eve/loyaltypoints/wallet/assetholding/operation/operation.proto\x12/eve.loyaltypoints.wallet.assetholding.operation\x1a%eve/loyaltypoints/wallet/wallet.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"v\n\nAttributes\x124\n\x06wallet\x18\x01 \x01(\x0b2$.eve.loyaltypoints.wallet.Identifier\x122\n\x06amount\x18\x02 \x01(\x0b2".eve.loyaltypoints.wallet.CurrencyB\\ZZgithub.com/ccpgames/eve-proto-go/generated/eve/loyaltypoints/wallet/assetholding/operationb\x06proto3', dependencies=[eve_dot_loyaltypoints_dot_wallet_dot_wallet__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.loyaltypoints.wallet.assetholding.operation.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.loyaltypoints.wallet.assetholding.operation.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=155, serialized_end=181)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.loyaltypoints.wallet.assetholding.operation.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='wallet', full_name='eve.loyaltypoints.wallet.assetholding.operation.Attributes.wallet', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='amount', full_name='eve.loyaltypoints.wallet.assetholding.operation.Attributes.amount', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=183, serialized_end=301)
_ATTRIBUTES.fields_by_name['wallet'].message_type = eve_dot_loyaltypoints_dot_wallet_dot_wallet__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['amount'].message_type = eve_dot_loyaltypoints_dot_wallet_dot_wallet__pb2._CURRENCY
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.loyaltypoints.wallet.assetholding.operation.operation_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.loyaltypoints.wallet.assetholding.operation.operation_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
