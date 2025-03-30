#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\deadspace\incursionsite\incursion_site_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.deadspace import archetype_pb2 as eve_dot_deadspace_dot_archetype__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/deadspace/incursionsite/incursion_site.proto', package='eve.deadspace.incursionsite', syntax='proto3', serialized_options='ZFgithub.com/ccpgames/eve-proto-go/generated/eve/deadspace/incursionsite', create_key=_descriptor._internal_create_key, serialized_pb='\n0eve/deadspace/incursionsite/incursion_site.proto\x12\x1beve.deadspace.incursionsite\x1a\x1deve/deadspace/archetype.proto"H\n\nAttributes\x126\n\tarchetype\x18\x01 \x01(\x0b2#.eve.deadspace.archetype.Identifier:\x02\x18\x01BHZFgithub.com/ccpgames/eve-proto-go/generated/eve/deadspace/incursionsiteb\x06proto3', dependencies=[eve_dot_deadspace_dot_archetype__pb2.DESCRIPTOR])
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.deadspace.incursionsite.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='archetype', full_name='eve.deadspace.incursionsite.Attributes.archetype', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=112, serialized_end=184)
_ATTRIBUTES.fields_by_name['archetype'].message_type = eve_dot_deadspace_dot_archetype__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.deadspace.incursionsite.incursion_site_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
_ATTRIBUTES._options = None
