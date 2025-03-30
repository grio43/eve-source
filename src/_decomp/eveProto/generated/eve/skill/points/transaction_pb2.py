#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\points\transaction_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/points/transaction.proto', package='eve.skill.points', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/skill/points', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/skill/points/transaction.proto\x12\x10eve.skill.points*[\n\x0fTransactionType\x12 \n\x1cTRANSACTION_TYPE_UNSPECIFIED\x10\x00\x12&\n"TRANSACTION_TYPE_DAILY_GOAL_REWARD\x10\x01B=Z;github.com/ccpgames/eve-proto-go/generated/eve/skill/pointsb\x06proto3')
_TRANSACTIONTYPE = _descriptor.EnumDescriptor(name='TransactionType', full_name='eve.skill.points.TransactionType', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='TRANSACTION_TYPE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='TRANSACTION_TYPE_DAILY_GOAL_REWARD', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=56, serialized_end=147)
_sym_db.RegisterEnumDescriptor(_TRANSACTIONTYPE)
TransactionType = enum_type_wrapper.EnumTypeWrapper(_TRANSACTIONTYPE)
TRANSACTION_TYPE_UNSPECIFIED = 0
TRANSACTION_TYPE_DAILY_GOAL_REWARD = 1
DESCRIPTOR.enum_types_by_name['TransactionType'] = _TRANSACTIONTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
