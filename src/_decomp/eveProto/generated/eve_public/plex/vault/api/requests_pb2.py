#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\plex\vault\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.character import character_pb2 as eve__public_dot_character_dot_character__pb2
from eveProto.generated.eve_public.plex import plex_pb2 as eve__public_dot_plex_dot_plex__pb2
from eveProto.generated.eve_public.store.offer import offer_pb2 as eve__public_dot_store_dot_offer_dot_offer__pb2
from eveProto.generated.eve_public.user import user_pb2 as eve__public_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/plex/vault/api/requests.proto', package='eve_public.plex.vault.api', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve_public/plex/vault/api', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve_public/plex/vault/api/requests.proto\x12\x19eve_public.plex.vault.api\x1a$eve_public/character/character.proto\x1a\x1aeve_public/plex/plex.proto\x1a"eve_public/store/offer/offer.proto\x1a\x1aeve_public/user/user.proto"\x10\n\x0eBalanceRequest"=\n\x0fBalanceResponse\x12*\n\x07balance\x18\x01 \x01(\x0b2\x19.eve_public.plex.Currency"\xdb\x02\n\x0fPurchaseRequest\x121\n\x05offer\x18\x01 \x01(\x0b2".eve_public.store.offer.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\r\x12?\n\x04gift\x18\x03 \x01(\x0b2/.eve_public.plex.vault.api.PurchaseRequest.GiftH\x00\x12\x12\n\x08not_gift\x18\x04 \x01(\x08H\x00\x1a\xa2\x01\n\x04Gift\x12)\n\x04user\x18\x01 \x01(\x0b2\x1b.eve_public.user.Identifier\x12\x16\n\x0cno_character\x18\x02 \x01(\x08H\x00\x125\n\tcharacter\x18\x03 \x01(\x0b2 .eve_public.character.IdentifierH\x00\x12\x0f\n\x07message\x18\x04 \x01(\tB\x0f\n\rhas_characterB\t\n\x07is_gift"\x12\n\x10PurchaseResponseBFZDgithub.com/ccpgames/eve-proto-go/generated/eve_public/plex/vault/apib\x06proto3', dependencies=[eve__public_dot_character_dot_character__pb2.DESCRIPTOR,
 eve__public_dot_plex_dot_plex__pb2.DESCRIPTOR,
 eve__public_dot_store_dot_offer_dot_offer__pb2.DESCRIPTOR,
 eve__public_dot_user_dot_user__pb2.DESCRIPTOR])
