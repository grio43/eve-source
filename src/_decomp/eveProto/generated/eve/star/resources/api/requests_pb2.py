#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\star\resources\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.star import star_pb2 as eve_dot_star_dot_star__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/star/resources/api/requests.proto', package='eve.star.resources.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/star/resource/api', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/star/resources/api/requests.proto\x12\x16eve.star.resources.api\x1a\x13eve/star/star.proto"?\n\x19GetPowerProductionRequest\x12"\n\x04star\x18\x01 \x01(\x0b2\x14.eve.star.Identifier",\n\x1aGetPowerProductionResponse\x12\x0e\n\x06amount\x18\x01 \x01(\x04BBZ@github.com/ccpgames/eve-proto-go/generated/eve/star/resource/apib\x06proto3', dependencies=[eve_dot_star_dot_star__pb2.DESCRIPTOR])
_GETPOWERPRODUCTIONREQUEST = _descriptor.Descriptor(name='GetPowerProductionRequest', full_name='eve.star.resources.api.GetPowerProductionRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='star', full_name='eve.star.resources.api.GetPowerProductionRequest.star', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=86, serialized_end=149)
_GETPOWERPRODUCTIONRESPONSE = _descriptor.Descriptor(name='GetPowerProductionResponse', full_name='eve.star.resources.api.GetPowerProductionResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.star.resources.api.GetPowerProductionResponse.amount', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=151, serialized_end=195)
_GETPOWERPRODUCTIONREQUEST.fields_by_name['star'].message_type = eve_dot_star_dot_star__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetPowerProductionRequest'] = _GETPOWERPRODUCTIONREQUEST
DESCRIPTOR.message_types_by_name['GetPowerProductionResponse'] = _GETPOWERPRODUCTIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetPowerProductionRequest = _reflection.GeneratedProtocolMessageType('GetPowerProductionRequest', (_message.Message,), {'DESCRIPTOR': _GETPOWERPRODUCTIONREQUEST,
 '__module__': 'eve.star.resources.api.requests_pb2'})
_sym_db.RegisterMessage(GetPowerProductionRequest)
GetPowerProductionResponse = _reflection.GeneratedProtocolMessageType('GetPowerProductionResponse', (_message.Message,), {'DESCRIPTOR': _GETPOWERPRODUCTIONRESPONSE,
 '__module__': 'eve.star.resources.api.requests_pb2'})
_sym_db.RegisterMessage(GetPowerProductionResponse)
DESCRIPTOR._options = None
