#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\market\component\listing\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.market.component.listing import listing_pb2 as eve_dot_cosmetic_dot_market_dot_component_dot_listing_dot_listing__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/market/component/listing/api/requests.proto', package='eve.cosmetic.market.component.listing.api', syntax='proto3', serialized_options='ZTgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/component/listing/api', create_key=_descriptor._internal_create_key, serialized_pb='\n8eve/cosmetic/market/component/listing/api/requests.proto\x12)eve.cosmetic.market.component.listing.api\x1a3eve/cosmetic/market/component/listing/listing.proto"\x0f\n\rGetAllRequest"P\n\x0eGetAllResponse\x12>\n\x08listings\x18\x01 \x03(\x0b2,.eve.cosmetic.market.component.listing.EntryBVZTgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/component/listing/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_market_dot_component_dot_listing_dot_listing__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.cosmetic.market.component.listing.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=156, serialized_end=171)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.cosmetic.market.component.listing.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='listings', full_name='eve.cosmetic.market.component.listing.api.GetAllResponse.listings', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=173, serialized_end=253)
_GETALLRESPONSE.fields_by_name['listings'].message_type = eve_dot_cosmetic_dot_market_dot_component_dot_listing_dot_listing__pb2._ENTRY
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.cosmetic.market.component.listing.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.cosmetic.market.component.listing.api.requests_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
DESCRIPTOR._options = None
