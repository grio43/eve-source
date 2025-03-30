#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\corporation\accounting\wallet_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/corporation/accounting/wallet.proto', package='eve.corporation.accounting.wallet', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/wallet', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/corporation/accounting/wallet.proto\x12!eve.corporation.accounting.wallet\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x11eve/isk/isk.proto"z\n\nIdentifier\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier\x12:\n\x08division\x18\x02 \x01(\x0e2(.eve.corporation.accounting.wallet.KeyID"0\n\nAttributes\x12"\n\x07balance\x18\x01 \x01(\x0b2\x11.eve.isk.Currency"~\n\x1cGetAllDivisionBalanceRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x120\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.Identifier"\xf7\x01\n\x1dGetAllDivisionBalanceResponse\x12c\n\tdivisions\x18\x01 \x03(\x0b2P.eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse.DivisionBalance\x1aq\n\x0fDivisionBalance\x12:\n\x08division\x18\x01 \x01(\x0e2(.eve.corporation.accounting.wallet.KeyID\x12"\n\x07balance\x18\x02 \x01(\x0b2\x11.eve.isk.Currency*\x8c\x01\n\x05KeyID\x12\x13\n\x0fMissingDivision\x10\x00\x12\x0e\n\tDivision0\x10\xe8\x07\x12\x0e\n\tDivision1\x10\xe9\x07\x12\x0e\n\tDivision2\x10\xea\x07\x12\x0e\n\tDivision3\x10\xeb\x07\x12\x0e\n\tDivision4\x10\xec\x07\x12\x0e\n\tDivision5\x10\xed\x07\x12\x0e\n\tDivision6\x10\xee\x07BCZAgithub.com/ccpgames/eve-proto-go/generated/eve/corporation/walletb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR])
_KEYID = _descriptor.EnumDescriptor(name='KeyID', full_name='eve.corporation.accounting.wallet.KeyID', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='MissingDivision', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division0', index=1, number=1000, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division1', index=2, number=1001, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division2', index=3, number=1002, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division3', index=4, number=1003, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division4', index=5, number=1004, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division5', index=6, number=1005, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='Division6', index=7, number=1006, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=716, serialized_end=856)
_sym_db.RegisterEnumDescriptor(_KEYID)
KeyID = enum_type_wrapper.EnumTypeWrapper(_KEYID)
MissingDivision = 0
Division0 = 1000
Division1 = 1001
Division2 = 1002
Division3 = 1003
Division4 = 1004
Division5 = 1005
Division6 = 1006
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.corporation.accounting.wallet.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.accounting.wallet.Identifier.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='division', full_name='eve.corporation.accounting.wallet.Identifier.division', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=163, serialized_end=285)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.corporation.accounting.wallet.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='balance', full_name='eve.corporation.accounting.wallet.Attributes.balance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=287, serialized_end=335)
_GETALLDIVISIONBALANCEREQUEST = _descriptor.Descriptor(name='GetAllDivisionBalanceRequest', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceRequest.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=337, serialized_end=463)
_GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE = _descriptor.Descriptor(name='DivisionBalance', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse.DivisionBalance', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='division', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse.DivisionBalance.division', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='balance', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse.DivisionBalance.balance', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=600, serialized_end=713)
_GETALLDIVISIONBALANCERESPONSE = _descriptor.Descriptor(name='GetAllDivisionBalanceResponse', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='divisions', full_name='eve.corporation.accounting.wallet.GetAllDivisionBalanceResponse.divisions', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=466, serialized_end=713)
_IDENTIFIER.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['division'].enum_type = _KEYID
_ATTRIBUTES.fields_by_name['balance'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_GETALLDIVISIONBALANCEREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETALLDIVISIONBALANCEREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE.fields_by_name['division'].enum_type = _KEYID
_GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE.fields_by_name['balance'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE.containing_type = _GETALLDIVISIONBALANCERESPONSE
_GETALLDIVISIONBALANCERESPONSE.fields_by_name['divisions'].message_type = _GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetAllDivisionBalanceRequest'] = _GETALLDIVISIONBALANCEREQUEST
DESCRIPTOR.message_types_by_name['GetAllDivisionBalanceResponse'] = _GETALLDIVISIONBALANCERESPONSE
DESCRIPTOR.enum_types_by_name['KeyID'] = _KEYID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.corporation.accounting.wallet_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.corporation.accounting.wallet_pb2'})
_sym_db.RegisterMessage(Attributes)
GetAllDivisionBalanceRequest = _reflection.GeneratedProtocolMessageType('GetAllDivisionBalanceRequest', (_message.Message,), {'DESCRIPTOR': _GETALLDIVISIONBALANCEREQUEST,
 '__module__': 'eve.corporation.accounting.wallet_pb2'})
_sym_db.RegisterMessage(GetAllDivisionBalanceRequest)
GetAllDivisionBalanceResponse = _reflection.GeneratedProtocolMessageType('GetAllDivisionBalanceResponse', (_message.Message,), {'DivisionBalance': _reflection.GeneratedProtocolMessageType('DivisionBalance', (_message.Message,), {'DESCRIPTOR': _GETALLDIVISIONBALANCERESPONSE_DIVISIONBALANCE,
                     '__module__': 'eve.corporation.accounting.wallet_pb2'}),
 'DESCRIPTOR': _GETALLDIVISIONBALANCERESPONSE,
 '__module__': 'eve.corporation.accounting.wallet_pb2'})
_sym_db.RegisterMessage(GetAllDivisionBalanceResponse)
_sym_db.RegisterMessage(GetAllDivisionBalanceResponse.DivisionBalance)
DESCRIPTOR._options = None
