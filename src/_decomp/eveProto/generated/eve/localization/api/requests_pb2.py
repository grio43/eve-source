#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\localization\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.localization import message_pb2 as eve_dot_localization_dot_message__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/localization/api/requests.proto', package='eve.localization.message.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/localization/message/api', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/localization/api/requests.proto\x12\x1ceve.localization.message.api\x1a\x1eeve/localization/message.proto"P\n\x17GetLocalizedTextRequest\x125\n\x07message\x18\x01 \x01(\x0b2$.eve.localization.message.Identifier"(\n\x18GetLocalizedTextResponse\x12\x0c\n\x04text\x18\x01 \x01(\tBIZGgithub.com/ccpgames/eve-proto-go/generated/eve/localization/message/apib\x06proto3', dependencies=[eve_dot_localization_dot_message__pb2.DESCRIPTOR])
_GETLOCALIZEDTEXTREQUEST = _descriptor.Descriptor(name='GetLocalizedTextRequest', full_name='eve.localization.message.api.GetLocalizedTextRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='message', full_name='eve.localization.message.api.GetLocalizedTextRequest.message', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=101, serialized_end=181)
_GETLOCALIZEDTEXTRESPONSE = _descriptor.Descriptor(name='GetLocalizedTextResponse', full_name='eve.localization.message.api.GetLocalizedTextResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='text', full_name='eve.localization.message.api.GetLocalizedTextResponse.text', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=183, serialized_end=223)
_GETLOCALIZEDTEXTREQUEST.fields_by_name['message'].message_type = eve_dot_localization_dot_message__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetLocalizedTextRequest'] = _GETLOCALIZEDTEXTREQUEST
DESCRIPTOR.message_types_by_name['GetLocalizedTextResponse'] = _GETLOCALIZEDTEXTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetLocalizedTextRequest = _reflection.GeneratedProtocolMessageType('GetLocalizedTextRequest', (_message.Message,), {'DESCRIPTOR': _GETLOCALIZEDTEXTREQUEST,
 '__module__': 'eve.localization.api.requests_pb2'})
_sym_db.RegisterMessage(GetLocalizedTextRequest)
GetLocalizedTextResponse = _reflection.GeneratedProtocolMessageType('GetLocalizedTextResponse', (_message.Message,), {'DESCRIPTOR': _GETLOCALIZEDTEXTRESPONSE,
 '__module__': 'eve.localization.api.requests_pb2'})
_sym_db.RegisterMessage(GetLocalizedTextResponse)
DESCRIPTOR._options = None
