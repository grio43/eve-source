#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\assetholding\entitlement\api\admin\admin_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.assetholding.entitlement import entitlement_pb2 as eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/assetholding/entitlement/api/admin/admin.proto', package='eve_public.assetholding.entitlement.api.admin', syntax='proto3', serialized_options='ZXgithub.com/ccpgames/eve-proto-go/generated/eve_public/assetholding/entitlement/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n9eve_public/assetholding/entitlement/api/admin/admin.proto\x12-eve_public.assetholding.entitlement.api.admin\x1a5eve_public/assetholding/entitlement/entitlement.proto"Y\n\rExpireRequest\x12D\n\x0bentitlement\x18\x01 \x01(\x0b2/.eve_public.assetholding.entitlement.Identifier:\x02\x18\x01"\x14\n\x0eExpireResponse:\x02\x18\x01"\x17\n\x11AutoRedeemRequest:\x02\x18\x01"\x18\n\x12AutoRedeemResponse:\x02\x18\x01BZZXgithub.com/ccpgames/eve-proto-go/generated/eve_public/assetholding/entitlement/api/adminb\x06proto3', dependencies=[eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2.DESCRIPTOR])
_EXPIREREQUEST = _descriptor.Descriptor(name='ExpireRequest', full_name='eve_public.assetholding.entitlement.api.admin.ExpireRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.assetholding.entitlement.api.admin.ExpireRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=163, serialized_end=252)
_EXPIRERESPONSE = _descriptor.Descriptor(name='ExpireResponse', full_name='eve_public.assetholding.entitlement.api.admin.ExpireResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=254, serialized_end=274)
_AUTOREDEEMREQUEST = _descriptor.Descriptor(name='AutoRedeemRequest', full_name='eve_public.assetholding.entitlement.api.admin.AutoRedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=276, serialized_end=299)
_AUTOREDEEMRESPONSE = _descriptor.Descriptor(name='AutoRedeemResponse', full_name='eve_public.assetholding.entitlement.api.admin.AutoRedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=301, serialized_end=325)
_EXPIREREQUEST.fields_by_name['entitlement'].message_type = eve__public_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ExpireRequest'] = _EXPIREREQUEST
DESCRIPTOR.message_types_by_name['ExpireResponse'] = _EXPIRERESPONSE
DESCRIPTOR.message_types_by_name['AutoRedeemRequest'] = _AUTOREDEEMREQUEST
DESCRIPTOR.message_types_by_name['AutoRedeemResponse'] = _AUTOREDEEMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ExpireRequest = _reflection.GeneratedProtocolMessageType('ExpireRequest', (_message.Message,), {'DESCRIPTOR': _EXPIREREQUEST,
 '__module__': 'eve_public.assetholding.entitlement.api.admin.admin_pb2'})
_sym_db.RegisterMessage(ExpireRequest)
ExpireResponse = _reflection.GeneratedProtocolMessageType('ExpireResponse', (_message.Message,), {'DESCRIPTOR': _EXPIRERESPONSE,
 '__module__': 'eve_public.assetholding.entitlement.api.admin.admin_pb2'})
_sym_db.RegisterMessage(ExpireResponse)
AutoRedeemRequest = _reflection.GeneratedProtocolMessageType('AutoRedeemRequest', (_message.Message,), {'DESCRIPTOR': _AUTOREDEEMREQUEST,
 '__module__': 'eve_public.assetholding.entitlement.api.admin.admin_pb2'})
_sym_db.RegisterMessage(AutoRedeemRequest)
AutoRedeemResponse = _reflection.GeneratedProtocolMessageType('AutoRedeemResponse', (_message.Message,), {'DESCRIPTOR': _AUTOREDEEMRESPONSE,
 '__module__': 'eve_public.assetholding.entitlement.api.admin.admin_pb2'})
_sym_db.RegisterMessage(AutoRedeemResponse)
DESCRIPTOR._options = None
_EXPIREREQUEST._options = None
_EXPIRERESPONSE._options = None
_AUTOREDEEMREQUEST._options = None
_AUTOREDEEMRESPONSE._options = None
