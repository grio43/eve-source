#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\entitlement\user\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.entitlement.user import entitlement_pb2 as eve_dot_entitlement_dot_user_dot_entitlement__pb2
from eveProto.generated.eve.fulfillment.sale import sale_pb2 as eve_dot_fulfillment_dot_sale_dot_sale__pb2
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/entitlement/user/api.proto', package='eve.entitlement.user.api', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/user/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/entitlement/user/api.proto\x12\x18eve.entitlement.user.api\x1a&eve/entitlement/user/entitlement.proto\x1a\x1feve/fulfillment/sale/sale.proto\x1a\x19eve/payment/payment.proto"\xb8\x01\n\x0cGrantRequest\x12G\n\x1cuser_entitlement_fulfillment\x18\x01 \x01(\x0b2!.eve.entitlement.user.Entitlement\x12+\n\x0epayment_method\x18\x02 \x01(\x0e2\x13.eve.payment.Method\x12.\n\x04sale\x18\x03 \x01(\x0b2 .eve.fulfillment.sale.Identifier:\x02\x18\x01"\x13\n\rGrantResponse:\x02\x18\x01BEZCgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/user/apib\x06proto3', dependencies=[eve_dot_entitlement_dot_user_dot_entitlement__pb2.DESCRIPTOR, eve_dot_fulfillment_dot_sale_dot_sale__pb2.DESCRIPTOR, eve_dot_payment_dot_payment__pb2.DESCRIPTOR])
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve.entitlement.user.api.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user_entitlement_fulfillment', full_name='eve.entitlement.user.api.GrantRequest.user_entitlement_fulfillment', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='payment_method', full_name='eve.entitlement.user.api.GrantRequest.payment_method', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='sale', full_name='eve.entitlement.user.api.GrantRequest.sale', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=161, serialized_end=345)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve.entitlement.user.api.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=347, serialized_end=366)
_GRANTREQUEST.fields_by_name['user_entitlement_fulfillment'].message_type = eve_dot_entitlement_dot_user_dot_entitlement__pb2._ENTITLEMENT
_GRANTREQUEST.fields_by_name['payment_method'].enum_type = eve_dot_payment_dot_payment__pb2._METHOD
_GRANTREQUEST.fields_by_name['sale'].message_type = eve_dot_fulfillment_dot_sale_dot_sale__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve.entitlement.user.api_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve.entitlement.user.api_pb2'})
_sym_db.RegisterMessage(GrantResponse)
DESCRIPTOR._options = None
_GRANTREQUEST._options = None
_GRANTRESPONSE._options = None