_BALANCEREQUEST = _descriptor.Descriptor(name='BalanceRequest', full_name='eve_public.plex.vault.api.BalanceRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=201, serialized_end=217)
_BALANCERESPONSE = _descriptor.Descriptor(name='BalanceResponse', full_name='eve_public.plex.vault.api.BalanceResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='balance', full_name='eve_public.plex.vault.api.BalanceResponse.balance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=219, serialized_end=280)
_PURCHASEREQUEST_GIFT = _descriptor.Descriptor(name='Gift', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_character', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift.no_character', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift.character', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='message', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift.message', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='has_character', full_name='eve_public.plex.vault.api.PurchaseRequest.Gift.has_character', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=457, serialized_end=619)
_PURCHASEREQUEST = _descriptor.Descriptor(name='PurchaseRequest', full_name='eve_public.plex.vault.api.PurchaseRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='offer', full_name='eve_public.plex.vault.api.PurchaseRequest.offer', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='quantity', full_name='eve_public.plex.vault.api.PurchaseRequest.quantity', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='gift', full_name='eve_public.plex.vault.api.PurchaseRequest.gift', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='not_gift', full_name='eve_public.plex.vault.api.PurchaseRequest.not_gift', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_PURCHASEREQUEST_GIFT], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='is_gift', full_name='eve_public.plex.vault.api.PurchaseRequest.is_gift', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=283, serialized_end=630)
_PURCHASERESPONSE = _descriptor.Descriptor(name='PurchaseResponse', full_name='eve_public.plex.vault.api.PurchaseResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=632, serialized_end=650)
_BALANCERESPONSE.fields_by_name['balance'].message_type = eve__public_dot_plex_dot_plex__pb2._CURRENCY
_PURCHASEREQUEST_GIFT.fields_by_name['user'].message_type = eve__public_dot_user_dot_user__pb2._IDENTIFIER
_PURCHASEREQUEST_GIFT.fields_by_name['character'].message_type = eve__public_dot_character_dot_character__pb2._IDENTIFIER
_PURCHASEREQUEST_GIFT.containing_type = _PURCHASEREQUEST
_PURCHASEREQUEST_GIFT.oneofs_by_name['has_character'].fields.append(_PURCHASEREQUEST_GIFT.fields_by_name['no_character'])
_PURCHASEREQUEST_GIFT.fields_by_name['no_character'].containing_oneof = _PURCHASEREQUEST_GIFT.oneofs_by_name['has_character']
_PURCHASEREQUEST_GIFT.oneofs_by_name['has_character'].fields.append(_PURCHASEREQUEST_GIFT.fields_by_name['character'])
_PURCHASEREQUEST_GIFT.fields_by_name['character'].containing_oneof = _PURCHASEREQUEST_GIFT.oneofs_by_name['has_character']
_PURCHASEREQUEST.fields_by_name['offer'].message_type = eve__public_dot_store_dot_offer_dot_offer__pb2._IDENTIFIER
_PURCHASEREQUEST.fields_by_name['gift'].message_type = _PURCHASEREQUEST_GIFT
_PURCHASEREQUEST.oneofs_by_name['is_gift'].fields.append(_PURCHASEREQUEST.fields_by_name['gift'])
_PURCHASEREQUEST.fields_by_name['gift'].containing_oneof = _PURCHASEREQUEST.oneofs_by_name['is_gift']
_PURCHASEREQUEST.oneofs_by_name['is_gift'].fields.append(_PURCHASEREQUEST.fields_by_name['not_gift'])
_PURCHASEREQUEST.fields_by_name['not_gift'].containing_oneof = _PURCHASEREQUEST.oneofs_by_name['is_gift']
DESCRIPTOR.message_types_by_name['BalanceRequest'] = _BALANCEREQUEST
DESCRIPTOR.message_types_by_name['BalanceResponse'] = _BALANCERESPONSE
DESCRIPTOR.message_types_by_name['PurchaseRequest'] = _PURCHASEREQUEST
DESCRIPTOR.message_types_by_name['PurchaseResponse'] = _PURCHASERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
BalanceRequest = _reflection.GeneratedProtocolMessageType('BalanceRequest', (_message.Message,), {'DESCRIPTOR': _BALANCEREQUEST,
 '__module__': 'eve_public.plex.vault.api.requests_pb2'})
_sym_db.RegisterMessage(BalanceRequest)
BalanceResponse = _reflection.GeneratedProtocolMessageType('BalanceResponse', (_message.Message,), {'DESCRIPTOR': _BALANCERESPONSE,
 '__module__': 'eve_public.plex.vault.api.requests_pb2'})
_sym_db.RegisterMessage(BalanceResponse)
PurchaseRequest = _reflection.GeneratedProtocolMessageType('PurchaseRequest', (_message.Message,), {'Gift': _reflection.GeneratedProtocolMessageType('Gift', (_message.Message,), {'DESCRIPTOR': _PURCHASEREQUEST_GIFT,
          '__module__': 'eve_public.plex.vault.api.requests_pb2'}),
 'DESCRIPTOR': _PURCHASEREQUEST,
 '__module__': 'eve_public.plex.vault.api.requests_pb2'})
_sym_db.RegisterMessage(PurchaseRequest)
_sym_db.RegisterMessage(PurchaseRequest.Gift)
PurchaseResponse = _reflection.GeneratedProtocolMessageType('PurchaseResponse', (_message.Message,), {'DESCRIPTOR': _PURCHASERESPONSE,
 '__module__': 'eve_public.plex.vault.api.requests_pb2'})
_sym_db.RegisterMessage(PurchaseResponse)
DESCRIPTOR._options = None
