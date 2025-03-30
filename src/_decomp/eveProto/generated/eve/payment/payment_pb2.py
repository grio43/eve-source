#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\payment\payment_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.payment.merchant import merchant_pb2 as eve_dot_payment_dot_merchant_dot_merchant__pb2
from eveProto.generated.eve.vendors.ingenico.api import ingenico_pb2 as eve_dot_vendors_dot_ingenico_dot_api_dot_ingenico__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/payment/payment.proto', package='eve.payment', syntax='proto3', serialized_options='Z6github.com/ccpgames/eve-proto-go/generated/eve/payment', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/payment/payment.proto\x12\x0beve.payment\x1a#eve/payment/merchant/merchant.proto\x1a\'eve/vendors/ingenico/api/ingenico.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\\\n\nIdentifier\x12\x19\n\x11payment_reference\x18\x01 \x01(\t\x123\n\x10payment_provider\x18\x02 \x01(\x0e2\x15.eve.payment.ProviderB\x02\x18\x01"\xc7\x02\n\nAttributes\x12\x17\n\x0famount_in_cents\x18\x01 \x01(\x03\x12\x10\n\x08currency\x18\x02 \x01(\t\x12+\n\x0epayment_method\x18\x03 \x01(\x0e2\x13.eve.payment.Method\x125\n\x11payment_timestamp\x18\x04 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x1a\n\x10unknown_tax_rate\x18\x05 \x01(\x08H\x00\x12(\n\x08tax_rate\x18\x06 \x01(\x0b2\x14.eve.payment.TaxRateH\x00\x12#\n\x06status\x18\x07 \x01(\x0e2\x13.eve.payment.Status\x12/\n\x10payment_provider\x18\x08 \x01(\x0e2\x15.eve.payment.ProviderB\x0e\n\x0chas_tax_rate"\\\n\x07TaxRate\x12\x17\n\x0famount_in_cents\x18\x01 \x01(\x03\x12!\n\x19percentage_of_total_value\x18\x02 \x01(\x01\x12\x15\n\rtaxable_cents\x18\x03 \x01(\x03"\xed\x01\n\x07Details\x122\n\x08merchant\x18\x01 \x01(\x0b2 .eve.payment.merchant.Identifier\x12\x11\n\trecurring\x18\x02 \x01(\x08\x12\x11\n\tsensitive\x18\x03 \x01(\x08\x12\x13\n\x0bdescription\x18\x04 \x01(\t\x12*\n\nfraud_risk\x18\x05 \x01(\x0e2\x16.eve.payment.FraudRisk\x12\x0f\n\x07user_ip\x18\x06 \x01(\t\x126\n\x08ingenico\x18\x07 \x01(\x0b2$.eve.vendors.ingenico.api.Attributes"@\n\x05Money\x12\x15\n\rcurrency_code\x18\x01 \x01(\t\x12\r\n\x05units\x18\x02 \x01(\x03\x12\r\n\x05nanos\x18\x03 \x01(\x05:\x02\x18\x01*\x9f\x04\n\x06Method\x12\x12\n\x0ePM_UNSPECIFIED\x10\x00\x12\x12\n\x0ePM_CREDIT_CARD\x10\x01\x12\x11\n\rPM_DEBIT_CARD\x10\x02\x12\x13\n\x0fPM_STEAM_WALLET\x10\x03\x12\r\n\tPM_PAYPAL\x10\x04\x12\x13\n\x0fPM_DIRECT_DEBIT\x10\x05\x12\x10\n\x0cPM_WEB_MONEY\x10\x06\x12\x12\n\x0ePM_PAYSAFECARD\x10\x07\x12\r\n\tPM_YANDEX\x10\x08\x12\r\n\tPM_SOFORT\x10\t\x12\x0c\n\x08PM_IDEAL\x10\n\x12\x0c\n\x08PM_TOKEN\x10\x0b\x12\r\n\tPM_ALIPAY\x10e\x12\x10\n\x0cPM_ALIPAY_QR\x10f\x12\x10\n\x0cPM_WECHAT_QR\x10g\x12\x13\n\x0fPM_WEIXINPAY_QR\x10h\x12\x0c\n\x07PM_GIFT\x10\xc9\x01\x12\x17\n\x12PM_CODE_REDEMPTION\x10\xca\x01\x12\x18\n\x13PM_IN_GAME_CURRENCY\x10\xcb\x01\x12\x19\n\x14PM_RECRUITMENT_AWARD\x10\xcc\x01\x12\x16\n\x11PM_MEET_AND_GREET\x10\xcd\x01\x12\x15\n\x10PM_SURVEY_REWARD\x10\xce\x01\x12\r\n\x08PM_STEAM\x10\xad\x02\x12\x0e\n\tPM_AMAZON\x10\xae\x02\x12\x0c\n\x07PM_SONY\x10\xaf\x02\x12\x0e\n\tPM_OCULUS\x10\xb0\x02\x12\x0e\n\tPM_TWITCH\x10\xb1\x02\x12\x11\n\x0cPM_EPICSTORE\x10\xb2\x02\x12\x0e\n\tPM_REWARD\x10\xb3\x02*\xc2\x01\n\x08Provider\x12\x12\n\x0ePP_UNSPECIFIED\x10\x00\x12\x0f\n\x0bPP_INGENICO\x10\x01\x12\x0c\n\x08PP_STEAM\x10\x02\x12\r\n\tPP_AMAZON\x10\x03\x12\x0b\n\x07PP_SONY\x10\x04\x12\r\n\tPP_OCULUS\x10\x05\x12\x0e\n\nPP_NETEASE\x10\x06\x12\x10\n\x0cPP_BRAINTREE\x10\x07\x12\r\n\tPP_TWITCH\x10\x08\x12\x15\n\x11PP_MEET_AND_GREET\x10\t\x12\x10\n\x0cPP_EPICSTORE\x10\n*U\n\tFraudRisk\x12\x12\n\x0ePF_UNSPECIFIED\x10\x00\x12\x0e\n\nPF_NO_RISK\x10\x01\x12\x12\n\x0ePF_MEDIUM_RISK\x10\x02\x12\x10\n\x0cPF_HIGH_RISK\x10\x03*\xe2\x03\n\x06Status\x12\x12\n\x0ePS_UNSPECIFIED\x10\x00\x12\n\n\x06PS_NEW\x10\x01\x12\x10\n\x0cPS_VALIDATED\x10\x02\x12\x0e\n\nPS_STARTED\x10\x03\x12\r\n\tPS_FAILED\x10\x04\x12\x0c\n\x08PS_ERROR\x10\x05\x12\x16\n\x12PS_PENDING_PAYMENT\x10\x06\x12\x0b\n\x07PS_PAID\x10\x07\x12\x15\n\x11PS_PENDING_REFUND\x10\x08\x12\x0f\n\x0bPS_REFUNDED\x10\t\x12\x1c\n\x18PS_PENDING_AND_ACTIVATED\x10\n\x12\x17\n\x13PS_REVERSED_PAYMENT\x10\x0b\x12\x18\n\x14PS_CANCELLED_PAYMENT\x10\x0c\x12\x11\n\rPS_CHARGEBACK\x10\r\x12\x19\n\x15PS_PENDING_CHARGEBACK\x10\x0e\x12\x18\n\x14PS_CONNECTION_FAILED\x10\x0f\x12\x1c\n\x18PS_PENDING_AUTHORIZATION\x10\x10\x12\x15\n\x11PS_PAID_COMPLETED\x10\x11\x12\x1c\n\x18PS_PAID_PENDING_DELIVERY\x10\x12\x12\x16\n\x12PS_CANCELED_REFUND\x10\x13\x12\x10\n\x0cPS_TIMED_OUT\x10\x14\x12\x16\n\x12PS_REJECTED_REFUND\x10\x15B8Z6github.com/ccpgames/eve-proto-go/generated/eve/paymentb\x06proto3', dependencies=[eve_dot_payment_dot_merchant_dot_merchant__pb2.DESCRIPTOR, eve_dot_vendors_dot_ingenico_dot_api_dot_ingenico__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_METHOD = _descriptor.EnumDescriptor(name='Method', full_name='eve.payment.Method', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PM_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_CREDIT_CARD', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_DEBIT_CARD', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_STEAM_WALLET', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_PAYPAL', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_DIRECT_DEBIT', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_WEB_MONEY', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_PAYSAFECARD', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_YANDEX', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_SOFORT', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_IDEAL', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_TOKEN', index=11, number=11, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_ALIPAY', index=12, number=101, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_ALIPAY_QR', index=13, number=102, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_WECHAT_QR', index=14, number=103, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_WEIXINPAY_QR', index=15, number=104, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_GIFT', index=16, number=201, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_CODE_REDEMPTION', index=17, number=202, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_IN_GAME_CURRENCY', index=18, number=203, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_RECRUITMENT_AWARD', index=19, number=204, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_MEET_AND_GREET', index=20, number=205, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_SURVEY_REWARD', index=21, number=206, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_STEAM', index=22, number=301, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_AMAZON', index=23, number=302, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_SONY', index=24, number=303, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_OCULUS', index=25, number=304, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_TWITCH', index=26, number=305, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_EPICSTORE', index=27, number=306, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_REWARD', index=28, number=307, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=978, serialized_end=1521)
_sym_db.RegisterEnumDescriptor(_METHOD)
Method = enum_type_wrapper.EnumTypeWrapper(_METHOD)
_PROVIDER = _descriptor.EnumDescriptor(name='Provider', full_name='eve.payment.Provider', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PP_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_INGENICO', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_STEAM', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_AMAZON', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_SONY', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_OCULUS', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_NETEASE', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_BRAINTREE', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_TWITCH', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_MEET_AND_GREET', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PP_EPICSTORE', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1524, serialized_end=1718)
_sym_db.RegisterEnumDescriptor(_PROVIDER)
Provider = enum_type_wrapper.EnumTypeWrapper(_PROVIDER)
_FRAUDRISK = _descriptor.EnumDescriptor(name='FraudRisk', full_name='eve.payment.FraudRisk', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PF_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PF_NO_RISK', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PF_MEDIUM_RISK', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PF_HIGH_RISK', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1720, serialized_end=1805)
_sym_db.RegisterEnumDescriptor(_FRAUDRISK)
FraudRisk = enum_type_wrapper.EnumTypeWrapper(_FRAUDRISK)
_STATUS = _descriptor.EnumDescriptor(name='Status', full_name='eve.payment.Status', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PS_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_NEW', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_VALIDATED', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_STARTED', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_FAILED', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_ERROR', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PENDING_PAYMENT', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PAID', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PENDING_REFUND', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_REFUNDED', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PENDING_AND_ACTIVATED', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_REVERSED_PAYMENT', index=11, number=11, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_CANCELLED_PAYMENT', index=12, number=12, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_CHARGEBACK', index=13, number=13, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PENDING_CHARGEBACK', index=14, number=14, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_CONNECTION_FAILED', index=15, number=15, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PENDING_AUTHORIZATION', index=16, number=16, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PAID_COMPLETED', index=17, number=17, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_PAID_PENDING_DELIVERY', index=18, number=18, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_CANCELED_REFUND', index=19, number=19, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_TIMED_OUT', index=20, number=20, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PS_REJECTED_REFUND', index=21, number=21, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1808, serialized_end=2290)
_sym_db.RegisterEnumDescriptor(_STATUS)
Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
PM_UNSPECIFIED = 0
PM_CREDIT_CARD = 1
PM_DEBIT_CARD = 2
PM_STEAM_WALLET = 3
PM_PAYPAL = 4
PM_DIRECT_DEBIT = 5
PM_WEB_MONEY = 6
PM_PAYSAFECARD = 7
PM_YANDEX = 8
PM_SOFORT = 9
PM_IDEAL = 10
PM_TOKEN = 11
PM_ALIPAY = 101
PM_ALIPAY_QR = 102
PM_WECHAT_QR = 103
PM_WEIXINPAY_QR = 104
PM_GIFT = 201
PM_CODE_REDEMPTION = 202
PM_IN_GAME_CURRENCY = 203
PM_RECRUITMENT_AWARD = 204
PM_MEET_AND_GREET = 205
PM_SURVEY_REWARD = 206
PM_STEAM = 301
PM_AMAZON = 302
PM_SONY = 303
PM_OCULUS = 304
PM_TWITCH = 305
PM_EPICSTORE = 306
PM_REWARD = 307
PP_UNSPECIFIED = 0
PP_INGENICO = 1
PP_STEAM = 2
PP_AMAZON = 3
PP_SONY = 4
PP_OCULUS = 5
PP_NETEASE = 6
PP_BRAINTREE = 7
PP_TWITCH = 8
PP_MEET_AND_GREET = 9
PP_EPICSTORE = 10
PF_UNSPECIFIED = 0
PF_NO_RISK = 1
PF_MEDIUM_RISK = 2
PF_HIGH_RISK = 3
PS_UNSPECIFIED = 0
PS_NEW = 1
PS_VALIDATED = 2
PS_STARTED = 3
PS_FAILED = 4
PS_ERROR = 5
PS_PENDING_PAYMENT = 6
PS_PAID = 7
PS_PENDING_REFUND = 8
PS_REFUNDED = 9
PS_PENDING_AND_ACTIVATED = 10
PS_REVERSED_PAYMENT = 11
PS_CANCELLED_PAYMENT = 12
PS_CHARGEBACK = 13
PS_PENDING_CHARGEBACK = 14
PS_CONNECTION_FAILED = 15
PS_PENDING_AUTHORIZATION = 16
PS_PAID_COMPLETED = 17
PS_PAID_PENDING_DELIVERY = 18
PS_CANCELED_REFUND = 19
PS_TIMED_OUT = 20
PS_REJECTED_REFUND = 21
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.payment.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='payment_reference', full_name='eve.payment.Identifier.payment_reference', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='payment_provider', full_name='eve.payment.Identifier.payment_provider', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=153, serialized_end=245)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.payment.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount_in_cents', full_name='eve.payment.Attributes.amount_in_cents', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='currency', full_name='eve.payment.Attributes.currency', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_method', full_name='eve.payment.Attributes.payment_method', index=2, number=3, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_timestamp', full_name='eve.payment.Attributes.payment_timestamp', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unknown_tax_rate', full_name='eve.payment.Attributes.unknown_tax_rate', index=4, number=5, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='tax_rate', full_name='eve.payment.Attributes.tax_rate', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='status', full_name='eve.payment.Attributes.status', index=6, number=7, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='payment_provider', full_name='eve.payment.Attributes.payment_provider', index=7, number=8, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='has_tax_rate', full_name='eve.payment.Attributes.has_tax_rate', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=248, serialized_end=575)
_TAXRATE = _descriptor.Descriptor(name='TaxRate', full_name='eve.payment.TaxRate', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount_in_cents', full_name='eve.payment.TaxRate.amount_in_cents', index=0, number=1, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='percentage_of_total_value', full_name='eve.payment.TaxRate.percentage_of_total_value', index=1, number=2, type=1, cpp_type=5, label=1, has_default_value=False, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='taxable_cents', full_name='eve.payment.TaxRate.taxable_cents', index=2, number=3, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=577, serialized_end=669)
_DETAILS = _descriptor.Descriptor(name='Details', full_name='eve.payment.Details', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='merchant', full_name='eve.payment.Details.merchant', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recurring', full_name='eve.payment.Details.recurring', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='sensitive', full_name='eve.payment.Details.sensitive', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.payment.Details.description', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='fraud_risk', full_name='eve.payment.Details.fraud_risk', index=4, number=5, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='user_ip', full_name='eve.payment.Details.user_ip', index=5, number=6, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ingenico', full_name='eve.payment.Details.ingenico', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=672, serialized_end=909)
_MONEY = _descriptor.Descriptor(name='Money', full_name='eve.payment.Money', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='currency_code', full_name='eve.payment.Money.currency_code', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='units', full_name='eve.payment.Money.units', index=1, number=2, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve.payment.Money.nanos', index=2, number=3, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=911, serialized_end=975)
_IDENTIFIER.fields_by_name['payment_provider'].enum_type = _PROVIDER
_ATTRIBUTES.fields_by_name['payment_method'].enum_type = _METHOD
_ATTRIBUTES.fields_by_name['payment_timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['tax_rate'].message_type = _TAXRATE
_ATTRIBUTES.fields_by_name['status'].enum_type = _STATUS
_ATTRIBUTES.fields_by_name['payment_provider'].enum_type = _PROVIDER
_ATTRIBUTES.oneofs_by_name['has_tax_rate'].fields.append(_ATTRIBUTES.fields_by_name['unknown_tax_rate'])
_ATTRIBUTES.fields_by_name['unknown_tax_rate'].containing_oneof = _ATTRIBUTES.oneofs_by_name['has_tax_rate']
_ATTRIBUTES.oneofs_by_name['has_tax_rate'].fields.append(_ATTRIBUTES.fields_by_name['tax_rate'])
_ATTRIBUTES.fields_by_name['tax_rate'].containing_oneof = _ATTRIBUTES.oneofs_by_name['has_tax_rate']
_DETAILS.fields_by_name['merchant'].message_type = eve_dot_payment_dot_merchant_dot_merchant__pb2._IDENTIFIER
_DETAILS.fields_by_name['fraud_risk'].enum_type = _FRAUDRISK
_DETAILS.fields_by_name['ingenico'].message_type = eve_dot_vendors_dot_ingenico_dot_api_dot_ingenico__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['TaxRate'] = _TAXRATE
DESCRIPTOR.message_types_by_name['Details'] = _DETAILS
DESCRIPTOR.message_types_by_name['Money'] = _MONEY
DESCRIPTOR.enum_types_by_name['Method'] = _METHOD
DESCRIPTOR.enum_types_by_name['Provider'] = _PROVIDER
DESCRIPTOR.enum_types_by_name['FraudRisk'] = _FRAUDRISK
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.payment.payment_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.payment.payment_pb2'})
_sym_db.RegisterMessage(Attributes)
TaxRate = _reflection.GeneratedProtocolMessageType('TaxRate', (_message.Message,), {'DESCRIPTOR': _TAXRATE,
 '__module__': 'eve.payment.payment_pb2'})
_sym_db.RegisterMessage(TaxRate)
Details = _reflection.GeneratedProtocolMessageType('Details', (_message.Message,), {'DESCRIPTOR': _DETAILS,
 '__module__': 'eve.payment.payment_pb2'})
_sym_db.RegisterMessage(Details)
Money = _reflection.GeneratedProtocolMessageType('Money', (_message.Message,), {'DESCRIPTOR': _MONEY,
 '__module__': 'eve.payment.payment_pb2'})
_sym_db.RegisterMessage(Money)
DESCRIPTOR._options = None
_IDENTIFIER.fields_by_name['payment_provider']._options = None
_MONEY._options = None
