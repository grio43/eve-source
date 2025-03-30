#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\sovereignty\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.sovereignty.hub import hub_pb2 as eve_dot_sovereignty_dot_hub_dot_hub__pb2
from eveProto.generated.eve.sovereignty import infrastructurehub_pb2 as eve_dot_sovereignty_dot_infrastructurehub__pb2
from eveProto.generated.eve.sovereignty import versionmanifest_pb2 as eve_dot_sovereignty_dot_versionmanifest__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/sovereignty/api/requests.proto', package='eve.sovereignty.api', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/sovereignty/api', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/sovereignty/api/requests.proto\x12\x13eve.sovereignty.api\x1a\x1beve/alliance/alliance.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1deve/sovereignty/hub/hub.proto\x1a\'eve/sovereignty/infrastructurehub.proto\x1a%eve/sovereignty/versionmanifest.proto"D\n\x0fGetClaimRequest\x121\n\x0csolar_system\x18\x01 \x01(\x0b2\x1b.eve.solarsystem.Identifier"\xb5\x02\n\x10GetClaimResponse\x12\x13\n\tunclaimed\x18\x01 \x01(\x08H\x00\x12>\n\x07claimed\x18\x02 \x01(\x0b2+.eve.sovereignty.api.GetClaimResponse.ClaimH\x00\x1a\xbc\x01\n\x05Claim\x12*\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.Identifier\x12K\n\x12infrastructure_hub\x18\x02 \x01(\x0b2-.eve.sovereignty.infrastructurehub.IdentifierH\x00\x12.\n\x03hub\x18\x03 \x01(\x0b2\x1f.eve.sovereignty.hub.IdentifierH\x00B\n\n\x08hub_typeB\r\n\x0bclaim_state"\x1b\n\x19GetVersionManifestRequest"X\n\x1aGetVersionManifestResponse\x12:\n\x10version_manifest\x18\x01 \x01(\x0b2 .eve.sovereignty.VersionManifestB@Z>github.com/ccpgames/eve-proto-go/generated/eve/sovereignty/apib\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_sovereignty_dot_hub_dot_hub__pb2.DESCRIPTOR,
 eve_dot_sovereignty_dot_infrastructurehub__pb2.DESCRIPTOR,
 eve_dot_sovereignty_dot_versionmanifest__pb2.DESCRIPTOR])
