#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\plex\vault\assetholding\operation\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.assetholding import context_pb2 as eve_dot_assetholding_dot_context__pb2
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
from eveProto.generated.eve.plex.vault.assetholding.operation import operation_pb2 as eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/plex/vault/assetholding/operation/api/requests.proto', package='eve.plex.vault.assetholding.operation.api', syntax='proto3', serialized_options='ZTgithub.com/ccpgames/eve-proto-go/generated/eve/plex/vault/assetholding/operation/api', create_key=_descriptor._internal_create_key, serialized_pb='\n8eve/plex/vault/assetholding/operation/api/requests.proto\x12)eve.plex.vault.assetholding.operation.api\x1a\x1eeve/assetholding/context.proto\x1a\x13eve/plex/plex.proto\x1a5eve/plex/vault/assetholding/operation/operation.proto\x1a\x13eve/user/user.proto"R\n\nGetRequest\x12D\n\toperation\x18\x01 \x01(\x0b21.eve.plex.vault.assetholding.operation.Identifier"S\n\x0bGetResponse\x12D\n\toperation\x18\x01 \x01(\x0b21.eve.plex.vault.assetholding.operation.Attributes"\xc8\x01\n\x0eDepositRequest\x12D\n\toperation\x18\x01 \x01(\x0b21.eve.plex.vault.assetholding.operation.Identifier\x12"\n\x04user\x18\x02 \x01(\x0b2\x14.eve.user.Identifier\x12 \n\x04plex\x18\x03 \x01(\x0b2\x12.eve.plex.Currency\x12*\n\x07context\x18\x04 \x01(\x0b2\x19.eve.assetholding.Context"\x11\n\x0fDepositResponse"\xc9\x01\n\x0fWithdrawRequest\x12D\n\toperation\x18\x01 \x01(\x0b21.eve.plex.vault.assetholding.operation.Identifier\x12"\n\x04user\x18\x02 \x01(\x0b2\x14.eve.user.Identifier\x12 \n\x04plex\x18\x03 \x01(\x0b2\x12.eve.plex.Currency\x12*\n\x07context\x18\x04 \x01(\x0b2\x19.eve.assetholding.Context"\x12\n\x10WithdrawResponseBVZTgithub.com/ccpgames/eve-proto-go/generated/eve/plex/vault/assetholding/operation/apib\x06proto3', dependencies=[eve_dot_assetholding_dot_context__pb2.DESCRIPTOR,
 eve_dot_plex_dot_plex__pb2.DESCRIPTOR,
 eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.plex.vault.assetholding.operation.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve.plex.vault.assetholding.operation.api.GetRequest.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=232, serialized_end=314)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.plex.vault.assetholding.operation.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve.plex.vault.assetholding.operation.api.GetResponse.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=316, serialized_end=399)
_DEPOSITREQUEST = _descriptor.Descriptor(name='DepositRequest', full_name='eve.plex.vault.assetholding.operation.api.DepositRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve.plex.vault.assetholding.operation.api.DepositRequest.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user', full_name='eve.plex.vault.assetholding.operation.api.DepositRequest.user', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='plex', full_name='eve.plex.vault.assetholding.operation.api.DepositRequest.plex', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.plex.vault.assetholding.operation.api.DepositRequest.context', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=402, serialized_end=602)
_DEPOSITRESPONSE = _descriptor.Descriptor(name='DepositResponse', full_name='eve.plex.vault.assetholding.operation.api.DepositResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=604, serialized_end=621)
_WITHDRAWREQUEST = _descriptor.Descriptor(name='WithdrawRequest', full_name='eve.plex.vault.assetholding.operation.api.WithdrawRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='operation', full_name='eve.plex.vault.assetholding.operation.api.WithdrawRequest.operation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user', full_name='eve.plex.vault.assetholding.operation.api.WithdrawRequest.user', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='plex', full_name='eve.plex.vault.assetholding.operation.api.WithdrawRequest.plex', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='context', full_name='eve.plex.vault.assetholding.operation.api.WithdrawRequest.context', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=624, serialized_end=825)
_WITHDRAWRESPONSE = _descriptor.Descriptor(name='WithdrawResponse', full_name='eve.plex.vault.assetholding.operation.api.WithdrawResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=827, serialized_end=845)
_GETREQUEST.fields_by_name['operation'].message_type = eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['operation'].message_type = eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2._ATTRIBUTES
_DEPOSITREQUEST.fields_by_name['operation'].message_type = eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2._IDENTIFIER
_DEPOSITREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_DEPOSITREQUEST.fields_by_name['plex'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_DEPOSITREQUEST.fields_by_name['context'].message_type = eve_dot_assetholding_dot_context__pb2._CONTEXT
_WITHDRAWREQUEST.fields_by_name['operation'].message_type = eve_dot_plex_dot_vault_dot_assetholding_dot_operation_dot_operation__pb2._IDENTIFIER
_WITHDRAWREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_WITHDRAWREQUEST.fields_by_name['plex'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_WITHDRAWREQUEST.fields_by_name['context'].message_type = eve_dot_assetholding_dot_context__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['DepositRequest'] = _DEPOSITREQUEST
DESCRIPTOR.message_types_by_name['DepositResponse'] = _DEPOSITRESPONSE
DESCRIPTOR.message_types_by_name['WithdrawRequest'] = _WITHDRAWREQUEST
DESCRIPTOR.message_types_by_name['WithdrawResponse'] = _WITHDRAWRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
DepositRequest = _reflection.GeneratedProtocolMessageType('DepositRequest', (_message.Message,), {'DESCRIPTOR': _DEPOSITREQUEST,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(DepositRequest)
DepositResponse = _reflection.GeneratedProtocolMessageType('DepositResponse', (_message.Message,), {'DESCRIPTOR': _DEPOSITRESPONSE,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(DepositResponse)
WithdrawRequest = _reflection.GeneratedProtocolMessageType('WithdrawRequest', (_message.Message,), {'DESCRIPTOR': _WITHDRAWREQUEST,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(WithdrawRequest)
WithdrawResponse = _reflection.GeneratedProtocolMessageType('WithdrawResponse', (_message.Message,), {'DESCRIPTOR': _WITHDRAWRESPONSE,
 '__module__': 'eve.plex.vault.assetholding.operation.api.requests_pb2'})
_sym_db.RegisterMessage(WithdrawResponse)
DESCRIPTOR._options = None
