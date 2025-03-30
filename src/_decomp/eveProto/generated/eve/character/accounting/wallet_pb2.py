#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\accounting\wallet_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/accounting/wallet.proto', package='eve.character.accounting.wallet', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/character/wallet', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/character/accounting/wallet.proto\x12\x1feve.character.accounting.wallet\x1a\x1deve/character/character.proto\x1a\x11eve/isk/isk.proto":\n\nIdentifier\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"0\n\nAttributes\x12"\n\x07balance\x18\x01 \x01(\x0b2\x11.eve.isk.Currency"L\n\nGetRequest\x12>\n\tcharacter\x18\x01 \x01(\x0b2+.eve.character.accounting.wallet.Identifier"J\n\x0bGetResponse\x12;\n\x06wallet\x18\x01 \x01(\x0b2+.eve.character.accounting.wallet.AttributesBAZ?github.com/ccpgames/eve-proto-go/generated/eve/character/walletb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.accounting.wallet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.accounting.wallet.Identifier.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=124, serialized_end=182)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.accounting.wallet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='balance', full_name='eve.character.accounting.wallet.Attributes.balance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=184, serialized_end=232)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.character.accounting.wallet.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.accounting.wallet.GetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=234, serialized_end=310)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.character.accounting.wallet.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='wallet', full_name='eve.character.accounting.wallet.GetResponse.wallet', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=312, serialized_end=386)
_IDENTIFIER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['balance'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_GETREQUEST.fields_by_name['character'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['wallet'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.accounting.wallet_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.accounting.wallet_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.character.accounting.wallet_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.character.accounting.wallet_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
