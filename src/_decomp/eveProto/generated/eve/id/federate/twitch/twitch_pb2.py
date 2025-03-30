#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\id\federate\twitch\twitch_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/id/federate/twitch/twitch.proto', package='eve.id.federate.twitch', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/id/federate/twitch', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/id/federate/twitch/twitch.proto\x12\x16eve.id.federate.twitch"\x18\n\nIdentifier\x12\n\n\x02id\x18\x01 \x01(\t"(\n\nAttributes\x12\x1a\n\x12preferred_username\x18\x01 \x01(\tBCZAgithub.com/ccpgames/eve-proto-go/generated/eve/id/federate/twitchb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.id.federate.twitch.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.id.federate.twitch.Identifier.id', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=63, serialized_end=87)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.id.federate.twitch.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='preferred_username', full_name='eve.id.federate.twitch.Attributes.preferred_username', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=89, serialized_end=129)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.id.federate.twitch.twitch_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.id.federate.twitch.twitch_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
