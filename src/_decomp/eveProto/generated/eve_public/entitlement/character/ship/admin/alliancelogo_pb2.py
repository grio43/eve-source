#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\entitlement\character\ship\admin\alliancelogo_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.entitlement.character.ship import alliancelogo_pb2 as eve__public_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/entitlement/character/ship/admin/alliancelogo.proto', package='eve_public.entitlement.character.ship.admin.alliancelogo', syntax='proto3', serialized_options='Zcgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/character/ship/admin/alliancelogo', create_key=_descriptor._internal_create_key, serialized_pb='\n>eve_public/entitlement/character/ship/admin/alliancelogo.proto\x128eve_public.entitlement.character.ship.admin.alliancelogo\x1a8eve_public/entitlement/character/ship/alliancelogo.proto"c\n\x0cGrantRequest\x12S\n\x0bentitlement\x18\x01 \x01(\x0b2>.eve_public.entitlement.character.ship.alliancelogo.Identifier"\x0f\n\rGrantResponse"d\n\rRevokeRequest\x12S\n\x0bentitlement\x18\x01 \x01(\x0b2>.eve_public.entitlement.character.ship.alliancelogo.Identifier"\x10\n\x0eRevokeResponseBeZcgithub.com/ccpgames/eve-proto-go/generated/eve_public/entitlement/character/ship/admin/alliancelogob\x06proto3', dependencies=[eve__public_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2.DESCRIPTOR])
_GRANTREQUEST = _descriptor.Descriptor(name='GrantRequest', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.GrantRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.GrantRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=182, serialized_end=281)
_GRANTRESPONSE = _descriptor.Descriptor(name='GrantResponse', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.GrantResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=283, serialized_end=298)
_REVOKEREQUEST = _descriptor.Descriptor(name='RevokeRequest', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.RevokeRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='entitlement', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.RevokeRequest.entitlement', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=300, serialized_end=400)
_REVOKERESPONSE = _descriptor.Descriptor(name='RevokeResponse', full_name='eve_public.entitlement.character.ship.admin.alliancelogo.RevokeResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=402, serialized_end=418)
_GRANTREQUEST.fields_by_name['entitlement'].message_type = eve__public_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2._IDENTIFIER
_REVOKEREQUEST.fields_by_name['entitlement'].message_type = eve__public_dot_entitlement_dot_character_dot_ship_dot_alliancelogo__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GrantRequest'] = _GRANTREQUEST
DESCRIPTOR.message_types_by_name['GrantResponse'] = _GRANTRESPONSE
DESCRIPTOR.message_types_by_name['RevokeRequest'] = _REVOKEREQUEST
DESCRIPTOR.message_types_by_name['RevokeResponse'] = _REVOKERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GrantRequest = _reflection.GeneratedProtocolMessageType('GrantRequest', (_message.Message,), {'DESCRIPTOR': _GRANTREQUEST,
 '__module__': 'eve_public.entitlement.character.ship.admin.alliancelogo_pb2'})
_sym_db.RegisterMessage(GrantRequest)
GrantResponse = _reflection.GeneratedProtocolMessageType('GrantResponse', (_message.Message,), {'DESCRIPTOR': _GRANTRESPONSE,
 '__module__': 'eve_public.entitlement.character.ship.admin.alliancelogo_pb2'})
_sym_db.RegisterMessage(GrantResponse)
RevokeRequest = _reflection.GeneratedProtocolMessageType('RevokeRequest', (_message.Message,), {'DESCRIPTOR': _REVOKEREQUEST,
 '__module__': 'eve_public.entitlement.character.ship.admin.alliancelogo_pb2'})
_sym_db.RegisterMessage(RevokeRequest)
RevokeResponse = _reflection.GeneratedProtocolMessageType('RevokeResponse', (_message.Message,), {'DESCRIPTOR': _REVOKERESPONSE,
 '__module__': 'eve_public.entitlement.character.ship.admin.alliancelogo_pb2'})
_sym_db.RegisterMessage(RevokeResponse)
DESCRIPTOR._options = None
