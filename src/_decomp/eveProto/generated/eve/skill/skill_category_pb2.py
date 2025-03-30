#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\skill\skill_category_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.skill import skill_type_pb2 as eve_dot_skill_dot_skill__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/skill/skill_category.proto', package='eve.skillcategory', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/skillcategory', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/skill/skill_category.proto\x12\x11eve.skillcategory\x1a\x1aeve/skill/skill_type.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"E\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12)\n\x06skills\x18\x02 \x03(\x0b2\x19.eve.skilltype.Identifier"\x0f\n\rGetAllRequest"C\n\x0eGetAllResponse\x121\n\ncategories\x18\x01 \x03(\x0b2\x1d.eve.skillcategory.Identifier"=\n\nGetRequest\x12/\n\x08category\x18\x01 \x01(\x0b2\x1d.eve.skillcategory.Identifier"@\n\x0bGetResponse\x121\n\nattributes\x18\x01 \x01(\x0b2\x1d.eve.skillcategory.AttributesB>Z<github.com/ccpgames/eve-proto-go/generated/eve/skillcategoryb\x06proto3', dependencies=[eve_dot_skill_dot_skill__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.skillcategory.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.skillcategory.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=81, serialized_end=113)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.skillcategory.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.skillcategory.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='skills', full_name='eve.skillcategory.Attributes.skills', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=115, serialized_end=184)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.skillcategory.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=186, serialized_end=201)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.skillcategory.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='categories', full_name='eve.skillcategory.GetAllResponse.categories', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=203, serialized_end=270)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.skillcategory.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='category', full_name='eve.skillcategory.GetRequest.category', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=272, serialized_end=333)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.skillcategory.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.skillcategory.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=335, serialized_end=399)
_ATTRIBUTES.fields_by_name['skills'].message_type = eve_dot_skill_dot_skill__type__pb2._IDENTIFIER
_GETALLRESPONSE.fields_by_name['categories'].message_type = _IDENTIFIER
_GETREQUEST.fields_by_name['category'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(Attributes)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.skill.skill_category_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
