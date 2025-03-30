#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\dungeon\room_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/dungeon/room.proto', package='eve.dungeon.room', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/dungeon/room', create_key=_descriptor._internal_create_key, serialized_pb='\n\x16eve/dungeon/room.proto\x12\x10eve.dungeon.room" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04B=Z;github.com/ccpgames/eve-proto-go/generated/eve/dungeon/roomb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.dungeon.room.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.dungeon.room.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=44, serialized_end=76)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.dungeon.room_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
