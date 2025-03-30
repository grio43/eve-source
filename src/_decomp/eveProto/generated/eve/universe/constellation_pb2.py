#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\universe\constellation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.constellation import constellation_pb2 as eve_dot_constellation_dot_constellation__pb2
from eveProto.generated.eve.region import region_pb2 as eve_dot_region_dot_region__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/universe/constellation.proto', package='eve.universe.constellation', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/universe/constellation', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/universe/constellation.proto\x12\x1aeve.universe.constellation\x1a%eve/constellation/constellation.proto\x1a\x17eve/region/region.proto"?\n\x15GetAllInRegionRequest\x12&\n\x06region\x18\x01 \x01(\x0b2\x16.eve.region.Identifier"O\n\x16GetAllInRegionResponse\x125\n\x0econstellations\x18\x02 \x03(\x0b2\x1d.eve.constellation.IdentifierBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/universe/constellationb\x06proto3', dependencies=[eve_dot_constellation_dot_constellation__pb2.DESCRIPTOR, eve_dot_region_dot_region__pb2.DESCRIPTOR])
_GETALLINREGIONREQUEST = _descriptor.Descriptor(name='GetAllInRegionRequest', full_name='eve.universe.constellation.GetAllInRegionRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='region', full_name='eve.universe.constellation.GetAllInRegionRequest.region', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=128, serialized_end=191)
_GETALLINREGIONRESPONSE = _descriptor.Descriptor(name='GetAllInRegionResponse', full_name='eve.universe.constellation.GetAllInRegionResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='constellations', full_name='eve.universe.constellation.GetAllInRegionResponse.constellations', index=0, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=193, serialized_end=272)
_GETALLINREGIONREQUEST.fields_by_name['region'].message_type = eve_dot_region_dot_region__pb2._IDENTIFIER
_GETALLINREGIONRESPONSE.fields_by_name['constellations'].message_type = eve_dot_constellation_dot_constellation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetAllInRegionRequest'] = _GETALLINREGIONREQUEST
DESCRIPTOR.message_types_by_name['GetAllInRegionResponse'] = _GETALLINREGIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllInRegionRequest = _reflection.GeneratedProtocolMessageType('GetAllInRegionRequest', (_message.Message,), {'DESCRIPTOR': _GETALLINREGIONREQUEST,
 '__module__': 'eve.universe.constellation_pb2'})
_sym_db.RegisterMessage(GetAllInRegionRequest)
GetAllInRegionResponse = _reflection.GeneratedProtocolMessageType('GetAllInRegionResponse', (_message.Message,), {'DESCRIPTOR': _GETALLINREGIONRESPONSE,
 '__module__': 'eve.universe.constellation_pb2'})
_sym_db.RegisterMessage(GetAllInRegionResponse)
DESCRIPTOR._options = None
