#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\bubble\presence\presence_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/bubble/presence/presence.proto', package='eve.bubble.presence', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/bubble/presence', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/bubble/presence/presence.proto\x12\x13eve.bubble.presence\x1a\x1deve/character/character.proto\x1a\x13eve/ship/ship.proto"{\n\x06Member\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12"\n\x04ship\x18\x02 \x01(\x0b2\x14.eve.ship.Identifier\x12\x0f\n\x07cloaked\x18\x03 \x01(\x08\x12\x0e\n\x06online\x18\x04 \x01(\x08B@Z>github.com/ccpgames/eve-proto-go/generated/eve/bubble/presenceb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_MEMBER = _descriptor.Descriptor(name='Member', full_name='eve.bubble.presence.Member', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.bubble.presence.Member.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ship', full_name='eve.bubble.presence.Member.ship', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='cloaked', full_name='eve.bubble.presence.Member.cloaked', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='online', full_name='eve.bubble.presence.Member.online', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=111, serialized_end=234)
_MEMBER.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_MEMBER.fields_by_name['ship'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Member'] = _MEMBER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Member = _reflection.GeneratedProtocolMessageType('Member', (_message.Message,), {'DESCRIPTOR': _MEMBER,
 '__module__': 'eve.bubble.presence.presence_pb2'})
_sym_db.RegisterMessage(Member)
DESCRIPTOR._options = None
