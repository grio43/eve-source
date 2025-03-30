#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\isk\wallet\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.accounting import entrytype_pb2 as eve_dot_accounting_dot_entrytype__pb2
from eveProto.generated.eve.accounting import transaction_pb2 as eve_dot_accounting_dot_transaction__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.isk.wallet import wallet_pb2 as eve_dot_isk_dot_wallet_dot_wallet__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/isk/wallet/api/events.proto', package='eve.isk.wallet.api', syntax='proto3', serialized_options='Z=github.com/ccpgames/eve-proto-go/generated/eve/isk/wallet/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1feve/isk/wallet/api/events.proto\x12\x12eve.isk.wallet.api\x1a\x1eeve/accounting/entrytype.proto\x1a eve/accounting/transaction.proto\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x11eve/isk/isk.proto\x1a\x1beve/isk/wallet/wallet.proto"\xbd\x03\n\x0eGrantCommanded\x12\x1b\n\x11from_wallet_owner\x18\x01 \x01(\x08H\x00\x125\n\x10acting_character\x18\x02 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x12,\n\rtransfer_from\x18\x03 \x01(\x0b2\x15.eve.isk.wallet.Owner\x12*\n\x0btransfer_to\x18\x04 \x01(\x0b2\x15.eve.isk.wallet.Owner\x12!\n\x06amount\x18\x05 \x01(\x0b2\x11.eve.isk.Currency\x128\n\nentry_type\x18\x06 \x01(\x0b2$.eve.accounting.entrytype.Identifier\x12@\n\treference\x18\x07 \x01(\x0b2-.eve.accounting.transaction.ExternalReference\x12\x10\n\x06direct\x18\x08 \x01(\x08H\x01\x129\n\x12client_corporation\x18\t \x01(\x0b2\x1b.eve.corporation.IdentifierH\x01B\x07\n\x05actorB\x08\n\x06clientB?Z=github.com/ccpgames/eve-proto-go/generated/eve/isk/wallet/apib\x06proto3', dependencies=[eve_dot_accounting_dot_entrytype__pb2.DESCRIPTOR,
 eve_dot_accounting_dot_transaction__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_isk_dot_wallet_dot_wallet__pb2.DESCRIPTOR])
_GRANTCOMMANDED = _descriptor.Descriptor(name='GrantCommanded', full_name='eve.isk.wallet.api.GrantCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='from_wallet_owner', full_name='eve.isk.wallet.api.GrantCommanded.from_wallet_owner', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='acting_character', full_name='eve.isk.wallet.api.GrantCommanded.acting_character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='transfer_from', full_name='eve.isk.wallet.api.GrantCommanded.transfer_from', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='transfer_to', full_name='eve.isk.wallet.api.GrantCommanded.transfer_to', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.isk.wallet.api.GrantCommanded.amount', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='entry_type', full_name='eve.isk.wallet.api.GrantCommanded.entry_type', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reference', full_name='eve.isk.wallet.api.GrantCommanded.reference', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='direct', full_name='eve.isk.wallet.api.GrantCommanded.direct', index=7, number=8, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='client_corporation', full_name='eve.isk.wallet.api.GrantCommanded.client_corporation', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='actor', full_name='eve.isk.wallet.api.GrantCommanded.actor', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='client', full_name='eve.isk.wallet.api.GrantCommanded.client', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=236, serialized_end=681)
_GRANTCOMMANDED.fields_by_name['acting_character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GRANTCOMMANDED.fields_by_name['transfer_from'].message_type = eve_dot_isk_dot_wallet_dot_wallet__pb2._OWNER
_GRANTCOMMANDED.fields_by_name['transfer_to'].message_type = eve_dot_isk_dot_wallet_dot_wallet__pb2._OWNER
_GRANTCOMMANDED.fields_by_name['amount'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_GRANTCOMMANDED.fields_by_name['entry_type'].message_type = eve_dot_accounting_dot_entrytype__pb2._IDENTIFIER
_GRANTCOMMANDED.fields_by_name['reference'].message_type = eve_dot_accounting_dot_transaction__pb2._EXTERNALREFERENCE
_GRANTCOMMANDED.fields_by_name['client_corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GRANTCOMMANDED.oneofs_by_name['actor'].fields.append(_GRANTCOMMANDED.fields_by_name['from_wallet_owner'])
_GRANTCOMMANDED.fields_by_name['from_wallet_owner'].containing_oneof = _GRANTCOMMANDED.oneofs_by_name['actor']
_GRANTCOMMANDED.oneofs_by_name['actor'].fields.append(_GRANTCOMMANDED.fields_by_name['acting_character'])
_GRANTCOMMANDED.fields_by_name['acting_character'].containing_oneof = _GRANTCOMMANDED.oneofs_by_name['actor']
_GRANTCOMMANDED.oneofs_by_name['client'].fields.append(_GRANTCOMMANDED.fields_by_name['direct'])
_GRANTCOMMANDED.fields_by_name['direct'].containing_oneof = _GRANTCOMMANDED.oneofs_by_name['client']
_GRANTCOMMANDED.oneofs_by_name['client'].fields.append(_GRANTCOMMANDED.fields_by_name['client_corporation'])
_GRANTCOMMANDED.fields_by_name['client_corporation'].containing_oneof = _GRANTCOMMANDED.oneofs_by_name['client']
DESCRIPTOR.message_types_by_name['GrantCommanded'] = _GRANTCOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantCommanded = _reflection.GeneratedProtocolMessageType('GrantCommanded', (_message.Message,), {'DESCRIPTOR': _GRANTCOMMANDED,
 '__module__': 'eve.isk.wallet.api.events_pb2'})
_sym_db.RegisterMessage(GrantCommanded)
DESCRIPTOR._options = None
