#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\market\entry\transaction_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/market/entry/transaction.proto', package='eve.market.transaction', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/market/transaction', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/market/entry/transaction.proto\x12\x16eve.market.transaction" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x12"\x0c\n\nAttributesBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/market/transactionb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.market.transaction.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.market.transaction.Identifier.sequential', index=0, number=1, type=18, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=62, serialized_end=94)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.market.transaction.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=96, serialized_end=108)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.market.entry.transaction_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.market.entry.transaction_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
