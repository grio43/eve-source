#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\graphics\graphic_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/graphics/graphic.proto', package='eve.graphics', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/graphics', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1aeve/graphics/graphic.proto\x12\x0ceve.graphics" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\x0f\n\rGetAllRequest"<\n\x0eGetAllResponse\x12*\n\x08graphics\x18\x01 \x03(\x0b2\x18.eve.graphics.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/graphicsb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.graphics.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.graphics.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=44, serialized_end=76)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.graphics.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=78, serialized_end=93)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.graphics.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='graphics', full_name='eve.graphics.GetAllResponse.graphics', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=95, serialized_end=155)
_GETALLRESPONSE.fields_by_name['graphics'].message_type = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.graphics.graphic_pb2'})
_sym_db.RegisterMessage(Identifier)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.graphics.graphic_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.graphics.graphic_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
DESCRIPTOR._options = None
