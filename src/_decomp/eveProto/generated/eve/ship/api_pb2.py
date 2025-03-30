#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/api.proto', package='eve.ship.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x12eve/ship/api.proto\x12\x0ceve.ship.api\x1a\x13eve/ship/ship.proto"6\n\nGetRequest\x12(\n\nidentifier\x18\x01 \x01(\x0b2\x14.eve.ship.Identifier"7\n\x0bGetResponse\x12(\n\nattributes\x18\x01 \x01(\x0b2\x14.eve.ship.Attributes"H\n\x1cGetPlayerSuppliedNameRequest\x12(\n\nidentifier\x18\x01 \x01(\x0b2\x14.eve.ship.Identifier"-\n\x1dGetPlayerSuppliedNameResponse\x12\x0c\n\x04name\x18\x01 \x01(\tB9Z7github.com/ccpgames/eve-proto-go/generated/eve/ship/apib\x06proto3', dependencies=[eve_dot_ship_dot_ship__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.ship.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.ship.api.GetRequest.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=57, serialized_end=111)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.ship.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.ship.api.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=113, serialized_end=168)
_GETPLAYERSUPPLIEDNAMEREQUEST = _descriptor.Descriptor(name='GetPlayerSuppliedNameRequest', full_name='eve.ship.api.GetPlayerSuppliedNameRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.ship.api.GetPlayerSuppliedNameRequest.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=170, serialized_end=242)
_GETPLAYERSUPPLIEDNAMERESPONSE = _descriptor.Descriptor(name='GetPlayerSuppliedNameResponse', full_name='eve.ship.api.GetPlayerSuppliedNameResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.ship.api.GetPlayerSuppliedNameResponse.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=244, serialized_end=289)
_GETREQUEST.fields_by_name['identifier'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = eve_dot_ship_dot_ship__pb2._ATTRIBUTES
_GETPLAYERSUPPLIEDNAMEREQUEST.fields_by_name['identifier'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetPlayerSuppliedNameRequest'] = _GETPLAYERSUPPLIEDNAMEREQUEST
DESCRIPTOR.message_types_by_name['GetPlayerSuppliedNameResponse'] = _GETPLAYERSUPPLIEDNAMERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.ship.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.ship.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetPlayerSuppliedNameRequest = _reflection.GeneratedProtocolMessageType('GetPlayerSuppliedNameRequest', (_message.Message,), {'DESCRIPTOR': _GETPLAYERSUPPLIEDNAMEREQUEST,
 '__module__': 'eve.ship.api_pb2'})
_sym_db.RegisterMessage(GetPlayerSuppliedNameRequest)
GetPlayerSuppliedNameResponse = _reflection.GeneratedProtocolMessageType('GetPlayerSuppliedNameResponse', (_message.Message,), {'DESCRIPTOR': _GETPLAYERSUPPLIEDNAMERESPONSE,
 '__module__': 'eve.ship.api_pb2'})
_sym_db.RegisterMessage(GetPlayerSuppliedNameResponse)
DESCRIPTOR._options = None
