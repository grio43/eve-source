#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\membership\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.membership import membership_pb2 as eve_dot_character_dot_membership_dot_membership__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/membership/api/events.proto', package='eve.character.membership.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/character/membership/api', create_key=_descriptor._internal_create_key, serialized_pb='\n)eve/character/membership/api/events.proto\x12\x1ceve.character.membership.api\x1a\x1deve/character/character.proto\x1a)eve/character/membership/membership.proto"q\n\x07Revised\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x128\n\nattributes\x18\x02 \x01(\x0b2$.eve.character.membership.AttributesBIZGgithub.com/ccpgames/eve-proto-go/generated/eve/character/membership/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_character_dot_membership_dot_membership__pb2.DESCRIPTOR])
_REVISED = _descriptor.Descriptor(name='Revised', full_name='eve.character.membership.api.Revised', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.membership.api.Revised.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.character.membership.api.Revised.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=149, serialized_end=262)
_REVISED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REVISED.fields_by_name['attributes'].message_type = eve_dot_character_dot_membership_dot_membership__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Revised'] = _REVISED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Revised = _reflection.GeneratedProtocolMessageType('Revised', (_message.Message,), {'DESCRIPTOR': _REVISED,
 '__module__': 'eve.character.membership.api.events_pb2'})
_sym_db.RegisterMessage(Revised)
DESCRIPTOR._options = None
