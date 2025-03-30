#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\fulfillment\offer_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/fulfillment/offer.proto', package='eve_public.fulfillment.offer', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/fulfillment/offer', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve_public/fulfillment/offer.proto\x12\x1ceve_public.fulfillment.offer"%\n\nIdentifier\x12\x13\n\x0bstore_offer\x18\x01 \x01(\t:\x02\x18\x01BIZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/fulfillment/offerb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.fulfillment.offer.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='store_offer', full_name='eve_public.fulfillment.offer.Identifier.store_offer', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=68, serialized_end=105)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.fulfillment.offer_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
_IDENTIFIER._options = None
