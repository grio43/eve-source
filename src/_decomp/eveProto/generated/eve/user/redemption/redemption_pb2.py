#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\user\redemption\redemption_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from eveProto.generated.eve.user.redemption import token_pb2 as eve_dot_user_dot_redemption_dot_token__pb2
from eveProto.generated.eve.user import user_pb2 as eve_dot_user_dot_user__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/user/redemption/redemption.proto', package='eve.user.redemption', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/user/redemption', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/user/redemption/redemption.proto\x12\x13eve.user.redemption\x1a\x1deve/character/character.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto\x1a\x1feve/user/redemption/token.proto\x1a\x13eve/user/user.proto"@\n\x1aGetRedeemableTokensRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier"\xf0\x01\n\x1bGetRedeemableTokensResponse\x12F\n\x06tokens\x18\x01 \x03(\x0b26.eve.user.redemption.GetRedeemableTokensResponse.Token\x1a\x88\x01\n\x05Token\x129\n\nuser_token\x18\x01 \x01(\x0b2%.eve.user.redemption.token.Identifier\x12D\n\x15user_token_attributes\x18\x02 \x01(\x0b2%.eve.user.redemption.token.Attributes"\x86\x02\n\x13RedeemTokensRequest\x12"\n\x04user\x18\x01 \x01(\x0b2\x14.eve.user.Identifier\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.Identifier\x12*\n\x07station\x18\x03 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\x04 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x125\n\x06tokens\x18\x05 \x03(\x0b2%.eve.user.redemption.token.IdentifierB\n\n\x08location"\x16\n\x14RedeemTokensResponse"T\n\x1cInsertRedeemableTokenRequest\x124\n\x05token\x18\x01 \x01(\x0b2%.eve.user.redemption.token.Attributes"\x1f\n\x1dInsertRedeemableTokenResponseB@Z>github.com/ccpgames/eve-proto-go/generated/eve/user/redemptionb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 eve_dot_user_dot_redemption_dot_token__pb2.DESCRIPTOR,
 eve_dot_user_dot_user__pb2.DESCRIPTOR])
_GETREDEEMABLETOKENSREQUEST = _descriptor.Descriptor(name='GetRedeemableTokensRequest', full_name='eve.user.redemption.GetRedeemableTokensRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.redemption.GetRedeemableTokensRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=204, serialized_end=268)
_GETREDEEMABLETOKENSRESPONSE_TOKEN = _descriptor.Descriptor(name='Token', full_name='eve.user.redemption.GetRedeemableTokensResponse.Token', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user_token', full_name='eve.user.redemption.GetRedeemableTokensResponse.Token.user_token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='user_token_attributes', full_name='eve.user.redemption.GetRedeemableTokensResponse.Token.user_token_attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=375, serialized_end=511)
_GETREDEEMABLETOKENSRESPONSE = _descriptor.Descriptor(name='GetRedeemableTokensResponse', full_name='eve.user.redemption.GetRedeemableTokensResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='tokens', full_name='eve.user.redemption.GetRedeemableTokensResponse.tokens', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETREDEEMABLETOKENSRESPONSE_TOKEN], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=271, serialized_end=511)
_REDEEMTOKENSREQUEST = _descriptor.Descriptor(name='RedeemTokensRequest', full_name='eve.user.redemption.RedeemTokensRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='user', full_name='eve.user.redemption.RedeemTokensRequest.user', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character', full_name='eve.user.redemption.RedeemTokensRequest.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.user.redemption.RedeemTokensRequest.station', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.user.redemption.RedeemTokensRequest.structure', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='tokens', full_name='eve.user.redemption.RedeemTokensRequest.tokens', index=4, number=5, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='location', full_name='eve.user.redemption.RedeemTokensRequest.location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=514, serialized_end=776)
_REDEEMTOKENSRESPONSE = _descriptor.Descriptor(name='RedeemTokensResponse', full_name='eve.user.redemption.RedeemTokensResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=778, serialized_end=800)
_INSERTREDEEMABLETOKENREQUEST = _descriptor.Descriptor(name='InsertRedeemableTokenRequest', full_name='eve.user.redemption.InsertRedeemableTokenRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='token', full_name='eve.user.redemption.InsertRedeemableTokenRequest.token', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=802, serialized_end=886)
_INSERTREDEEMABLETOKENRESPONSE = _descriptor.Descriptor(name='InsertRedeemableTokenResponse', full_name='eve.user.redemption.InsertRedeemableTokenResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=888, serialized_end=919)
_GETREDEEMABLETOKENSREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_GETREDEEMABLETOKENSRESPONSE_TOKEN.fields_by_name['user_token'].message_type = eve_dot_user_dot_redemption_dot_token__pb2._IDENTIFIER
_GETREDEEMABLETOKENSRESPONSE_TOKEN.fields_by_name['user_token_attributes'].message_type = eve_dot_user_dot_redemption_dot_token__pb2._ATTRIBUTES
_GETREDEEMABLETOKENSRESPONSE_TOKEN.containing_type = _GETREDEEMABLETOKENSRESPONSE
_GETREDEEMABLETOKENSRESPONSE.fields_by_name['tokens'].message_type = _GETREDEEMABLETOKENSRESPONSE_TOKEN
_REDEEMTOKENSREQUEST.fields_by_name['user'].message_type = eve_dot_user_dot_user__pb2._IDENTIFIER
_REDEEMTOKENSREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REDEEMTOKENSREQUEST.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_REDEEMTOKENSREQUEST.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_REDEEMTOKENSREQUEST.fields_by_name['tokens'].message_type = eve_dot_user_dot_redemption_dot_token__pb2._IDENTIFIER
_REDEEMTOKENSREQUEST.oneofs_by_name['location'].fields.append(_REDEEMTOKENSREQUEST.fields_by_name['station'])
_REDEEMTOKENSREQUEST.fields_by_name['station'].containing_oneof = _REDEEMTOKENSREQUEST.oneofs_by_name['location']
_REDEEMTOKENSREQUEST.oneofs_by_name['location'].fields.append(_REDEEMTOKENSREQUEST.fields_by_name['structure'])
_REDEEMTOKENSREQUEST.fields_by_name['structure'].containing_oneof = _REDEEMTOKENSREQUEST.oneofs_by_name['location']
_INSERTREDEEMABLETOKENREQUEST.fields_by_name['token'].message_type = eve_dot_user_dot_redemption_dot_token__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRedeemableTokensRequest'] = _GETREDEEMABLETOKENSREQUEST
DESCRIPTOR.message_types_by_name['GetRedeemableTokensResponse'] = _GETREDEEMABLETOKENSRESPONSE
DESCRIPTOR.message_types_by_name['RedeemTokensRequest'] = _REDEEMTOKENSREQUEST
DESCRIPTOR.message_types_by_name['RedeemTokensResponse'] = _REDEEMTOKENSRESPONSE
DESCRIPTOR.message_types_by_name['InsertRedeemableTokenRequest'] = _INSERTREDEEMABLETOKENREQUEST
DESCRIPTOR.message_types_by_name['InsertRedeemableTokenResponse'] = _INSERTREDEEMABLETOKENRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRedeemableTokensRequest = _reflection.GeneratedProtocolMessageType('GetRedeemableTokensRequest', (_message.Message,), {'DESCRIPTOR': _GETREDEEMABLETOKENSREQUEST,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(GetRedeemableTokensRequest)
GetRedeemableTokensResponse = _reflection.GeneratedProtocolMessageType('GetRedeemableTokensResponse', (_message.Message,), {'Token': _reflection.GeneratedProtocolMessageType('Token', (_message.Message,), {'DESCRIPTOR': _GETREDEEMABLETOKENSRESPONSE_TOKEN,
           '__module__': 'eve.user.redemption.redemption_pb2'}),
 'DESCRIPTOR': _GETREDEEMABLETOKENSRESPONSE,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(GetRedeemableTokensResponse)
_sym_db.RegisterMessage(GetRedeemableTokensResponse.Token)
RedeemTokensRequest = _reflection.GeneratedProtocolMessageType('RedeemTokensRequest', (_message.Message,), {'DESCRIPTOR': _REDEEMTOKENSREQUEST,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(RedeemTokensRequest)
RedeemTokensResponse = _reflection.GeneratedProtocolMessageType('RedeemTokensResponse', (_message.Message,), {'DESCRIPTOR': _REDEEMTOKENSRESPONSE,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(RedeemTokensResponse)
InsertRedeemableTokenRequest = _reflection.GeneratedProtocolMessageType('InsertRedeemableTokenRequest', (_message.Message,), {'DESCRIPTOR': _INSERTREDEEMABLETOKENREQUEST,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(InsertRedeemableTokenRequest)
InsertRedeemableTokenResponse = _reflection.GeneratedProtocolMessageType('InsertRedeemableTokenResponse', (_message.Message,), {'DESCRIPTOR': _INSERTREDEEMABLETOKENRESPONSE,
 '__module__': 'eve.user.redemption.redemption_pb2'})
_sym_db.RegisterMessage(InsertRedeemableTokenResponse)
DESCRIPTOR._options = None
