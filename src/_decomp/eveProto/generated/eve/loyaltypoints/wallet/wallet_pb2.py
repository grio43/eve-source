#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\loyaltypoints\wallet\wallet_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/loyaltypoints/wallet/wallet.proto', package='eve.loyaltypoints.wallet', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/loyaltypoints/wallet', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/loyaltypoints/wallet/wallet.proto\x12\x18eve.loyaltypoints.wallet\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto"\xa6\x01\n\nIdentifier\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12+\n\x06issuer\x18\x03 \x01(\x0b2\x1b.eve.corporation.IdentifierB\x07\n\x05owner"A\n\nAttributes\x123\n\x07balance\x18\x01 \x01(\x0b2".eve.loyaltypoints.wallet.Currency"\x1a\n\x08Currency\x12\x0e\n\x06amount\x18\x01 \x01(\x04BEZCgithub.com/ccpgames/eve-proto-go/generated/eve/loyaltypoints/walletb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.loyaltypoints.wallet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.loyaltypoints.wallet.Identifier.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.loyaltypoints.wallet.Identifier.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='issuer', full_name='eve.loyaltypoints.wallet.Identifier.issuer', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='owner', full_name='eve.loyaltypoints.wallet.Identifier.owner', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=134, serialized_end=300)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.loyaltypoints.wallet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='balance', full_name='eve.loyaltypoints.wallet.Attributes.balance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=302, serialized_end=367)
_CURRENCY = _descriptor.Descriptor(name='Currency', full_name='eve.loyaltypoints.wallet.Currency', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.loyaltypoints.wallet.Currency.amount', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=369, serialized_end=395)
_IDENTIFIER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['issuer'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['owner'].fields.append(_IDENTIFIER.fields_by_name['character'])
_IDENTIFIER.fields_by_name['character'].containing_oneof = _IDENTIFIER.oneofs_by_name['owner']
_IDENTIFIER.oneofs_by_name['owner'].fields.append(_IDENTIFIER.fields_by_name['corporation'])
_IDENTIFIER.fields_by_name['corporation'].containing_oneof = _IDENTIFIER.oneofs_by_name['owner']
_ATTRIBUTES.fields_by_name['balance'].message_type = _CURRENCY
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Currency'] = _CURRENCY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.loyaltypoints.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.loyaltypoints.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Attributes)
Currency = _reflection.GeneratedProtocolMessageType('Currency', (_message.Message,), {'DESCRIPTOR': _CURRENCY,
 '__module__': 'eve.loyaltypoints.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Currency)
DESCRIPTOR._options = None