_GETCLAIMREQUEST = _descriptor.Descriptor(name='GetClaimRequest', full_name='eve.sovereignty.api.GetClaimRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='solar_system', full_name='eve.sovereignty.api.GetClaimRequest.solar_system', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=234, serialized_end=302)
_GETCLAIMRESPONSE_CLAIM = _descriptor.Descriptor(name='Claim', full_name='eve.sovereignty.api.GetClaimResponse.Claim', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.sovereignty.api.GetClaimResponse.Claim.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='infrastructure_hub', full_name='eve.sovereignty.api.GetClaimResponse.Claim.infrastructure_hub', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='hub', full_name='eve.sovereignty.api.GetClaimResponse.Claim.hub', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='hub_type', full_name='eve.sovereignty.api.GetClaimResponse.Claim.hub_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=411, serialized_end=599)
_GETCLAIMRESPONSE = _descriptor.Descriptor(name='GetClaimResponse', full_name='eve.sovereignty.api.GetClaimResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unclaimed', full_name='eve.sovereignty.api.GetClaimResponse.unclaimed', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='claimed', full_name='eve.sovereignty.api.GetClaimResponse.claimed', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETCLAIMRESPONSE_CLAIM], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='claim_state', full_name='eve.sovereignty.api.GetClaimResponse.claim_state', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=305, serialized_end=614)
_GETVERSIONMANIFESTREQUEST = _descriptor.Descriptor(name='GetVersionManifestRequest', full_name='eve.sovereignty.api.GetVersionManifestRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=616, serialized_end=643)
_GETVERSIONMANIFESTRESPONSE = _descriptor.Descriptor(name='GetVersionManifestResponse', full_name='eve.sovereignty.api.GetVersionManifestResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='version_manifest', full_name='eve.sovereignty.api.GetVersionManifestResponse.version_manifest', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=645, serialized_end=733)
_GETCLAIMREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_GETCLAIMRESPONSE_CLAIM.fields_by_name['alliance'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_GETCLAIMRESPONSE_CLAIM.fields_by_name['infrastructure_hub'].message_type = eve_dot_sovereignty_dot_infrastructurehub__pb2._IDENTIFIER
_GETCLAIMRESPONSE_CLAIM.fields_by_name['hub'].message_type = eve_dot_sovereignty_dot_hub_dot_hub__pb2._IDENTIFIER
_GETCLAIMRESPONSE_CLAIM.containing_type = _GETCLAIMRESPONSE
_GETCLAIMRESPONSE_CLAIM.oneofs_by_name['hub_type'].fields.append(_GETCLAIMRESPONSE_CLAIM.fields_by_name['infrastructure_hub'])
_GETCLAIMRESPONSE_CLAIM.fields_by_name['infrastructure_hub'].containing_oneof = _GETCLAIMRESPONSE_CLAIM.oneofs_by_name['hub_type']
_GETCLAIMRESPONSE_CLAIM.oneofs_by_name['hub_type'].fields.append(_GETCLAIMRESPONSE_CLAIM.fields_by_name['hub'])
_GETCLAIMRESPONSE_CLAIM.fields_by_name['hub'].containing_oneof = _GETCLAIMRESPONSE_CLAIM.oneofs_by_name['hub_type']
_GETCLAIMRESPONSE.fields_by_name['claimed'].message_type = _GETCLAIMRESPONSE_CLAIM
_GETCLAIMRESPONSE.oneofs_by_name['claim_state'].fields.append(_GETCLAIMRESPONSE.fields_by_name['unclaimed'])
_GETCLAIMRESPONSE.fields_by_name['unclaimed'].containing_oneof = _GETCLAIMRESPONSE.oneofs_by_name['claim_state']
_GETCLAIMRESPONSE.oneofs_by_name['claim_state'].fields.append(_GETCLAIMRESPONSE.fields_by_name['claimed'])
_GETCLAIMRESPONSE.fields_by_name['claimed'].containing_oneof = _GETCLAIMRESPONSE.oneofs_by_name['claim_state']
_GETVERSIONMANIFESTRESPONSE.fields_by_name['version_manifest'].message_type = eve_dot_sovereignty_dot_versionmanifest__pb2._VERSIONMANIFEST
DESCRIPTOR.message_types_by_name['GetClaimRequest'] = _GETCLAIMREQUEST
DESCRIPTOR.message_types_by_name['GetClaimResponse'] = _GETCLAIMRESPONSE
DESCRIPTOR.message_types_by_name['GetVersionManifestRequest'] = _GETVERSIONMANIFESTREQUEST
DESCRIPTOR.message_types_by_name['GetVersionManifestResponse'] = _GETVERSIONMANIFESTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetClaimRequest = _reflection.GeneratedProtocolMessageType('GetClaimRequest', (_message.Message,), {'DESCRIPTOR': _GETCLAIMREQUEST,
 '__module__': 'eve.sovereignty.api.requests_pb2'})
_sym_db.RegisterMessage(GetClaimRequest)
GetClaimResponse = _reflection.GeneratedProtocolMessageType('GetClaimResponse', (_message.Message,), {'Claim': _reflection.GeneratedProtocolMessageType('Claim', (_message.Message,), {'DESCRIPTOR': _GETCLAIMRESPONSE_CLAIM,
           '__module__': 'eve.sovereignty.api.requests_pb2'}),
 'DESCRIPTOR': _GETCLAIMRESPONSE,
 '__module__': 'eve.sovereignty.api.requests_pb2'})
_sym_db.RegisterMessage(GetClaimResponse)
_sym_db.RegisterMessage(GetClaimResponse.Claim)
GetVersionManifestRequest = _reflection.GeneratedProtocolMessageType('GetVersionManifestRequest', (_message.Message,), {'DESCRIPTOR': _GETVERSIONMANIFESTREQUEST,
 '__module__': 'eve.sovereignty.api.requests_pb2'})
_sym_db.RegisterMessage(GetVersionManifestRequest)
GetVersionManifestResponse = _reflection.GeneratedProtocolMessageType('GetVersionManifestResponse', (_message.Message,), {'DESCRIPTOR': _GETVERSIONMANIFESTRESPONSE,
 '__module__': 'eve.sovereignty.api.requests_pb2'})
_sym_db.RegisterMessage(GetVersionManifestResponse)
DESCRIPTOR._options = None
