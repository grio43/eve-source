#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\probe\exploration_scanresult_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.deadspace import archetype_pb2 as eve_dot_deadspace_dot_archetype__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/probe/exploration_scanresult.proto', package='eve.probe.explorationscanresult', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/probe/explorationscanresult', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/probe/exploration_scanresult.proto\x12\x1feve.probe.explorationscanresult\x1a\x1deve/deadspace/archetype.proto"\x0c\n\nIdentifier"D\n\nAttributes\x126\n\tarchetype\x18\x01 \x01(\x0b2#.eve.deadspace.archetype.IdentifierBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/probe/explorationscanresultb\x06proto3', dependencies=[eve_dot_deadspace_dot_archetype__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.probe.explorationscanresult.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=106, serialized_end=118)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.probe.explorationscanresult.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='archetype', full_name='eve.probe.explorationscanresult.Attributes.archetype', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=188)
_ATTRIBUTES.fields_by_name['archetype'].message_type = eve_dot_deadspace_dot_archetype__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.probe.exploration_scanresult_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.probe.exploration_scanresult_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
