#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\plex\vault\transaction_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/plex/vault/transaction.proto', package='eve.plex.vault.transaction', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/plex/vault/transaction', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/plex/vault/transaction.proto\x12\x1aeve.plex.vault.transaction\x1a\x13eve/plex/plex.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x03"\xc9\x01\n\nAttributes\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12"\n\x06amount\x18\x03 \x01(\x0b2\x12.eve.plex.Currency\x12.\n\x04type\x18\x04 \x01(\x0e2 .eve.plex.vault.transaction.Type\x12#\n\x07balance\x18\x05 \x01(\x0b2\x12.eve.plex.Currency*\x96\x02\n\x04Type\x12\x14\n\x10TYPE_UNSPECIFIED\x10\x00\x12\x1d\n\x19TYPE_BOUGHT_VIRTUAL_GOODS\x10\x01\x12\'\n#TYPE_BOUGHT_VIRTUAL_CURRENCY_ON_WEB\x10\x02\x12\x1e\n\x1aTYPE_DEPOSIT_PLEX_TO_VAULT\x10\x03\x12!\n\x1dTYPE_WITHDRAW_PLEX_FROM_VAULT\x10\x04\x12&\n"TYPE_ASSET_HOLDING_PLEX_WITHDRAWAL\x10\x05\x12#\n\x1fTYPE_ASSET_HOLDING_PLEX_DEPOSIT\x10\x06\x12 \n\x1cTYPE_MODIFY_VIRTUAL_CURRENCY\x10\x07BGZEgithub.com/ccpgames/eve-proto-go/generated/eve/plex/vault/transactionb\x06proto3', dependencies=[eve_dot_plex_dot_plex__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_TYPE = _descriptor.EnumDescriptor(name='Type', full_name='eve.plex.vault.transaction.Type', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TYPE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_BOUGHT_VIRTUAL_GOODS', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_BOUGHT_VIRTUAL_CURRENCY_ON_WEB', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_DEPOSIT_PLEX_TO_VAULT', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_WITHDRAW_PLEX_FROM_VAULT', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_ASSET_HOLDING_PLEX_WITHDRAWAL', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_ASSET_HOLDING_PLEX_DEPOSIT', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='TYPE_MODIFY_VIRTUAL_CURRENCY', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=357, serialized_end=635)
_sym_db.RegisterEnumDescriptor(_TYPE)
Type = enum_type_wrapper.EnumTypeWrapper(_TYPE)
TYPE_UNSPECIFIED = 0
TYPE_BOUGHT_VIRTUAL_GOODS = 1
TYPE_BOUGHT_VIRTUAL_CURRENCY_ON_WEB = 2
TYPE_DEPOSIT_PLEX_TO_VAULT = 3
TYPE_WITHDRAW_PLEX_FROM_VAULT = 4
TYPE_ASSET_HOLDING_PLEX_WITHDRAWAL = 5
TYPE_ASSET_HOLDING_PLEX_DEPOSIT = 6
TYPE_MODIFY_VIRTUAL_CURRENCY = 7
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.plex.vault.transaction.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.plex.vault.transaction.Identifier.sequential', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=118, serialized_end=150)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.plex.vault.transaction.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='timestamp', full_name='eve.plex.vault.transaction.Attributes.timestamp', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.plex.vault.transaction.Attributes.description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.plex.vault.transaction.Attributes.amount', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='type', full_name='eve.plex.vault.transaction.Attributes.type', index=3, number=4, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='balance', full_name='eve.plex.vault.transaction.Attributes.balance', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=153, serialized_end=354)
_ATTRIBUTES.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['amount'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_ATTRIBUTES.fields_by_name['type'].enum_type = _TYPE
_ATTRIBUTES.fields_by_name['balance'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['Type'] = _TYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.plex.vault.transaction_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.plex.vault.transaction_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
