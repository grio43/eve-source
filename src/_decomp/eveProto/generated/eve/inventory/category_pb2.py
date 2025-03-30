#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\inventory\category_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/inventory/category.proto', package='eve.inventory.category', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/category', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1ceve/inventory/category.proto\x12\x16eve.inventory.category" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"-\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tpublished\x18\x02 \x01(\x08"B\n\nGetRequest\x124\n\x08category\x18\x01 \x01(\x0b2".eve.inventory.category.Identifier"E\n\x0bGetResponse\x126\n\nattributes\x18\x01 \x01(\x0b2".eve.inventory.category.Attributes"\x0f\n\rGetAllRequest"H\n\x0eGetAllResponse\x126\n\ncategories\x18\x01 \x03(\x0b2".eve.inventory.category.IdentifierBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/categoryb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.inventory.category.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.inventory.category.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=56, serialized_end=88)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.inventory.category.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.inventory.category.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='published', full_name='eve.inventory.category.Attributes.published', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=90, serialized_end=135)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.inventory.category.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='category', full_name='eve.inventory.category.GetRequest.category', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=137, serialized_end=203)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.inventory.category.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.inventory.category.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=205, serialized_end=274)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.inventory.category.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=276, serialized_end=291)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.inventory.category.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='categories', full_name='eve.inventory.category.GetAllResponse.categories', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=293, serialized_end=365)
_GETREQUEST.fields_by_name['category'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = _ATTRIBUTES
_GETALLRESPONSE.fields_by_name['categories'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.inventory.category_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
DESCRIPTOR._options = None
