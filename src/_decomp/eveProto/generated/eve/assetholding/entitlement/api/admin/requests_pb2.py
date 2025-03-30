#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\assetholding\entitlement\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.assetholding.entitlement import entitlement_pb2 as eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2
from eveProto.generated.eve.quasar.admin import admin_pb2 as eve_dot_quasar_dot_admin_dot_admin__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/assetholding/entitlement/api/admin/requests.proto', package='eve.assetholding.entitlement.api.admin', syntax='proto3', serialized_options='ZQgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/entitlement/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n5eve/assetholding/entitlement/api/admin/requests.proto\x12&eve.assetholding.entitlement.api.admin\x1a.eve/assetholding/entitlement/entitlement.proto\x1a\x1ceve/quasar/admin/admin.proto"z\n\rRedeemRequest\x12=\n\x0bentitlement\x18\x01 \x01(\x0b2(.eve.assetholding.entitlement.Identifier\x12*\n\x07context\x18\x02 \x01(\x0b2\x19.eve.quasar.admin.Context"\x10\n\x0eRedeemResponse"z\n\rExpireRequest\x12=\n\x0bentitlement\x18\x01 \x01(\x0b2(.eve.assetholding.entitlement.Identifier\x12*\n\x07context\x18\x02 \x01(\x0b2\x19.eve.quasar.admin.Context"\x10\n\x0eExpireResponse"?\n\x11AutoRedeemRequest\x12*\n\x07context\x18\x01 \x01(\x0b2\x19.eve.quasar.admin.Context"\x14\n\x12AutoRedeemResponseBSZQgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/entitlement/api/adminb\x06proto3', dependencies=[eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2.DESCRIPTOR, eve_dot_quasar_dot_admin_dot_admin__pb2.DESCRIPTOR])
_REDEEMREQUEST = _descriptor.Descriptor(name='RedeemRequest', full_name='eve.assetholding.entitlement.api.admin.RedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve.assetholding.entitlement.api.admin.RedeemRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='context', full_name='eve.assetholding.entitlement.api.admin.RedeemRequest.context', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=175, serialized_end=297)
_REDEEMRESPONSE = _descriptor.Descriptor(name='RedeemResponse', full_name='eve.assetholding.entitlement.api.admin.RedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=299, serialized_end=315)
_EXPIREREQUEST = _descriptor.Descriptor(name='ExpireRequest', full_name='eve.assetholding.entitlement.api.admin.ExpireRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve.assetholding.entitlement.api.admin.ExpireRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='context', full_name='eve.assetholding.entitlement.api.admin.ExpireRequest.context', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=317, serialized_end=439)
_EXPIRERESPONSE = _descriptor.Descriptor(name='ExpireResponse', full_name='eve.assetholding.entitlement.api.admin.ExpireResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=441, serialized_end=457)
_AUTOREDEEMREQUEST = _descriptor.Descriptor(name='AutoRedeemRequest', full_name='eve.assetholding.entitlement.api.admin.AutoRedeemRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.assetholding.entitlement.api.admin.AutoRedeemRequest.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=459, serialized_end=522)
_AUTOREDEEMRESPONSE = _descriptor.Descriptor(name='AutoRedeemResponse', full_name='eve.assetholding.entitlement.api.admin.AutoRedeemResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=524, serialized_end=544)
_REDEEMREQUEST.fields_by_name['entitlement'].message_type = eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
_REDEEMREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
_EXPIREREQUEST.fields_by_name['entitlement'].message_type = eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
_EXPIREREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
_AUTOREDEEMREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
DESCRIPTOR.message_types_by_name['RedeemRequest'] = _REDEEMREQUEST
DESCRIPTOR.message_types_by_name['RedeemResponse'] = _REDEEMRESPONSE
DESCRIPTOR.message_types_by_name['ExpireRequest'] = _EXPIREREQUEST
DESCRIPTOR.message_types_by_name['ExpireResponse'] = _EXPIRERESPONSE
DESCRIPTOR.message_types_by_name['AutoRedeemRequest'] = _AUTOREDEEMREQUEST
DESCRIPTOR.message_types_by_name['AutoRedeemResponse'] = _AUTOREDEEMRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
RedeemRequest = _reflection.GeneratedProtocolMessageType('RedeemRequest', (_message.Message,), {'DESCRIPTOR': _REDEEMREQUEST,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(RedeemRequest)
RedeemResponse = _reflection.GeneratedProtocolMessageType('RedeemResponse', (_message.Message,), {'DESCRIPTOR': _REDEEMRESPONSE,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(RedeemResponse)
ExpireRequest = _reflection.GeneratedProtocolMessageType('ExpireRequest', (_message.Message,), {'DESCRIPTOR': _EXPIREREQUEST,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(ExpireRequest)
ExpireResponse = _reflection.GeneratedProtocolMessageType('ExpireResponse', (_message.Message,), {'DESCRIPTOR': _EXPIRERESPONSE,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(ExpireResponse)
AutoRedeemRequest = _reflection.GeneratedProtocolMessageType('AutoRedeemRequest', (_message.Message,), {'DESCRIPTOR': _AUTOREDEEMREQUEST,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(AutoRedeemRequest)
AutoRedeemResponse = _reflection.GeneratedProtocolMessageType('AutoRedeemResponse', (_message.Message,), {'DESCRIPTOR': _AUTOREDEEMRESPONSE,
 '__module__': 'eve.assetholding.entitlement.api.admin.requests_pb2'})
_sym_db.RegisterMessage(AutoRedeemResponse)
DESCRIPTOR._options = None
