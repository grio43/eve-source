#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ore\ore_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.ore import ore_type_pb2 as eve_dot_ore_dot_ore__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ore/ore.proto', package='eve.ore', syntax='proto3', serialized_options='Z2github.com/ccpgames/eve-proto-go/generated/eve/ore', create_key=_descriptor._internal_create_key, serialized_pb='\n\x11eve/ore/ore.proto\x12\x07eve.ore\x1a\x16eve/ore/ore_type.proto"7\n\nIdentifier\x12)\n\x04type\x18\x01 \x01(\x0b2\x1b.eve.ore.oretype.IdentifierB4Z2github.com/ccpgames/eve-proto-go/generated/eve/oreb\x06proto3', dependencies=[eve_dot_ore_dot_ore__type__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.ore.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.ore.Identifier.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=54, serialized_end=109)
_IDENTIFIER.fields_by_name['type'].message_type = eve_dot_ore_dot_ore__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.ore.ore_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
