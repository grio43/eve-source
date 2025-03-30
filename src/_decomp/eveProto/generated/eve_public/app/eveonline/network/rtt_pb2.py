#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\app\eveonline\network\rtt_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.network import rtt_pb2 as eve__public_dot_network_dot_rtt__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/app/eveonline/network/rtt.proto', package='eve_public.app.eveonline.network.rtt', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/network/rtt', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve_public/app/eveonline/network/rtt.proto\x12$eve_public.app.eveonline.network.rtt\x1a\x1ceve_public/network/rtt.proto"B\n\x10SamplesCollected\x12.\n\x06sample\x18\x01 \x03(\x0b2\x1e.eve_public.network.rtt.SampleBQZOgithub.com/ccpgames/eve-proto-go/generated/eve_public/app/eveonline/network/rttb\x06proto3', dependencies=[eve__public_dot_network_dot_rtt__pb2.DESCRIPTOR])
_SAMPLESCOLLECTED = _descriptor.Descriptor(name='SamplesCollected', full_name='eve_public.app.eveonline.network.rtt.SamplesCollected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sample', full_name='eve_public.app.eveonline.network.rtt.SamplesCollected.sample', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=114, serialized_end=180)
_SAMPLESCOLLECTED.fields_by_name['sample'].message_type = eve__public_dot_network_dot_rtt__pb2._SAMPLE
DESCRIPTOR.message_types_by_name['SamplesCollected'] = _SAMPLESCOLLECTED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SamplesCollected = _reflection.GeneratedProtocolMessageType('SamplesCollected', (_message.Message,), {'DESCRIPTOR': _SAMPLESCOLLECTED,
 '__module__': 'eve_public.app.eveonline.network.rtt_pb2'})
_sym_db.RegisterMessage(SamplesCollected)
DESCRIPTOR._options = None
