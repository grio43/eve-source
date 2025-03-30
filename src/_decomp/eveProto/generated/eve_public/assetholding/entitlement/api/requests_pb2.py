#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\assetholding\entitlement\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.assetholding.entitlement import entitlement_pb2 as eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/assetholding/entitlement/api/requests.proto', package='eve_public.assetholding.entitlement.api', syntax='proto3', serialized_options='ZRgithub.com/ccpgames/eve-proto-go/generated/eve_public/assetholding/entitlement/api', create_key=_descriptor._internal_create_key, serialized_pb='\n6eve_public/assetholding/entitlement/api/requests.proto\x12\'eve_public.assetholding.entitlement.api\x1a5eve_public/assetholding/entitlement/entitlement.proto"V\n\nGetRequest\x12D\n\x0bentitlement\x18\x01 \x01(\x0b2/.eve_public.assetholding.entitlement.Identifier:\x02\x18\x01"W\n\x0bGetResponse\x12D\n\x0bentitlement\x18\x02 \x01(\x0b2/.eve_public.assetholding.entitlement.Attributes:\x02\x18\x01"Y\n\rRedeemRequest\x12D\n\x0bentitlement\x18\x01 \x01(\x0b2/.eve_public.assetholding.entitlement.Identifier:\x02\x18\x01"\x14\n\x0eRedeemResponse:\x02\x18\x01BTZRgithub.com/ccpgames/eve-proto-go/generated/eve_public/assetholding/entitlement/apib\x06proto3', dependencies=[eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve_public.assetholding.entitlement.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.assetholding.entitlement.api.GetRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=154, serialized_end=240)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve_public.assetholding.entitlement.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.assetholding.entitlement.api.GetResponse.entitlement', index=0, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=242, serialized_end=329)
_REDEEMREQUEST = _descriptor.Descriptor(name='RedeemRequest', full_name='eve_public.assetholding.entitlement.api.RedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.assetholding.entitlement.api.RedeemRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=331, serialized_end=420)
_REDEEMRESPONSE = _descriptor.Descriptor(name='RedeemResponse', full_name='eve_public.assetholding.entitlement.api.RedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=422, serialized_end=442)
_GETREQUEST.fields_by_name['entitlement'].message_type = eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['entitlement'].message_type = eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2._ATTRIBUTES
_REDEEMREQUEST.fields_by_name['entitlement'].message_type = eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['RedeemRequest'] = _REDEEMREQUEST
DESCRIPTOR.message_types_by_name['RedeemResponse'] = _REDEEMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve_public.assetholding.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve_public.assetholding.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
RedeemRequest = _reflection.GeneratedProtocolMessageType('RedeemRequest', (_message.Message,), {'DESCRIPTOR': _REDEEMREQUEST,
 '__module__': 'eve_public.assetholding.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(RedeemRequest)
RedeemResponse = _reflection.GeneratedProtocolMessageType('RedeemResponse', (_message.Message,), {'DESCRIPTOR': _REDEEMRESPONSE,
 '__module__': 'eve_public.assetholding.entitlement.api.requests_pb2'})
_sym_db.RegisterMessage(RedeemResponse)
DESCRIPTOR._options = None
_GETREQUEST._options = None
_GETRESPONSE._options = None
_REDEEMREQUEST._options = None
_REDEEMRESPONSE._options = None
