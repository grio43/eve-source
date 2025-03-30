#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\entitlement\character\ship\admin\corplogo_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.entitlement.character.ship import corplogo_pb2 as eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/entitlement/character/ship/admin/corplogo.proto', package='eve.entitlement.character.ship.admin.corplogo', syntax='proto3', serialized_options='ZXgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/character/ship/admin/corplogo', create_key=_descriptor._internal_create_key, serialized_pb='\n3eve/entitlement/character/ship/admin/corplogo.proto\x12-eve.entitlement.character.ship.admin.corplogo\x1a-eve/entitlement/character/ship/corplogo.proto"X\n\x0cGrantRequest\x12H\n\x0bentitlement\x18\x01 \x01(\x0b23.eve.entitlement.character.ship.corplogo.Identifier"\x0f\n\rGrantResponse"Y\n\rRevokeRequest\x12H\n\x0bentitlement\x18\x01 \x01(\x0b23.eve.entitlement.character.ship.corplogo.Identifier"\x10\n\x0eRevokeResponseBZZXgithub.com/ccpgames/eve-proto-go/generated/eve/entitlement/character/ship/admin/corplogob\x06proto3', dependencies=[eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2.DESCRIPTOR])
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve.entitlement.character.ship.admin.corplogo.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve.entitlement.character.ship.admin.corplogo.GrantRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=149, serialized_end=237)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve.entitlement.character.ship.admin.corplogo.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=239, serialized_end=254)
_REVOKEREQUEST = _descriptor.Descriptor(name='RevokeRequest', full_name='eve.entitlement.character.ship.admin.corplogo.RevokeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve.entitlement.character.ship.admin.corplogo.RevokeRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=256, serialized_end=345)
_REVOKERESPONSE = _descriptor.Descriptor(name='RevokeResponse', full_name='eve.entitlement.character.ship.admin.corplogo.RevokeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=347, serialized_end=363)
_GRANTREQUEST.fields_by_name['entitlement'].message_type = eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2._IDENTIFIER
_REVOKEREQUEST.fields_by_name['entitlement'].message_type = eve_dot_entitlement_dot_character_dot_ship_dot_corplogo__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
DESCRIPTOR.message_types_by_name['RevokeRequest'] = _REVOKEREQUEST
DESCRIPTOR.message_types_by_name['RevokeResponse'] = _REVOKERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve.entitlement.character.ship.admin.corplogo_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve.entitlement.character.ship.admin.corplogo_pb2'})
_sym_db.RegisterMessage(GrantResponse)
RevokeRequest = _reflection.GeneratedProtocolMessageType('RevokeRequest', (_message.Message,), {'DESCRIPTOR': _REVOKEREQUEST,
 '__module__': 'eve.entitlement.character.ship.admin.corplogo_pb2'})
_sym_db.RegisterMessage(RevokeRequest)
RevokeResponse = _reflection.GeneratedProtocolMessageType('RevokeResponse', (_message.Message,), {'DESCRIPTOR': _REVOKERESPONSE,
 '__module__': 'eve.entitlement.character.ship.admin.corplogo_pb2'})
_sym_db.RegisterMessage(RevokeResponse)
DESCRIPTOR._options = None
