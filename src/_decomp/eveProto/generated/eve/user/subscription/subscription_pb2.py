#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\subscription\subscription_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.payment.customer import customer_pb2 as eve_dot_payment_dot_customer_dot_customer__pb2
from eveProto.generated.eve.store.offer import offer_pb2 as eve_dot_store_dot_offer_dot_offer__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/subscription/subscription.proto', package='eve.user.subscription', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/user/subscription', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve/user/subscription/subscription.proto\x12\x15eve.user.subscription\x1a#eve/payment/customer/customer.proto\x1a\x1beve/store/offer/offer.proto\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto"9\n\x0fGetStateRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier:\x02\x18\x01"T\n\x10GetStateResponse\x12<\n\x0csubscription\x18\x01 \x01(\x0e2&.eve.user.subscription.DeprecatedState:\x02\x18\x01"v\n\x13SubscriptionStarted\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x127\n\x13current_expiry_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp:\x02\x18\x01";\n\x11SubscriptionEnded\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier:\x02\x18\x01"\xb1\x01\n\x14SubscriptionExtended\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x128\n\x14previous_expiry_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x127\n\x13current_expiry_date\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp:\x02\x18\x01" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x03"\xb8\x02\n\nAttributes\x12-\n\x06status\x18\x01 \x01(\x0e2\x1d.eve.user.subscription.Status\x12.\n\nstart_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12"\n\x04user\x18\x03 \x01(\x0b2\x14.eve.user.Identifier\x122\n\x08customer\x18\x04 \x01(\x0b2 .eve.payment.customer.Identifier\x12*\n\x05offer\x18\x05 \x01(\x0b2\x1b.eve.store.offer.Identifier\x125\n\x11last_payment_date\x18\x06 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x10\n\x08currency\x18\x07 \x01(\t*+\n\x0fDeprecatedState\x12\x08\n\x04FREE\x10\x00\x12\x0e\n\nSUBSCRIBED\x10\x01*D\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x0e\n\nSTATE_FREE\x10\x01\x12\x14\n\x10STATE_SUBSCRIBED\x10\x02*\x9e\x01\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\x0e\n\nSTATUS_NEW\x10\x01\x12\x11\n\rSTATUS_ACTIVE\x10\x02\x12\x14\n\x10STATUS_SUSPENDED\x10\x03\x12\x11\n\rSTATUS_CLOSED\x10\x04\x12\x14\n\x10STATUS_CANCELLED\x10\x05\x12\x1a\n\x16STATUS_RECURRING_RETRY\x10\x06BBZ@github.com/ccpgames/eve-proto-go/generated/eve/user/subscriptionb\x06proto3', dependencies=[eve_dot_payment_dot_customer_dot_customer__pb2.DESCRIPTOR,
 eve_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_DEPRECATEDSTATE = _descriptor.EnumDescriptor(name='DeprecatedState', full_name='eve.user.subscription.DeprecatedState', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='FREE', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='SUBSCRIBED', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1042, serialized_end=1085)
