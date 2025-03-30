#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\accounting\entrytype_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/accounting/entrytype.proto', package='eve.accounting.entrytype', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/accounting/entrytype', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/accounting/entrytype.proto\x12\x18eve.accounting.entrytype" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\x1a\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t"\x0f\n\rGetAllRequest"\xd2\x01\n\x0eGetAllResponse\x12G\n\x0bentry_types\x18\x01 \x03(\x0b22.eve.accounting.entrytype.GetAllResponse.EntryType\x1aw\n\tEntryType\x120\n\x02id\x18\x01 \x01(\x0b2$.eve.accounting.entrytype.Identifier\x128\n\nattributes\x18\x02 \x01(\x0b2$.eve.accounting.entrytype.AttributesBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/accounting/entrytypeb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.accounting.entrytype.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.accounting.entrytype.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=60, serialized_end=92)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.accounting.entrytype.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.accounting.entrytype.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=94, serialized_end=120)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.accounting.entrytype.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=137)
_GETALLRESPONSE_ENTRYTYPE = _descriptor.Descriptor(name='EntryType', full_name='eve.accounting.entrytype.GetAllResponse.EntryType', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.accounting.entrytype.GetAllResponse.EntryType.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.accounting.entrytype.GetAllResponse.EntryType.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=231, serialized_end=350)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.accounting.entrytype.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entry_types', full_name='eve.accounting.entrytype.GetAllResponse.entry_types', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETALLRESPONSE_ENTRYTYPE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=140, serialized_end=350)
_GETALLRESPONSE_ENTRYTYPE.fields_by_name['id'].message_type = _IDENTIFIER
_GETALLRESPONSE_ENTRYTYPE.fields_by_name['attributes'].message_type = _ATTRIBUTES
_GETALLRESPONSE_ENTRYTYPE.containing_type = _GETALLRESPONSE
_GETALLRESPONSE.fields_by_name['entry_types'].message_type = _GETALLRESPONSE_ENTRYTYPE
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.accounting.entrytype_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.accounting.entrytype_pb2'})
_sym_db.RegisterMessage(Attributes)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.accounting.entrytype_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'EntryType': _reflection.GeneratedProtocolMessageType('EntryType', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE_ENTRYTYPE,
               '__module__': 'eve.accounting.entrytype_pb2'}),
 'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.accounting.entrytype_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
_sym_db.RegisterMessage(GetAllResponse.EntryType)
DESCRIPTOR._options = None
