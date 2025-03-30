#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\hub\api\commands_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.sovereignty.hub import hub_pb2 as eve_dot_sovereignty_dot_hub_dot_hub__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/hub/api/commands.proto', package='eve.sovereignty.hub.api', syntax='proto3', serialized_options='ZBgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/api', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/sovereignty/hub/api/commands.proto\x12\x17eve.sovereignty.hub.api\x1a\x1deve/sovereignty/hub/hub.proto"C\n\x13SimulationCommanded\x12,\n\x03hub\x18\x01 \x01(\x0b2\x1f.eve.sovereignty.hub.IdentifierBDZBgithub.com/ccpgames/eve-proto-go/generated/eve/sovereignty/hub/apib\x06proto3', dependencies=[eve_dot_sovereignty_dot_hub_dot_hub__pb2.DESCRIPTOR])
_SIMULATIONCOMMANDED = _descriptor.Descriptor(name='SimulationCommanded', full_name='eve.sovereignty.hub.api.SimulationCommanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='hub', full_name='eve.sovereignty.hub.api.SimulationCommanded.hub', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=98, serialized_end=165)
_SIMULATIONCOMMANDED.fields_by_name['hub'].message_type = eve_dot_sovereignty_dot_hub_dot_hub__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['SimulationCommanded'] = _SIMULATIONCOMMANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SimulationCommanded = _reflection.GeneratedProtocolMessageType('SimulationCommanded', (_message.Message,), {'DESCRIPTOR': _SIMULATIONCOMMANDED,
 '__module__': 'eve.sovereignty.hub.api.commands_pb2'})
_sym_db.RegisterMessage(SimulationCommanded)
DESCRIPTOR._options = None
