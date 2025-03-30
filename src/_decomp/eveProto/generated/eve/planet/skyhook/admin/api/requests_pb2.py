#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\planet\skyhook\admin\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.planet.skyhook import skyhook_pb2 as eve_dot_planet_dot_skyhook_dot_skyhook__pb2
from eveProto.generated.eve.quasar.admin import admin_pb2 as eve_dot_quasar_dot_admin_dot_admin__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/planet/skyhook/admin/api/requests.proto', package='eve.planet.skyhook.admin.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve/planet/skyhook/admin/api', create_key=_descriptor._internal_create_key, serialized_pb='\n+eve/planet/skyhook/admin/api/requests.proto\x12\x1ceve.planet.skyhook.admin.api\x1a!eve/corporation/corporation.proto\x1a eve/planet/skyhook/skyhook.proto\x1a\x1ceve/quasar/admin/admin.proto\x1a!eve/solarsystem/solarsystem.proto"\xd6\x01\n\x12ChangeOwnerRequest\x12*\n\x07context\x18\x01 \x01(\x0b2\x19.eve.quasar.admin.Context\x12/\n\x07skyhook\x18\x02 \x01(\x0b2\x1e.eve.planet.skyhook.Identifier\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x120\n\x0bcorporation\x18\x04 \x01(\x0b2\x1b.eve.corporation.Identifier"\x15\n\x13ChangeOwnerResponseBIZGgithub.com/ccpgames/eve-proto-go/generated/eve/planet/skyhook/admin/apib\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_planet_dot_skyhook_dot_skyhook__pb2.DESCRIPTOR,
 eve_dot_quasar_dot_admin_dot_admin__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR])
_CHANGEOWNERREQUEST = _descriptor.Descriptor(name='ChangeOwnerRequest', full_name='eve.planet.skyhook.admin.api.ChangeOwnerRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.planet.skyhook.admin.api.ChangeOwnerRequest.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skyhook', full_name='eve.planet.skyhook.admin.api.ChangeOwnerRequest.skyhook', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.planet.skyhook.admin.api.ChangeOwnerRequest.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.planet.skyhook.admin.api.ChangeOwnerRequest.corporation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=212, serialized_end=426)
_CHANGEOWNERRESPONSE = _descriptor.Descriptor(name='ChangeOwnerResponse', full_name='eve.planet.skyhook.admin.api.ChangeOwnerResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=428, serialized_end=449)
_CHANGEOWNERREQUEST.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
_CHANGEOWNERREQUEST.fields_by_name['skyhook'].message_type = eve_dot_planet_dot_skyhook_dot_skyhook__pb2._IDENTIFIER
_CHANGEOWNERREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_CHANGEOWNERREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ChangeOwnerRequest'] = _CHANGEOWNERREQUEST
DESCRIPTOR.message_types_by_name['ChangeOwnerResponse'] = _CHANGEOWNERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ChangeOwnerRequest = _reflection.GeneratedProtocolMessageType('ChangeOwnerRequest', (_message.Message,), {'DESCRIPTOR': _CHANGEOWNERREQUEST,
 '__module__': 'eve.planet.skyhook.admin.api.requests_pb2'})
_sym_db.RegisterMessage(ChangeOwnerRequest)
ChangeOwnerResponse = _reflection.GeneratedProtocolMessageType('ChangeOwnerResponse', (_message.Message,), {'DESCRIPTOR': _CHANGEOWNERRESPONSE,
 '__module__': 'eve.planet.skyhook.admin.api.requests_pb2'})
_sym_db.RegisterMessage(ChangeOwnerResponse)
DESCRIPTOR._options = None
