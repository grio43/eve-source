#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\entitlement\user\subscription\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.entitlement.user.subscription import subscription_pb2 as eve_dot_entitlement_dot_user_dot_subscription_dot_subscription__pb2
from eveProto.generated.eve.fulfillment.sale import sale_pb2 as eve_dot_fulfillment_dot_sale_dot_sale__pb2
from eveProto.generated.eve.payment import payment_pb2 as eve_dot_payment_dot_payment__pb2
from eveProto.generated.eve.store.sale import sale_pb2 as eve_dot_store_dot_sale_dot_sale__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/entitlement/user/subscription/api.proto', package='eve.entitlement.user.subscription.api', syntax='proto3', serialized_options='ZPgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/user/subscription/api', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/entitlement/user/subscription/api.proto\x12%eve.entitlement.user.subscription.api\x1a4eve/entitlement/user/subscription/subscription.proto\x1a\x1feve/fulfillment/sale/sale.proto\x1a\x19eve/payment/payment.proto\x1a\x19eve/store/sale/sale.proto"\xf2\x01\n\x0cGrantRequest\x12Q\n\x18subscription_fulfillment\x18\x01 \x01(\x0b2/.eve.entitlement.user.subscription.Subscription\x12+\n\x0epayment_method\x18\x02 \x01(\x0e2\x13.eve.payment.Method\x122\n\x04sale\x18\x03 \x01(\x0b2 .eve.fulfillment.sale.IdentifierB\x02\x18\x01\x12.\n\nstore_sale\x18\x04 \x01(\x0b2\x1a.eve.store.sale.Identifier"\x0f\n\rGrantResponseBRZPgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/user/subscription/apib\x06proto3', dependencies=[eve_dot_entitlement_dot_user_dot_subscription_dot_subscription__pb2.DESCRIPTOR,
 eve_dot_fulfillment_dot_sale_dot_sale__pb2.DESCRIPTOR,
 eve_dot_payment_dot_payment__pb2.DESCRIPTOR,
 eve_dot_store_dot_sale_dot_sale__pb2.DESCRIPTOR])
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve.entitlement.user.subscription.api.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='subscription_fulfillment', full_name='eve.entitlement.user.subscription.api.GrantRequest.subscription_fulfillment', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_method', full_name='eve.entitlement.user.subscription.api.GrantRequest.payment_method', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sale', full_name='eve.entitlement.user.subscription.api.GrantRequest.sale', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='store_sale', full_name='eve.entitlement.user.subscription.api.GrantRequest.store_sale', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=228, serialized_end=470)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve.entitlement.user.subscription.api.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=472, serialized_end=487)
_GRANTREQUEST.fields_by_name['subscription_fulfillment'].message_type = eve_dot_entitlement_dot_user_dot_subscription_dot_subscription__pb2._SUBSCRIPTION
_GRANTREQUEST.fields_by_name['payment_method'].enum_type = eve_dot_payment_dot_payment__pb2._METHOD
_GRANTREQUEST.fields_by_name['sale'].message_type = eve_dot_fulfillment_dot_sale_dot_sale__pb2._IDENTIFIER
_GRANTREQUEST.fields_by_name['store_sale'].message_type = eve_dot_store_dot_sale_dot_sale__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve.entitlement.user.subscription.api_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve.entitlement.user.subscription.api_pb2'})
_sym_db.RegisterMessage(GrantResponse)
DESCRIPTOR._options = None
_GRANTREQUEST.fields_by_name['sale']._options = None
