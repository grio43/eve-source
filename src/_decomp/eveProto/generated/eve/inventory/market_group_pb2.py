#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\inventory\market_group_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/inventory/market_group.proto', package='eve.inventory.market_group', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/market_group', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/inventory/market_group.proto\x12\x1aeve.inventory.market_group" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\x94\x01\n\nAttributes\x12\x19\n\x0fno_parent_group\x18\x01 \x01(\x08H\x00\x12>\n\x0cparent_group\x18\x02 \x01(\x0b2&.eve.inventory.market_group.IdentifierH\x00\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x13\n\x0bdescription\x18\x04 \x01(\tB\x08\n\x06parent"\x0f\n\rGetAllRequest"H\n\x0eGetAllResponse\x126\n\x06groups\x18\x01 \x03(\x0b2&.eve.inventory.market_group.Identifier"C\n\nGetRequest\x125\n\x05group\x18\x01 \x01(\x0b2&.eve.inventory.market_group.Identifier"D\n\x0bGetResponse\x125\n\x05group\x18\x01 \x01(\x0b2&.eve.inventory.market_group.AttributesBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/inventory/market_groupb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.inventory.market_group.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.inventory.market_group.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=64, serialized_end=96)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.inventory.market_group.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='no_parent_group', full_name='eve.inventory.market_group.Attributes.no_parent_group', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='parent_group', full_name='eve.inventory.market_group.Attributes.parent_group', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='name', full_name='eve.inventory.market_group.Attributes.name', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='description', full_name='eve.inventory.market_group.Attributes.description', index=3, number=4, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='parent', full_name='eve.inventory.market_group.Attributes.parent', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=99, serialized_end=247)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.inventory.market_group.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=249, serialized_end=264)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.inventory.market_group.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='groups', full_name='eve.inventory.market_group.GetAllResponse.groups', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=266, serialized_end=338)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.inventory.market_group.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='group', full_name='eve.inventory.market_group.GetRequest.group', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=340, serialized_end=407)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.inventory.market_group.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='group', full_name='eve.inventory.market_group.GetResponse.group', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=409, serialized_end=477)
_ATTRIBUTES.fields_by_name['parent_group'].message_type = _IDENTIFIER
_ATTRIBUTES.oneofs_by_name['parent'].fields.append(_ATTRIBUTES.fields_by_name['no_parent_group'])
_ATTRIBUTES.fields_by_name['no_parent_group'].containing_oneof = _ATTRIBUTES.oneofs_by_name['parent']
_ATTRIBUTES.oneofs_by_name['parent'].fields.append(_ATTRIBUTES.fields_by_name['parent_group'])
_ATTRIBUTES.fields_by_name['parent_group'].containing_oneof = _ATTRIBUTES.oneofs_by_name['parent']
_GETALLRESPONSE.fields_by_name['groups'].message_type = _IDENTIFIER
_GETREQUEST.fields_by_name['group'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['group'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(Attributes)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.inventory.market_group_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
