#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vanguard\contract\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vanguard/contract/api/events.proto', package='eve.vanguard.contract.api', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/vanguard/contract/api', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/vanguard/contract/api/events.proto\x12\x19eve.vanguard.contract.api"\x0f\n\tCompleted:\x02\x18\x01"!\n\x1bCorruptionContractCompleted:\x02\x18\x01""\n\x1cSuppressionContractCompleted:\x02\x18\x01BFZDgithub.com/ccpgames/eve-proto-go/generated/eve/vanguard/contract/apib\x06proto3')
_COMPLETED = _descriptor.Descriptor(name='Completed', full_name='eve.vanguard.contract.api.Completed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=69, serialized_end=84)
_CORRUPTIONCONTRACTCOMPLETED = _descriptor.Descriptor(name='CorruptionContractCompleted', full_name='eve.vanguard.contract.api.CorruptionContractCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=119)
_SUPPRESSIONCONTRACTCOMPLETED = _descriptor.Descriptor(name='SuppressionContractCompleted', full_name='eve.vanguard.contract.api.SuppressionContractCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=121, serialized_end=155)
DESCRIPTOR.message_types_by_name['Completed'] = _COMPLETED
DESCRIPTOR.message_types_by_name['CorruptionContractCompleted'] = _CORRUPTIONCONTRACTCOMPLETED
DESCRIPTOR.message_types_by_name['SuppressionContractCompleted'] = _SUPPRESSIONCONTRACTCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Completed = _reflection.GeneratedProtocolMessageType('Completed', (_message.Message,), {'DESCRIPTOR': _COMPLETED,
 '__module__': 'eve.vanguard.contract.api.events_pb2'})
_sym_db.RegisterMessage(Completed)
CorruptionContractCompleted = _reflection.GeneratedProtocolMessageType('CorruptionContractCompleted', (_message.Message,), {'DESCRIPTOR': _CORRUPTIONCONTRACTCOMPLETED,
 '__module__': 'eve.vanguard.contract.api.events_pb2'})
_sym_db.RegisterMessage(CorruptionContractCompleted)
SuppressionContractCompleted = _reflection.GeneratedProtocolMessageType('SuppressionContractCompleted', (_message.Message,), {'DESCRIPTOR': _SUPPRESSIONCONTRACTCOMPLETED,
 '__module__': 'eve.vanguard.contract.api.events_pb2'})
_sym_db.RegisterMessage(SuppressionContractCompleted)
DESCRIPTOR._options = None
_COMPLETED._options = None
_CORRUPTIONCONTRACTCOMPLETED._options = None
_SUPPRESSIONCONTRACTCOMPLETED._options = None
