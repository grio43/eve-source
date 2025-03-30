#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\store\product\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.store.product import product_pb2 as eve_dot_store_dot_product_dot_product__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/store/product/api/requests.proto', package='eve.store.product.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/store/product/api', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/store/product/api/requests.proto\x12\x15eve.store.product.api\x1a\x1feve/store/product/product.proto\x1a\x13eve/user/user.proto\x1a\x1fgoogle/protobuf/timestamp.proto"<\n\nGetRequest\x12.\n\x07product\x18\x01 \x01(\x0b2\x1d.eve.store.product.Identifier"@\n\x0bGetResponse\x121\n\nattributes\x18\x01 \x01(\x0b2\x1d.eve.store.product.Attributes"D\n\x1eGetLastPlexPurchaseDateRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"T\n\x1fGetLastPlexPurchaseDateResponse\x121\n\rpurchase_date\x18\x01 \x01(\x0b2\x1a.google.protobuf.TimestampBBZ@github.com/ccpgames/eve-proto-go/generated/eve/store/product/apib\x06proto3', dependencies=[eve_dot_store_dot_product_dot_product__pb2.DESCRIPTOR, eve_dot_user_dot_user__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.store.product.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='product', full_name='eve.store.product.api.GetRequest.product', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=210)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.store.product.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.store.product.api.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=212, serialized_end=276)
_GETLASTPLEXPURCHASEDATEREQUEST = _descriptor.Descriptor(name='GetLastPlexPurchaseDateRequest', full_name='eve.store.product.api.GetLastPlexPurchaseDateRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.store.product.api.GetLastPlexPurchaseDateRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=278, serialized_end=346)
_GETLASTPLEXPURCHASEDATERESPONSE = _descriptor.Descriptor(name='GetLastPlexPurchaseDateResponse', full_name='eve.store.product.api.GetLastPlexPurchaseDateResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='purchase_date', full_name='eve.store.product.api.GetLastPlexPurchaseDateResponse.purchase_date', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=348, serialized_end=432)
_GETREQUEST.fields_by_name['product'].message_type = eve_dot_store_dot_product_dot_product__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = eve_dot_store_dot_product_dot_product__pb2._ATTRIBUTES
_GETLASTPLEXPURCHASEDATEREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETLASTPLEXPURCHASEDATERESPONSE.fields_by_name['purchase_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetLastPlexPurchaseDateRequest'] = _GETLASTPLEXPURCHASEDATEREQUEST
DESCRIPTOR.message_types_by_name['GetLastPlexPurchaseDateResponse'] = _GETLASTPLEXPURCHASEDATERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.store.product.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.store.product.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetLastPlexPurchaseDateRequest = _reflection.GeneratedProtocolMessageType('GetLastPlexPurchaseDateRequest', (_message.Message,), {'DESCRIPTOR': _GETLASTPLEXPURCHASEDATEREQUEST,
 '__module__': 'eve.store.product.api.requests_pb2'})
_sym_db.RegisterMessage(GetLastPlexPurchaseDateRequest)
GetLastPlexPurchaseDateResponse = _reflection.GeneratedProtocolMessageType('GetLastPlexPurchaseDateResponse', (_message.Message,), {'DESCRIPTOR': _GETLASTPLEXPURCHASEDATERESPONSE,
 '__module__': 'eve.store.product.api.requests_pb2'})
_sym_db.RegisterMessage(GetLastPlexPurchaseDateResponse)
DESCRIPTOR._options = None
