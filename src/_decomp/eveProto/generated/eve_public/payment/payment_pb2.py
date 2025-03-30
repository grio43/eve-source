#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\payment\payment_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/payment/payment.proto', package='eve_public.payment', syntax='proto3', serialized_options='Z=github.com/ccpgames/eve-proto-go/generated/eve_public/payment', create_key=_descriptor._internal_create_key, serialized_pb='\n eve_public/payment/payment.proto\x12\x12eve_public.payment" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"@\n\x05Money\x12\x15\n\rcurrency_code\x18\x01 \x01(\t\x12\r\n\x05units\x18\x02 \x01(\x03\x12\r\n\x05nanos\x18\x03 \x01(\x05:\x02\x18\x01*\xb9\x03\n\x06Method\x12\x12\n\x0ePM_UNSPECIFIED\x10\x00\x12\x12\n\x0ePM_CREDIT_CARD\x10\x01\x12\x11\n\rPM_DEBIT_CARD\x10\x02\x12\x13\n\x0fPM_STEAM_WALLET\x10\x03\x12\r\n\tPM_PAYPAL\x10\x04\x12\x13\n\x0fPM_DIRECT_DEBIT\x10\x05\x12\x10\n\x0cPM_WEB_MONEY\x10\x06\x12\x12\n\x0ePM_PAYSAFECARD\x10\x07\x12\r\n\tPM_YANDEX\x10\x08\x12\r\n\tPM_SOFORT\x10\t\x12\x0c\n\x08PM_IDEAL\x10\n\x12\x0c\n\x08PM_TOKEN\x10\x0b\x12\x0c\n\x07PM_GIFT\x10\xc9\x01\x12\x17\n\x12PM_CODE_REDEMPTION\x10\xca\x01\x12\x18\n\x13PM_IN_GAME_CURRENCY\x10\xcb\x01\x12\x19\n\x14PM_RECRUITMENT_AWARD\x10\xcc\x01\x12\x16\n\x11PM_MEET_AND_GREET\x10\xcd\x01\x12\x15\n\x10PM_SURVEY_REWARD\x10\xce\x01\x12\r\n\x08PM_STEAM\x10\xad\x02\x12\x0e\n\tPM_AMAZON\x10\xae\x02\x12\x0e\n\tPM_TWITCH\x10\xb1\x02\x12\x11\n\x0cPM_EPICSTORE\x10\xb2\x02\x12\x0e\n\tPM_REWARD\x10\xb3\x02B?Z=github.com/ccpgames/eve-proto-go/generated/eve_public/paymentb\x06proto3')
_METHOD = _descriptor.EnumDescriptor(name='Method', full_name='eve_public.payment.Method', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='PM_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
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
 _descriptor.EnumValueDescriptor(name='PM_GIFT', index=12, number=201, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_CODE_REDEMPTION', index=13, number=202, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_IN_GAME_CURRENCY', index=14, number=203, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_RECRUITMENT_AWARD', index=15, number=204, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_MEET_AND_GREET', index=16, number=205, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_SURVEY_REWARD', index=17, number=206, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_STEAM', index=18, number=301, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_AMAZON', index=19, number=302, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_TWITCH', index=20, number=305, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_EPICSTORE', index=21, number=306, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PM_REWARD', index=22, number=307, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=157, serialized_end=598)
_sym_db.RegisterEnumDescriptor(_METHOD)
Method = enum_type_wrapper.EnumTypeWrapper(_METHOD)
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
PM_GIFT = 201
PM_CODE_REDEMPTION = 202
PM_IN_GAME_CURRENCY = 203
PM_RECRUITMENT_AWARD = 204
PM_MEET_AND_GREET = 205
PM_SURVEY_REWARD = 206
PM_STEAM = 301
PM_AMAZON = 302
PM_TWITCH = 305
PM_EPICSTORE = 306
PM_REWARD = 307
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.payment.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve_public.payment.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=56, serialized_end=88)
_MONEY = _descriptor.Descriptor(name='Money', full_name='eve_public.payment.Money', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='currency_code', full_name='eve_public.payment.Money.currency_code', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='units', full_name='eve_public.payment.Money.units', index=1, number=2, type=3, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve_public.payment.Money.nanos', index=2, number=3, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=90, serialized_end=154)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Money'] = _MONEY
DESCRIPTOR.enum_types_by_name['Method'] = _METHOD
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.payment.payment_pb2'})
_sym_db.RegisterMessage(Identifier)
Money = _reflection.GeneratedProtocolMessageType('Money', (_message.Message,), {'DESCRIPTOR': _MONEY,
 '__module__': 'eve_public.payment.payment_pb2'})
_sym_db.RegisterMessage(Money)
DESCRIPTOR._options = None
_MONEY._options = None
