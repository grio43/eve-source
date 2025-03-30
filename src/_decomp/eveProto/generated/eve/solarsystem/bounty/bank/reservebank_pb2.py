#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\solarsystem\bounty\bank\reservebank_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/solarsystem/bounty/bank/reservebank.proto', package='eve.solarsystem.bounty.bank.reserve', syntax='proto3', serialized_options='ZRgithub.com/ccpgames/eve-proto-go/generated/eve/solarsystem/bounty/bank/reservebank', create_key=_descriptor._internal_create_key, serialized_pb='\n-eve/solarsystem/bounty/bank/reservebank.proto\x12#eve.solarsystem.bounty.bank.reserve\x1a\x11eve/isk/isk.proto\x1a!eve/solarsystem/solarsystem.proto"t\n\x11ReserveBankPrimed\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12,\n\x11ess_reserve_value\x18\x02 \x01(\x0b2\x11.eve.isk.CurrencyBTZRgithub.com/ccpgames/eve-proto-go/generated/eve/solarsystem/bounty/bank/reservebankb\x06proto3', dependencies=[eve_dot_isk_dot_isk__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_RESERVEBANKPRIMED = _descriptor.Descriptor(name='ReserveBankPrimed', full_name='eve.solarsystem.bounty.bank.reserve.ReserveBankPrimed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.solarsystem.bounty.bank.reserve.ReserveBankPrimed.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ess_reserve_value', full_name='eve.solarsystem.bounty.bank.reserve.ReserveBankPrimed.ess_reserve_value', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=140, serialized_end=256)
_RESERVEBANKPRIMED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_RESERVEBANKPRIMED.fields_by_name['ess_reserve_value'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
DESCRIPTOR.message_types_by_name['ReserveBankPrimed'] = _RESERVEBANKPRIMED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ReserveBankPrimed = _reflection.GeneratedProtocolMessageType('ReserveBankPrimed', (_message.Message,), {'DESCRIPTOR': _RESERVEBANKPRIMED,
 '__module__': 'eve.solarsystem.bounty.bank.reservebank_pb2'})
_sym_db.RegisterMessage(ReserveBankPrimed)
DESCRIPTOR._options = None
