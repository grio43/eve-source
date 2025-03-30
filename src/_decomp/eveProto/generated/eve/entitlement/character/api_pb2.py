#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\entitlement\character\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.entitlement.character.ship import alliancelogo_pb2 as eve_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2
from eveProto.generated.eve.entitlement.character.ship import corplogo_pb2 as eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/entitlement/character/api.proto', package='eve.entitlement.character.api', syntax='proto3', serialized_options='ZHgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/character/api', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/entitlement/character/api.proto\x12\x1deve.entitlement.character.api\x1a1eve/entitlement/character/ship/alliancelogo.proto\x1a-eve/entitlement/character/ship/corplogo.proto"\xbe\x01\n\x11IsEntitledRequest\x12H\n\tcorp_logo\x18\x01 \x01(\x0b23.eve.entitlement.character.ship.corplogo.IdentifierH\x00\x12P\n\ralliance_logo\x18\x02 \x01(\x0b27.eve.entitlement.character.ship.alliancelogo.IdentifierH\x00B\r\n\x0bentitlement"\x14\n\x12IsEntitledResponseBJZHgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/character/apib\x06proto3', dependencies=[eve_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2.DESCRIPTOR, eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2.DESCRIPTOR])
_ISENTITLEDREQUEST = _descriptor.Descriptor(name='IsEntitledRequest', full_name='eve.entitlement.character.api.IsEntitledRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corp_logo', full_name='eve.entitlement.character.api.IsEntitledRequest.corp_logo', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='alliance_logo', full_name='eve.entitlement.character.api.IsEntitledRequest.alliance_logo', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='entitlement', full_name='eve.entitlement.character.api.IsEntitledRequest.entitlement', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=169, serialized_end=359)
_ISENTITLEDRESPONSE = _descriptor.Descriptor(name='IsEntitledResponse', full_name='eve.entitlement.character.api.IsEntitledResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=361, serialized_end=381)
_ISENTITLEDREQUEST.fields_by_name['corp_logo'].message_type = eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2._IDENTIFIER
_ISENTITLEDREQUEST.fields_by_name['alliance_logo'].message_type = eve_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2._IDENTIFIER
_ISENTITLEDREQUEST.oneofs_by_name['entitlement'].fields.append(_ISENTITLEDREQUEST.fields_by_name['corp_logo'])
_ISENTITLEDREQUEST.fields_by_name['corp_logo'].containing_oneof = _ISENTITLEDREQUEST.oneofs_by_name['entitlement']
_ISENTITLEDREQUEST.oneofs_by_name['entitlement'].fields.append(_ISENTITLEDREQUEST.fields_by_name['alliance_logo'])
_ISENTITLEDREQUEST.fields_by_name['alliance_logo'].containing_oneof = _ISENTITLEDREQUEST.oneofs_by_name['entitlement']
DESCRIPTOR.message_types_by_name['IsEntitledRequest'] = _ISENTITLEDREQUEST
DESCRIPTOR.message_types_by_name['IsEntitledResponse'] = _ISENTITLEDRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
IsEntitledRequest = _reflection.GeneratedProtocolMessageType('IsEntitledRequest', (_message.Message,), {'DESCRIPTOR': _ISENTITLEDREQUEST,
 '__module__': 'eve.entitlement.character.api_pb2'})
_sym_db.RegisterMessage(IsEntitledRequest)
IsEntitledResponse = _reflection.GeneratedProtocolMessageType('IsEntitledResponse', (_message.Message,), {'DESCRIPTOR': _ISENTITLEDRESPONSE,
 '__module__': 'eve.entitlement.character.api_pb2'})
_sym_db.RegisterMessage(IsEntitledResponse)
DESCRIPTOR._options = None
