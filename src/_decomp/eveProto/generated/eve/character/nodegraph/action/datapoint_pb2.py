#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\nodegraph\action\datapoint_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.nodegraph import nodegraph_pb2 as eve_dot_nodegraph_dot_nodegraph__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/nodegraph/action/datapoint.proto', package='eve.character.nodegraph.action.datapoint', syntax='proto3', serialized_options='ZIgithub.com/ccpgames/eve-proto-go/generated/eve/character/nodegraph/action', create_key=_descriptor._internal_create_key, serialized_pb='\n.eve/character/nodegraph/action/datapoint.proto\x12(eve.character.nodegraph.action.datapoint\x1a\x1deve/character/character.proto\x1a\x1deve/nodegraph/nodegraph.proto"\xb4\x01\n\tTriggered\x12,\n\tnodegraph\x18\x01 \x01(\x0b2\x19.eve.nodegraph.Identifier\x12\x16\n\x0edatapoint_name\x18\x02 \x01(\t\x12\x1d\n\x13no_active_character\x18\x03 \x01(\x08H\x00\x125\n\x10active_character\x18\x04 \x01(\x0b2\x19.eve.character.IdentifierH\x00B\x0b\n\tcharacterBKZIgithub.com/ccpgames/eve-proto-go/generated/eve/character/nodegraph/actionb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_nodegraph_dot_nodegraph__pb2.DESCRIPTOR])
_TRIGGERED = _descriptor.Descriptor(name='Triggered', full_name='eve.character.nodegraph.action.datapoint.Triggered', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='nodegraph', full_name='eve.character.nodegraph.action.datapoint.Triggered.nodegraph', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='datapoint_name', full_name='eve.character.nodegraph.action.datapoint.Triggered.datapoint_name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_active_character', full_name='eve.character.nodegraph.action.datapoint.Triggered.no_active_character', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='active_character', full_name='eve.character.nodegraph.action.datapoint.Triggered.active_character', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='character', full_name='eve.character.nodegraph.action.datapoint.Triggered.character', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=155, serialized_end=335)
_TRIGGERED.fields_by_name['nodegraph'].message_type = eve_dot_nodegraph_dot_nodegraph__pb2._IDENTIFIER
_TRIGGERED.fields_by_name['active_character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_TRIGGERED.oneofs_by_name['character'].fields.append(_TRIGGERED.fields_by_name['no_active_character'])
_TRIGGERED.fields_by_name['no_active_character'].containing_oneof = _TRIGGERED.oneofs_by_name['character']
_TRIGGERED.oneofs_by_name['character'].fields.append(_TRIGGERED.fields_by_name['active_character'])
_TRIGGERED.fields_by_name['active_character'].containing_oneof = _TRIGGERED.oneofs_by_name['character']
DESCRIPTOR.message_types_by_name['Triggered'] = _TRIGGERED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Triggered = _reflection.GeneratedProtocolMessageType('Triggered', (_message.Message,), {'DESCRIPTOR': _TRIGGERED,
 '__module__': 'eve.character.nodegraph.action.datapoint_pb2'})
_sym_db.RegisterMessage(Triggered)
DESCRIPTOR._options = None
