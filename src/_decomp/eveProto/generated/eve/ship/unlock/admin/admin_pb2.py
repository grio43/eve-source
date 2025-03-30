#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\ship\unlock\admin\admin_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/ship/unlock/admin/admin.proto', package='eve.ship.unlock.admin', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/ship/unlock/admin', create_key=_descriptor._internal_create_key, serialized_pb='\n!eve/ship/unlock/admin/admin.proto\x12\x15eve.ship.unlock.admin\x1a\x1deve/character/character.proto\x1a\x18eve/ship/ship_type.proto"r\n\x0cResetRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x124\n\x12unlocked_ship_type\x18\x02 \x01(\x0b2\x18.eve.shiptype.Identifier"\x0f\n\rResetResponse"?\n\x0fResetAllRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"\x12\n\x10ResetAllResponseBBZ@github.com/ccpgames/eve-proto-go/generated/eve/ship/unlock/adminb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_RESETREQUEST = _descriptor.Descriptor(name='ResetRequest', full_name='eve.ship.unlock.admin.ResetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.unlock.admin.ResetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='unlocked_ship_type', full_name='eve.ship.unlock.admin.ResetRequest.unlocked_ship_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=117, serialized_end=231)
_RESETRESPONSE = _descriptor.Descriptor(name='ResetResponse', full_name='eve.ship.unlock.admin.ResetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=233, serialized_end=248)
_RESETALLREQUEST = _descriptor.Descriptor(name='ResetAllRequest', full_name='eve.ship.unlock.admin.ResetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.ship.unlock.admin.ResetAllRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=250, serialized_end=313)
_RESETALLRESPONSE = _descriptor.Descriptor(name='ResetAllResponse', full_name='eve.ship.unlock.admin.ResetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=315, serialized_end=333)
_RESETREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_RESETREQUEST.fields_by_name['unlocked_ship_type'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_RESETALLREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ResetRequest'] = _RESETREQUEST
DESCRIPTOR.message_types_by_name['ResetResponse'] = _RESETRESPONSE
DESCRIPTOR.message_types_by_name['ResetAllRequest'] = _RESETALLREQUEST
DESCRIPTOR.message_types_by_name['ResetAllResponse'] = _RESETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ResetRequest = _reflection.GeneratedProtocolMessageType('ResetRequest', (_message.Message,), {'DESCRIPTOR': _RESETREQUEST,
 '__module__': 'eve.ship.unlock.admin.admin_pb2'})
_sym_db.RegisterMessage(ResetRequest)
ResetResponse = _reflection.GeneratedProtocolMessageType('ResetResponse', (_message.Message,), {'DESCRIPTOR': _RESETRESPONSE,
 '__module__': 'eve.ship.unlock.admin.admin_pb2'})
_sym_db.RegisterMessage(ResetResponse)
ResetAllRequest = _reflection.GeneratedProtocolMessageType('ResetAllRequest', (_message.Message,), {'DESCRIPTOR': _RESETALLREQUEST,
 '__module__': 'eve.ship.unlock.admin.admin_pb2'})
_sym_db.RegisterMessage(ResetAllRequest)
ResetAllResponse = _reflection.GeneratedProtocolMessageType('ResetAllResponse', (_message.Message,), {'DESCRIPTOR': _RESETALLRESPONSE,
 '__module__': 'eve.ship.unlock.admin.admin_pb2'})
_sym_db.RegisterMessage(ResetAllResponse)
DESCRIPTOR._options = None
