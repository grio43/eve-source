#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\store\category\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve import eve_pb2 as eve_dot_eve__pb2
from eveProto.generated.eve.store.category import category_pb2 as eve_dot_store_dot_category_dot_category__pb2
from eveProto.generated.eve.store import store_pb2 as eve_dot_store_dot_store__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/store/category/api.proto', package='eve.store.category.api', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/store/category/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/store/category/api.proto\x12\x16eve.store.category.api\x1a\reve/eve.proto\x1a!eve/store/category/category.proto\x1a\x15eve/store/store.proto">\n\nGetRequest\x120\n\x08category\x18\x01 \x01(\x0b2\x1e.eve.store.category.Identifier"A\n\x0bGetResponse\x122\n\nattributes\x18\x01 \x01(\x0b2\x1e.eve.store.category.Attributes"M\n\rGetAllRequest\x12#\n\x07catalog\x18\x01 \x01(\x0e2\x12.eve.store.Catalog\x12\x17\n\x04page\x18\x02 \x01(\x0b2\t.eve.Page"f\n\x0eGetAllResponse\x122\n\ncategories\x18\x01 \x03(\x0b2\x1e.eve.store.category.Identifier\x12 \n\tnext_page\x18\x02 \x01(\x0b2\r.eve.NextPageBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/store/category/apib\x06proto3', dependencies=[eve_dot_eve__pb2.DESCRIPTOR, eve_dot_store_dot_category_dot_category__pb2.DESCRIPTOR, eve_dot_store_dot_store__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.store.category.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='category', full_name='eve.store.category.api.GetRequest.category', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=129, serialized_end=191)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.store.category.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.store.category.api.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=193, serialized_end=258)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.store.category.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='catalog', full_name='eve.store.category.api.GetAllRequest.catalog', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='page', full_name='eve.store.category.api.GetAllRequest.page', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=260, serialized_end=337)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.store.category.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='categories', full_name='eve.store.category.api.GetAllResponse.categories', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='next_page', full_name='eve.store.category.api.GetAllResponse.next_page', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=339, serialized_end=441)
_GETREQUEST.fields_by_name['category'].message_type = eve_dot_store_dot_category_dot_category__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = eve_dot_store_dot_category_dot_category__pb2._ATTRIBUTES
_GETALLREQUEST.fields_by_name['catalog'].enum_type = eve_dot_store_dot_store__pb2._CATALOG
_GETALLREQUEST.fields_by_name['page'].message_type = eve_dot_eve__pb2._PAGE
_GETALLRESPONSE.fields_by_name['categories'].message_type = eve_dot_store_dot_category_dot_category__pb2._IDENTIFIER
_GETALLRESPONSE.fields_by_name['next_page'].message_type = eve_dot_eve__pb2._NEXTPAGE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.store.category.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.store.category.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.store.category.api_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.store.category.api_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
DESCRIPTOR._options = None
