#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\market\skin\listing\api\admin\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.cosmetic.market.skin.listing import listing_pb2 as eve__public_dot_cosmetic_dot_market_dot_skin_dot_listing_dot_listing__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/market/skin/listing/api/admin/requests.proto', package='eve_public.cosmetic.market.skin.listing.api.admin', syntax='proto3', serialized_options='Z\\github.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/market/skin/listing/api/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n@eve_public/cosmetic/market/skin/listing/api/admin/requests.proto\x121eve_public.cosmetic.market.skin.listing.api.admin\x1a5eve_public/cosmetic/market/skin/listing/listing.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x89\x01\n\x14SetExpirationRequest\x12D\n\x07listing\x18\x01 \x01(\x0b23.eve_public.cosmetic.market.skin.listing.Identifier\x12+\n\x07expires\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp"\x17\n\x15SetExpirationResponseB^Z\\github.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/market/skin/listing/api/adminb\x06proto3', dependencies=[eve__public_dot_cosmetic_dot_market_dot_skin_dot_listing_dot_listing__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_SETEXPIRATIONREQUEST = _descriptor.Descriptor(name='SetExpirationRequest', full_name='eve_public.cosmetic.market.skin.listing.api.admin.SetExpirationRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='listing', full_name='eve_public.cosmetic.market.skin.listing.api.admin.SetExpirationRequest.listing', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='expires', full_name='eve_public.cosmetic.market.skin.listing.api.admin.SetExpirationRequest.expires', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=208, serialized_end=345)
_SETEXPIRATIONRESPONSE = _descriptor.Descriptor(name='SetExpirationResponse', full_name='eve_public.cosmetic.market.skin.listing.api.admin.SetExpirationResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=347, serialized_end=370)
_SETEXPIRATIONREQUEST.fields_by_name['listing'].message_type = eve__public_dot_cosmetic_dot_market_dot_skin_dot_listing_dot_listing__pb2._IDENTIFIER
_SETEXPIRATIONREQUEST.fields_by_name['expires'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['SetExpirationRequest'] = _SETEXPIRATIONREQUEST
DESCRIPTOR.message_types_by_name['SetExpirationResponse'] = _SETEXPIRATIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SetExpirationRequest = _reflection.GeneratedProtocolMessageType('SetExpirationRequest', (_message.Message,), {'DESCRIPTOR': _SETEXPIRATIONREQUEST,
 '__module__': 'eve_public.cosmetic.market.skin.listing.api.admin.requests_pb2'})
_sym_db.RegisterMessage(SetExpirationRequest)
SetExpirationResponse = _reflection.GeneratedProtocolMessageType('SetExpirationResponse', (_message.Message,), {'DESCRIPTOR': _SETEXPIRATIONRESPONSE,
 '__module__': 'eve_public.cosmetic.market.skin.listing.api.admin.requests_pb2'})
_sym_db.RegisterMessage(SetExpirationResponse)
DESCRIPTOR._options = None
