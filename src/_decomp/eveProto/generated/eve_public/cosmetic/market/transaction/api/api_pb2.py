#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\market\transaction\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.cosmetic.market.transaction import transaction_pb2 as eve__public_dot_cosmetic_dot_market_dot_transaction_dot_transaction__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/market/transaction/api/api.proto', package='eve_public.cosmetic.market.transaction.api', syntax='proto3', serialized_options='ZUgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/market/transaction/api', create_key=_descriptor._internal_create_key, serialized_pb='\n4eve_public/cosmetic/market/transaction/api/api.proto\x12*eve_public.cosmetic.market.transaction.api\x1a8eve_public/cosmetic/market/transaction/transaction.proto"\x0f\n\rGetAllRequest"Z\n\x0eGetAllResponse\x12H\n\x0ctransactions\x18\x01 \x03(\x0b22.eve_public.cosmetic.market.transaction.Identifier"U\n\nGetRequest\x12G\n\x0btransaction\x18\x01 \x01(\x0b22.eve_public.cosmetic.market.transaction.Identifier"Q\n\x0bGetResponse\x12B\n\x06status\x18\x01 \x01(\x0b22.eve_public.cosmetic.market.transaction.AttributesBWZUgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/market/transaction/apib\x06proto3', dependencies=[eve__public_dot_cosmetic_dot_market_dot_transaction_dot_transaction__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve_public.cosmetic.market.transaction.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=158, serialized_end=173)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve_public.cosmetic.market.transaction.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='transactions', full_name='eve_public.cosmetic.market.transaction.api.GetAllResponse.transactions', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=175, serialized_end=265)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.cosmetic.market.transaction.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='transaction', full_name='eve_public.cosmetic.market.transaction.api.GetRequest.transaction', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=267, serialized_end=352)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.cosmetic.market.transaction.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='status', full_name='eve_public.cosmetic.market.transaction.api.GetResponse.status', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=354, serialized_end=435)
_GETALLRESPONSE.fields_by_name['transactions'].message_type = eve__public_dot_cosmetic_dot_market_dot_transaction_dot_transaction__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['transaction'].message_type = eve__public_dot_cosmetic_dot_market_dot_transaction_dot_transaction__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['status'].message_type = eve__public_dot_cosmetic_dot_market_dot_transaction_dot_transaction__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve_public.cosmetic.market.transaction.api.api_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve_public.cosmetic.market.transaction.api.api_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.cosmetic.market.transaction.api.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.cosmetic.market.transaction.api.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
