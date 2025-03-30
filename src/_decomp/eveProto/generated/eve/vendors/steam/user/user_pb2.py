#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vendors\steam\user\user_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vendors/steam/user/user.proto', package='eve.vendors.steam.user', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/steam/user', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/vendors/steam/user/user.proto\x12\x16eve.vendors.steam.user"\x1e\n\nIdentifier\x12\x10\n\x08steam_id\x18\x01 \x01(\t"5\n\nAttributes\x12\x11\n\tuser_name\x18\x01 \x01(\t\x12\x14\n\x0ccountry_code\x18\x02 \x01(\tBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/vendors/steam/userb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.vendors.steam.user.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='steam_id', full_name='eve.vendors.steam.user.Identifier.steam_id', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=61, serialized_end=91)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.vendors.steam.user.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user_name', full_name='eve.vendors.steam.user.Attributes.user_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='country_code', full_name='eve.vendors.steam.user.Attributes.country_code', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=146)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.vendors.steam.user.user_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.vendors.steam.user.user_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
