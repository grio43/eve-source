#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\structure\paintwork\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.structure.paintwork import paintwork_pb2 as eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/structure/paintwork/api/api.proto', package='eve.cosmetic.structure.paintwork.api', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/api', create_key=_descriptor._internal_create_key, serialized_pb='\n.eve/cosmetic/structure/paintwork/api/api.proto\x12$eve.cosmetic.structure.paintwork.api\x1a0eve/cosmetic/structure/paintwork/paintwork.proto\x1a\x1deve/structure/structure.proto"{\n\x03Set\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier\x12F\n\tpaintwork\x18\x02 \x01(\x0b23.eve.cosmetic.structure.paintwork.SlotConfigurationBQZOgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2.DESCRIPTOR, eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_SET = _descriptor.Descriptor(name='Set', full_name='eve.cosmetic.structure.paintwork.api.Set', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.cosmetic.structure.paintwork.api.Set.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='paintwork', full_name='eve.cosmetic.structure.paintwork.api.Set.paintwork', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=169, serialized_end=292)
_SET.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_SET.fields_by_name['paintwork'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2._SLOTCONFIGURATION
DESCRIPTOR.message_types_by_name['Set'] = _SET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Set = _reflection.GeneratedProtocolMessageType('Set', (_message.Message,), {'DESCRIPTOR': _SET,
 '__module__': 'eve.cosmetic.structure.paintwork.api.api_pb2'})
_sym_db.RegisterMessage(Set)
DESCRIPTOR._options = None