_sym_db.RegisterEnumDescriptor(_DEPRECATEDSTATE)
DeprecatedState = enum_type_wrapper.EnumTypeWrapper(_DEPRECATEDSTATE)
_STATE = _descriptor.EnumDescriptor(name='State', full_name='eve.user.subscription.State', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='STATE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='STATE_FREE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='STATE_SUBSCRIBED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1087, serialized_end=1155)
_sym_db.RegisterEnumDescriptor(_STATE)
State = enum_type_wrapper.EnumTypeWrapper(_STATE)
_STATUS = _descriptor.EnumDescriptor(name='Status', full_name='eve.user.subscription.Status', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='STATUS_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_NEW', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_ACTIVE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_SUSPENDED', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_CLOSED', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_CANCELLED', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATUS_RECURRING_RETRY', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1158, serialized_end=1316)
_sym_db.RegisterEnumDescriptor(_STATUS)
Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
FREE = 0
SUBSCRIBED = 1
STATE_UNSPECIFIED = 0
STATE_FREE = 1
STATE_SUBSCRIBED = 2
STATUS_UNSPECIFIED = 0
STATUS_NEW = 1
STATUS_ACTIVE = 2
STATUS_SUSPENDED = 3
STATUS_CLOSED = 4
STATUS_CANCELLED = 5
STATUS_RECURRING_RETRY = 6
_GETSTATEREQUEST = _descriptor.Descriptor(name='GetStateRequest', full_name='eve.user.subscription.GetStateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.subscription.GetStateRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=187, serialized_end=244)
_GETSTATERESPONSE = _descriptor.Descriptor(name='GetStateResponse', full_name='eve.user.subscription.GetStateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='subscription', full_name='eve.user.subscription.GetStateResponse.subscription', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=246, serialized_end=330)
_SUBSCRIPTIONSTARTED = _descriptor.Descriptor(name='SubscriptionStarted', full_name='eve.user.subscription.SubscriptionStarted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.subscription.SubscriptionStarted.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='current_expiry_date', full_name='eve.user.subscription.SubscriptionStarted.current_expiry_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=332, serialized_end=450)
_SUBSCRIPTIONENDED = _descriptor.Descriptor(name='SubscriptionEnded', full_name='eve.user.subscription.SubscriptionEnded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.subscription.SubscriptionEnded.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=452, serialized_end=511)
_SUBSCRIPTIONEXTENDED = _descriptor.Descriptor(name='SubscriptionExtended', full_name='eve.user.subscription.SubscriptionExtended', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.subscription.SubscriptionExtended.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='previous_expiry_date', full_name='eve.user.subscription.SubscriptionExtended.previous_expiry_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='current_expiry_date', full_name='eve.user.subscription.SubscriptionExtended.current_expiry_date', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=514, serialized_end=691)
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.user.subscription.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.user.subscription.Identifier.sequential', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=693, serialized_end=725)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.user.subscription.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='status', full_name='eve.user.subscription.Attributes.status', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='start_date', full_name='eve.user.subscription.Attributes.start_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user', full_name='eve.user.subscription.Attributes.user', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='customer', full_name='eve.user.subscription.Attributes.customer', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='offer', full_name='eve.user.subscription.Attributes.offer', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_payment_date', full_name='eve.user.subscription.Attributes.last_payment_date', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='currency', full_name='eve.user.subscription.Attributes.currency', index=6, number=7, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=728, serialized_end=1040)
_GETSTATEREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETSTATERESPONSE.fields_by_name['subscription'].enum_type = _DEPRECATEDSTATE
_SUBSCRIPTIONSTARTED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_SUBSCRIPTIONSTARTED.fields_by_name['current_expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_SUBSCRIPTIONENDED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_SUBSCRIPTIONEXTENDED.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_SUBSCRIPTIONEXTENDED.fields_by_name['previous_expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_SUBSCRIPTIONEXTENDED.fields_by_name['current_expiry_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['status'].enum_type = _STATUS
_ATTRIBUTES.fields_by_name['start_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['customer'].message_type = eve_dot_payment_dot_customer_dot_customer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['offer'].message_type = eve_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['last_payment_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['GetStateRequest'] = _GETSTATEREQUEST
DESCRIPTOR.message_types_by_name['GetStateResponse'] = _GETSTATERESPONSE
DESCRIPTOR.message_types_by_name['SubscriptionStarted'] = _SUBSCRIPTIONSTARTED
DESCRIPTOR.message_types_by_name['SubscriptionEnded'] = _SUBSCRIPTIONENDED
DESCRIPTOR.message_types_by_name['SubscriptionExtended'] = _SUBSCRIPTIONEXTENDED
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['DeprecatedState'] = _DEPRECATEDSTATE
DESCRIPTOR.enum_types_by_name['State'] = _STATE
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetStateRequest = _reflection.GeneratedProtocolMessageType('GetStateRequest', (_message.Message,), {'DESCRIPTOR': _GETSTATEREQUEST,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(GetStateRequest)
GetStateResponse = _reflection.GeneratedProtocolMessageType('GetStateResponse', (_message.Message,), {'DESCRIPTOR': _GETSTATERESPONSE,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(GetStateResponse)
SubscriptionStarted = _reflection.GeneratedProtocolMessageType('SubscriptionStarted', (_message.Message,), {'DESCRIPTOR': _SUBSCRIPTIONSTARTED,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(SubscriptionStarted)
SubscriptionEnded = _reflection.GeneratedProtocolMessageType('SubscriptionEnded', (_message.Message,), {'DESCRIPTOR': _SUBSCRIPTIONENDED,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(SubscriptionEnded)
SubscriptionExtended = _reflection.GeneratedProtocolMessageType('SubscriptionExtended', (_message.Message,), {'DESCRIPTOR': _SUBSCRIPTIONEXTENDED,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(SubscriptionExtended)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.user.subscription.subscription_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
_GETSTATEREQUEST._options = None
_GETSTATERESPONSE._options = None
_SUBSCRIPTIONSTARTED._options = None
_SUBSCRIPTIONENDED._options = None
_SUBSCRIPTIONEXTENDED._options = None
