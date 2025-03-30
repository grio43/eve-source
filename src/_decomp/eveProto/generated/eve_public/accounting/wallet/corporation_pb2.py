#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\accounting\wallet\corporation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.corporation import corporation_pb2 as eve__public_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/accounting/wallet/corporation.proto', package='eve_public.accounting.wallet.corporation', syntax='proto3', serialized_options='ZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/accounting/wallet/corporation', create_key=_descriptor._internal_create_key, serialized_pb='\n.eve_public/accounting/wallet/corporation.proto\x12(eve_public.accounting.wallet.corporation\x1a(eve_public/corporation/corporation.proto"Z\n\nIdentifier\x127\n\x0bcorporation\x18\x01 \x01(\x0b2".eve_public.corporation.Identifier\x12\x13\n\x0baccount_key\x18\x02 \x01(\rBUZSgithub.com/ccpgames/eve-proto-go/generated/eve_public/accounting/wallet/corporationb\x06proto3', dependencies=[eve__public_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.accounting.wallet.corporation.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve_public.accounting.wallet.corporation.Identifier.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='account_key', full_name='eve_public.accounting.wallet.corporation.Identifier.account_key', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=134, serialized_end=224)
_IDENTIFIER.fields_by_name['corporation'].message_type = eve__public_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.accounting.wallet.corporation_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
