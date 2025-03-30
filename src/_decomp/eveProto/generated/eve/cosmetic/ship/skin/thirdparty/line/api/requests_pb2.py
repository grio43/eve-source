#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\line\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.line import line_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/line/api/requests.proto', package='eve.cosmetic.ship.skin.thirdparty.line.api', syntax='proto3', serialized_options='ZUgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/line/api', create_key=_descriptor._internal_create_key, serialized_pb='\n9eve/cosmetic/ship/skin/thirdparty/line/api/requests.proto\x12*eve.cosmetic.ship.skin.thirdparty.line.api\x1a1eve/cosmetic/ship/skin/thirdparty/line/line.proto"N\n\nGetRequest\x12@\n\x04line\x18\x01 \x01(\x0b22.eve.cosmetic.ship.skin.thirdparty.line.Identifier"U\n\x0bGetResponse\x12F\n\nattributes\x18\x01 \x01(\x0b22.eve.cosmetic.ship.skin.thirdparty.line.AttributesBWZUgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/line/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='line', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.GetRequest.line', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=156, serialized_end=234)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.GetResponse.attributes', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=236, serialized_end=321)
_GETREQUEST.fields_by_name['line'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.line.api.requests_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.line.api.requests_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
