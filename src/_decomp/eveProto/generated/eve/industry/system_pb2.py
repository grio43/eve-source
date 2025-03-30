#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\system_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.industry import activity_pb2 as eve_dot_industry_dot_activity__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/system.proto', package='eve.industry.system', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/industry/system', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/industry/system.proto\x12\x13eve.industry.system\x1a\x1beve/industry/activity.proto\x1a!eve/solarsystem/solarsystem.proto"k\n\x07Indices\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12-\n\x07indices\x18\x02 \x03(\x0b2\x1c.eve.industry.activity.Index"\x17\n\x15GetCostIndicesRequest"L\n\x16GetCostIndicesResponse\x122\n\x0ccost_indices\x18\x01 \x03(\x0b2\x1c.eve.industry.system.IndicesB@Z>github.com/ccpgames/eve-proto-go/generated/eve/industry/systemb\x06proto3', dependencies=[eve_dot_industry_dot_activity__pb2.DESCRIPTOR, eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_INDICES = _descriptor.Descriptor(name='Indices', full_name='eve.industry.system.Indices', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.industry.system.Indices.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='indices', full_name='eve.industry.system.Indices.indices', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=114, serialized_end=221)
_GETCOSTINDICESREQUEST = _descriptor.Descriptor(name='GetCostIndicesRequest', full_name='eve.industry.system.GetCostIndicesRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=223, serialized_end=246)
_GETCOSTINDICESRESPONSE = _descriptor.Descriptor(name='GetCostIndicesResponse', full_name='eve.industry.system.GetCostIndicesResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='cost_indices', full_name='eve.industry.system.GetCostIndicesResponse.cost_indices', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=248, serialized_end=324)
_INDICES.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_INDICES.fields_by_name['indices'].message_type = eve_dot_industry_dot_activity__pb2._INDEX
_GETCOSTINDICESRESPONSE.fields_by_name['cost_indices'].message_type = _INDICES
DESCRIPTOR.message_types_by_name['Indices'] = _INDICES
DESCRIPTOR.message_types_by_name['GetCostIndicesRequest'] = _GETCOSTINDICESREQUEST
DESCRIPTOR.message_types_by_name['GetCostIndicesResponse'] = _GETCOSTINDICESRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Indices = _reflection.GeneratedProtocolMessageType('Indices', (_message.Message,), {'DESCRIPTOR': _INDICES,
 '__module__': 'eve.industry.system_pb2'})
_sym_db.RegisterMessage(Indices)
GetCostIndicesRequest = _reflection.GeneratedProtocolMessageType('GetCostIndicesRequest', (_message.Message,), {'DESCRIPTOR': _GETCOSTINDICESREQUEST,
 '__module__': 'eve.industry.system_pb2'})
_sym_db.RegisterMessage(GetCostIndicesRequest)
GetCostIndicesResponse = _reflection.GeneratedProtocolMessageType('GetCostIndicesResponse', (_message.Message,), {'DESCRIPTOR': _GETCOSTINDICESRESPONSE,
 '__module__': 'eve.industry.system_pb2'})
_sym_db.RegisterMessage(GetCostIndicesResponse)
DESCRIPTOR._options = None
