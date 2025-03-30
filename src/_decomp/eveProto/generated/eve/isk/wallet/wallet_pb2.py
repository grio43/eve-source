#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\isk\wallet\wallet_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/isk/wallet/wallet.proto', package='eve.isk.wallet', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/isk/wallet', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/isk/wallet/wallet.proto\x12\x0eeve.isk.wallet\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x11eve/isk/isk.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x05"V\n\nAttributes\x12$\n\x05owner\x18\x01 \x01(\x0b2\x15.eve.isk.wallet.Owner\x12"\n\x07balance\x18\x02 \x01(\x0b2\x11.eve.isk.Currency"y\n\x05Owner\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00B\x0c\n\nowner_typeB;Z9github.com/ccpgames/eve-proto-go/generated/eve/isk/walletb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.isk.wallet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.isk.wallet.Identifier.sequential', index=0, number=1, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=164)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.isk.wallet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='owner', full_name='eve.isk.wallet.Attributes.owner', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='balance', full_name='eve.isk.wallet.Attributes.balance', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=166, serialized_end=252)
_OWNER = _descriptor.Descriptor(name='Owner', full_name='eve.isk.wallet.Owner', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.isk.wallet.Owner.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.isk.wallet.Owner.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='owner_type', full_name='eve.isk.wallet.Owner.owner_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=254, serialized_end=375)
_ATTRIBUTES.fields_by_name['owner'].message_type = _OWNER
_ATTRIBUTES.fields_by_name['balance'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_OWNER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_OWNER.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_OWNER.oneofs_by_name['owner_type'].fields.append(_OWNER.fields_by_name['character'])
_OWNER.fields_by_name['character'].containing_oneof = _OWNER.oneofs_by_name['owner_type']
_OWNER.oneofs_by_name['owner_type'].fields.append(_OWNER.fields_by_name['corporation'])
_OWNER.fields_by_name['corporation'].containing_oneof = _OWNER.oneofs_by_name['owner_type']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Owner'] = _OWNER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.isk.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.isk.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Attributes)
Owner = _reflection.GeneratedProtocolMessageType('Owner', (_message.Message,), {'DESCRIPTOR': _OWNER,
 '__module__': 'eve.isk.wallet.wallet_pb2'})
_sym_db.RegisterMessage(Owner)
DESCRIPTOR._options = None
