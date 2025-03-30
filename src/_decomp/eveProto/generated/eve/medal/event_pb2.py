#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\medal\event_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.medal import medal_pb2 as eve_dot_medal_dot_medal__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/medal/event.proto', package='eve.medal.event', syntax='proto3', serialized_options='Z:github.com/ccpgames/eve-proto-go/generated/eve/medal/event', create_key=_descriptor._internal_create_key, serialized_pb='\n\x15eve/medal/event.proto\x12\x0feve.medal.event\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x15eve/medal/medal.proto"\xf9\x01\n\x07Awarded\x12\'\n\x08medal_id\x18\x01 \x01(\x0b2\x15.eve.medal.Identifier\x12)\n\nmedal_info\x18\x02 \x01(\x0b2\x15.eve.medal.Attributes\x12-\n\nrecipients\x18\x03 \x03(\x0b2\x19.eve.character.Identifier\x120\n\x0bcorporation\x18\x04 \x01(\x0b2\x1b.eve.corporation.Identifier\x12)\n\x06issuer\x18\x05 \x01(\x0b2\x19.eve.character.Identifier\x12\x0e\n\x06reason\x18\x06 \x01(\tB<Z:github.com/ccpgames/eve-proto-go/generated/eve/medal/eventb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR, eve_dot_medal_dot_medal__pb2.DESCRIPTOR])
_AWARDED = _descriptor.Descriptor(name='Awarded', full_name='eve.medal.event.Awarded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='medal_id', full_name='eve.medal.event.Awarded.medal_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='medal_info', full_name='eve.medal.event.Awarded.medal_info', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='recipients', full_name='eve.medal.event.Awarded.recipients', index=2, number=3, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.medal.event.Awarded.corporation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issuer', full_name='eve.medal.event.Awarded.issuer', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reason', full_name='eve.medal.event.Awarded.reason', index=5, number=6, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=132, serialized_end=381)
_AWARDED.fields_by_name['medal_id'].message_type = eve_dot_medal_dot_medal__pb2._IDENTIFIER
_AWARDED.fields_by_name['medal_info'].message_type = eve_dot_medal_dot_medal__pb2._ATTRIBUTES
_AWARDED.fields_by_name['recipients'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_AWARDED.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_AWARDED.fields_by_name['issuer'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Awarded'] = _AWARDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Awarded = _reflection.GeneratedProtocolMessageType('Awarded', (_message.Message,), {'DESCRIPTOR': _AWARDED,
 '__module__': 'eve.medal.event_pb2'})
_sym_db.RegisterMessage(Awarded)
DESCRIPTOR._options = None
