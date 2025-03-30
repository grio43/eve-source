#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\bookmark\folder_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/bookmark/folder.proto', package='eve.bookmark.folder', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/folder', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/bookmark/folder.proto\x12\x13eve.bookmark.folder\x1a\x1deve/character/character.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"[\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12*\n\x07creator\x18\x03 \x01(\x0b2\x19.eve.character.Identifier*\x9d\x01\n\x0bAccessLevel\x12\x15\n\x11ACCESS_LEVEL_NONE\x10\x00\x12\x19\n\x15ACCESS_LEVEL_PERSONAL\x10\x01\x12\x15\n\x11ACCESS_LEVEL_VIEW\x10\x02\x12\x14\n\x10ACCESS_LEVEL_USE\x10\x03\x12\x17\n\x13ACCESS_LEVEL_MANAGE\x10\x04\x12\x16\n\x12ACCESS_LEVEL_ADMIN\x10\x05B7Z5github.com/ccpgames/eve-proto-go/generated/eve/folderb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_ACCESSLEVEL = _descriptor.EnumDescriptor(name='AccessLevel', full_name='eve.bookmark.folder.AccessLevel', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_NONE', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_PERSONAL', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_VIEW', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_USE', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_MANAGE', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACCESS_LEVEL_ADMIN', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=209, serialized_end=366)
_sym_db.RegisterEnumDescriptor(_ACCESSLEVEL)
AccessLevel = enum_type_wrapper.EnumTypeWrapper(_ACCESSLEVEL)
ACCESS_LEVEL_NONE = 0
ACCESS_LEVEL_PERSONAL = 1
ACCESS_LEVEL_VIEW = 2
ACCESS_LEVEL_USE = 3
ACCESS_LEVEL_MANAGE = 4
ACCESS_LEVEL_ADMIN = 5
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.bookmark.folder.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.bookmark.folder.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=81, serialized_end=113)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.bookmark.folder.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.bookmark.folder.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='description', full_name='eve.bookmark.folder.Attributes.description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='creator', full_name='eve.bookmark.folder.Attributes.creator', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=115, serialized_end=206)
_ATTRIBUTES.fields_by_name['creator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.enum_types_by_name['AccessLevel'] = _ACCESSLEVEL
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.bookmark.folder_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.bookmark.folder_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
