#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\structure\paintwork\license\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.corporation import loyalty_pb2 as eve_dot_corporation_dot_loyalty__pb2
from eveProto.generated.eve.cosmetic.structure.paintwork.license import license_pb2 as eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2
from eveProto.generated.eve.cosmetic.structure.paintwork import paintwork_pb2 as eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2
from eveProto.generated.eve.quasar.admin import admin_pb2 as eve_dot_quasar_dot_admin_dot_admin__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from eveProto.generated.eve.structure import structure_type_pb2 as eve_dot_structure_dot_structure__type__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/structure/paintwork/license/api/api.proto', package='eve.cosmetic.structure.paintwork.license.api', syntax='proto3', serialized_options='ZWgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/license/api', create_key=_descriptor._internal_create_key, serialized_pb='\n6eve/cosmetic/structure/paintwork/license/api/api.proto\x12,eve.cosmetic.structure.paintwork.license.api\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x1deve/corporation/loyalty.proto\x1a6eve/cosmetic/structure/paintwork/license/license.proto\x1a0eve/cosmetic/structure/paintwork/paintwork.proto\x1a\x1ceve/quasar/admin/admin.proto\x1a\x1deve/structure/structure.proto\x1a"eve/structure/structure_type.proto\x1a\x1egoogle/protobuf/duration.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xf5\x02\n\x06Issued\x12@\n\x02id\x18\x01 \x01(\x0b24.eve.cosmetic.structure.paintwork.license.Identifier\x12H\n\nattributes\x18\x02 \x01(\x0b24.eve.cosmetic.structure.paintwork.license.Attributes\x120\n\tstructure\x18\x03 \x01(\x0b2\x19.eve.structure.IdentifierB\x02\x18\x01\x12F\n\tpaintwork\x18\x04 \x01(\x0b23.eve.cosmetic.structure.paintwork.SlotConfiguration\x12.\n\x05price\x18\x05 \x01(\x0b2\x1f.eve.corporation.loyalty.Points\x125\n\x0estructure_type\x18\x06 \x01(\x0b2\x1d.eve.structuretype.Identifier"\xab\x02\n\rReceiptIssued\x12,\n\tactivator\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x120\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.Identifier\x12*\n\x06issued\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12+\n\x08duration\x18\x04 \x01(\x0b2\x19.google.protobuf.Duration\x12.\n\x05price\x18\x05 \x01(\x0b2\x1f.eve.corporation.loyalty.Points\x12-\n\nstructures\x18\x06 \x03(\x0b2\x19.eve.structure.Identifier:\x02\x18\x01"\xa6\n\n\x07Revoked\x12E\n\x07license\x18\x01 \x01(\x0b24.eve.cosmetic.structure.paintwork.license.Identifier\x12a\n\x10character_action\x18\x02 \x01(\x0b2E.eve.cosmetic.structure.paintwork.license.api.Revoked.CharacterActionH\x00\x12Y\n\x0cadmin_action\x18\x03 \x01(\x0b2A.eve.cosmetic.structure.paintwork.license.api.Revoked.AdminActionH\x00\x12P\n\x07expired\x18\x04 \x01(\x0b2=.eve.cosmetic.structure.paintwork.license.api.Revoked.ExpiredH\x00\x12`\n\x10upkeep_low_power\x18\x05 \x01(\x0b2D.eve.cosmetic.structure.paintwork.license.api.Revoked.UpkeepLowPowerH\x00\x12a\n\x10upkeep_abandoned\x18\x06 \x01(\x0b2E.eve.cosmetic.structure.paintwork.license.api.Revoked.UpkeepAbandonedH\x00\x12k\n\x15ownership_transferred\x18\x07 \x01(\x0b2J.eve.cosmetic.structure.paintwork.license.api.Revoked.OwnershipTransferredH\x00\x12b\n\x0elicense_issued\x18\x08 \x01(\x0b2H.eve.cosmetic.structure.paintwork.license.api.Revoked.NewerLicenseIssuedH\x00\x12]\n\tdestroyed\x18\t \x01(\x0b2H.eve.cosmetic.structure.paintwork.license.api.Revoked.StructureDestroyedH\x00\x12_\n\nunanchored\x18\n \x01(\x0b2I.eve.cosmetic.structure.paintwork.license.api.Revoked.StructureUnanchoredH\x00\x12,\n\tstructure\x18\x0b \x01(\x0b2\x19.eve.structure.Identifier\x1aA\n\x0fCharacterAction\x12.\n\x0bdeactivator\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x1a9\n\x0bAdminAction\x12*\n\x07context\x18\x01 \x01(\x0b2\x19.eve.quasar.admin.Context\x1a8\n\x07Expired\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x1a\x10\n\x0eUpkeepLowPower\x1a\x11\n\x0fUpkeepAbandoned\x1a\x16\n\x14OwnershipTransferred\x1a\x14\n\x12NewerLicenseIssued\x1a\x14\n\x12StructureDestroyed\x1a\x15\n\x13StructureUnanchoredB\x08\n\x06reason"S\n\x1fGetAllOwnedByCorporationRequest\x120\n\x0bcorporation\x18\x01 \x01(\x0b2\x1b.eve.corporation.Identifier"\xac\x02\n GetAllOwnedByCorporationResponse\x12h\n\x08licenses\x18\x01 \x03(\x0b2V.eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse.License\x1a\x9d\x01\n\x07License\x12H\n\nidentifier\x18\x01 \x01(\x0b24.eve.cosmetic.structure.paintwork.license.Identifier\x12H\n\nattributes\x18\x02 \x01(\x0b24.eve.cosmetic.structure.paintwork.license.AttributesBYZWgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/structure/paintwork/license/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_loyalty__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2.DESCRIPTOR,
 eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2.DESCRIPTOR,
 eve_dot_quasar_dot_admin_dot_admin__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__type__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_ISSUED = _descriptor.Descriptor(name='Issued', full_name='eve.cosmetic.structure.paintwork.license.api.Issued', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.structure', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='paintwork', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.paintwork', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='price', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.price', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure_type', full_name='eve.cosmetic.structure.paintwork.license.api.Issued.structure_type', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=470, serialized_end=843)
_RECEIPTISSUED = _descriptor.Descriptor(name='ReceiptIssued', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='activator', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.activator', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='issued', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.issued', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='duration', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.duration', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='price', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.price', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structures', full_name='eve.cosmetic.structure.paintwork.license.api.ReceiptIssued.structures', index=5, number=6, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=846, serialized_end=1145)
_REVOKED_CHARACTERACTION = _descriptor.Descriptor(name='CharacterAction', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.CharacterAction', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='deactivator', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.CharacterAction.deactivator', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2146, serialized_end=2211)
_REVOKED_ADMINACTION = _descriptor.Descriptor(name='AdminAction', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.AdminAction', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='context', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.AdminAction.context', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2213, serialized_end=2270)
_REVOKED_EXPIRED = _descriptor.Descriptor(name='Expired', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.Expired', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='timestamp', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.Expired.timestamp', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2272, serialized_end=2328)
_REVOKED_UPKEEPLOWPOWER = _descriptor.Descriptor(name='UpkeepLowPower', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.UpkeepLowPower', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2330, serialized_end=2346)
_REVOKED_UPKEEPABANDONED = _descriptor.Descriptor(name='UpkeepAbandoned', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.UpkeepAbandoned', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2348, serialized_end=2365)
_REVOKED_OWNERSHIPTRANSFERRED = _descriptor.Descriptor(name='OwnershipTransferred', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.OwnershipTransferred', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2367, serialized_end=2389)
_REVOKED_NEWERLICENSEISSUED = _descriptor.Descriptor(name='NewerLicenseIssued', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.NewerLicenseIssued', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2391, serialized_end=2411)
_REVOKED_STRUCTUREDESTROYED = _descriptor.Descriptor(name='StructureDestroyed', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.StructureDestroyed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2413, serialized_end=2433)
_REVOKED_STRUCTUREUNANCHORED = _descriptor.Descriptor(name='StructureUnanchored', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.StructureUnanchored', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2435, serialized_end=2456)
_REVOKED = _descriptor.Descriptor(name='Revoked', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='character_action', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.character_action', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='admin_action', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.admin_action', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='expired', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.expired', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='upkeep_low_power', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.upkeep_low_power', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='upkeep_abandoned', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.upkeep_abandoned', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='ownership_transferred', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.ownership_transferred', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='license_issued', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.license_issued', index=7, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='destroyed', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.destroyed', index=8, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unanchored', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.unanchored', index=9, number=10, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.structure', index=10, number=11, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_REVOKED_CHARACTERACTION,
 _REVOKED_ADMINACTION,
 _REVOKED_EXPIRED,
 _REVOKED_UPKEEPLOWPOWER,
 _REVOKED_UPKEEPABANDONED,
 _REVOKED_OWNERSHIPTRANSFERRED,
 _REVOKED_NEWERLICENSEISSUED,
 _REVOKED_STRUCTUREDESTROYED,
 _REVOKED_STRUCTUREUNANCHORED], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='reason', full_name='eve.cosmetic.structure.paintwork.license.api.Revoked.reason', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1148, serialized_end=2466)
_GETALLOWNEDBYCORPORATIONREQUEST = _descriptor.Descriptor(name='GetAllOwnedByCorporationRequest', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationRequest.corporation', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2468, serialized_end=2551)
_GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE = _descriptor.Descriptor(name='License', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse.License', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse.License.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse.License.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2697, serialized_end=2854)
_GETALLOWNEDBYCORPORATIONRESPONSE = _descriptor.Descriptor(name='GetAllOwnedByCorporationResponse', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='licenses', full_name='eve.cosmetic.structure.paintwork.license.api.GetAllOwnedByCorporationResponse.licenses', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2554, serialized_end=2854)
_ISSUED.fields_by_name['id'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2._IDENTIFIER
_ISSUED.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2._ATTRIBUTES
_ISSUED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_ISSUED.fields_by_name['paintwork'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_paintwork__pb2._SLOTCONFIGURATION
_ISSUED.fields_by_name['price'].message_type = eve_dot_corporation_dot_loyalty__pb2._POINTS
_ISSUED.fields_by_name['structure_type'].message_type = eve_dot_structure_dot_structure__type__pb2._IDENTIFIER
_RECEIPTISSUED.fields_by_name['activator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_RECEIPTISSUED.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_RECEIPTISSUED.fields_by_name['issued'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_RECEIPTISSUED.fields_by_name['duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_RECEIPTISSUED.fields_by_name['price'].message_type = eve_dot_corporation_dot_loyalty__pb2._POINTS
_RECEIPTISSUED.fields_by_name['structures'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_REVOKED_CHARACTERACTION.fields_by_name['deactivator'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REVOKED_CHARACTERACTION.containing_type = _REVOKED
_REVOKED_ADMINACTION.fields_by_name['context'].message_type = eve_dot_quasar_dot_admin_dot_admin__pb2._CONTEXT
_REVOKED_ADMINACTION.containing_type = _REVOKED
_REVOKED_EXPIRED.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_REVOKED_EXPIRED.containing_type = _REVOKED
_REVOKED_UPKEEPLOWPOWER.containing_type = _REVOKED
_REVOKED_UPKEEPABANDONED.containing_type = _REVOKED
_REVOKED_OWNERSHIPTRANSFERRED.containing_type = _REVOKED
_REVOKED_NEWERLICENSEISSUED.containing_type = _REVOKED
_REVOKED_STRUCTUREDESTROYED.containing_type = _REVOKED
_REVOKED_STRUCTUREUNANCHORED.containing_type = _REVOKED
_REVOKED.fields_by_name['license'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2._IDENTIFIER
_REVOKED.fields_by_name['character_action'].message_type = _REVOKED_CHARACTERACTION
_REVOKED.fields_by_name['admin_action'].message_type = _REVOKED_ADMINACTION
_REVOKED.fields_by_name['expired'].message_type = _REVOKED_EXPIRED
_REVOKED.fields_by_name['upkeep_low_power'].message_type = _REVOKED_UPKEEPLOWPOWER
_REVOKED.fields_by_name['upkeep_abandoned'].message_type = _REVOKED_UPKEEPABANDONED
_REVOKED.fields_by_name['ownership_transferred'].message_type = _REVOKED_OWNERSHIPTRANSFERRED
_REVOKED.fields_by_name['license_issued'].message_type = _REVOKED_NEWERLICENSEISSUED
_REVOKED.fields_by_name['destroyed'].message_type = _REVOKED_STRUCTUREDESTROYED
_REVOKED.fields_by_name['unanchored'].message_type = _REVOKED_STRUCTUREUNANCHORED
_REVOKED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['character_action'])
_REVOKED.fields_by_name['character_action'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['admin_action'])
_REVOKED.fields_by_name['admin_action'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['expired'])
_REVOKED.fields_by_name['expired'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['upkeep_low_power'])
_REVOKED.fields_by_name['upkeep_low_power'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['upkeep_abandoned'])
_REVOKED.fields_by_name['upkeep_abandoned'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['ownership_transferred'])
_REVOKED.fields_by_name['ownership_transferred'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['license_issued'])
_REVOKED.fields_by_name['license_issued'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['destroyed'])
_REVOKED.fields_by_name['destroyed'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_REVOKED.oneofs_by_name['reason'].fields.append(_REVOKED.fields_by_name['unanchored'])
_REVOKED.fields_by_name['unanchored'].containing_oneof = _REVOKED.oneofs_by_name['reason']
_GETALLOWNEDBYCORPORATIONREQUEST.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE.fields_by_name['identifier'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2._IDENTIFIER
_GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_structure_dot_paintwork_dot_license_dot_license__pb2._ATTRIBUTES
_GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE.containing_type = _GETALLOWNEDBYCORPORATIONRESPONSE
_GETALLOWNEDBYCORPORATIONRESPONSE.fields_by_name['licenses'].message_type = _GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE
DESCRIPTOR.message_types_by_name['Issued'] = _ISSUED
DESCRIPTOR.message_types_by_name['ReceiptIssued'] = _RECEIPTISSUED
DESCRIPTOR.message_types_by_name['Revoked'] = _REVOKED
DESCRIPTOR.message_types_by_name['GetAllOwnedByCorporationRequest'] = _GETALLOWNEDBYCORPORATIONREQUEST
DESCRIPTOR.message_types_by_name['GetAllOwnedByCorporationResponse'] = _GETALLOWNEDBYCORPORATIONRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Issued = _reflection.GeneratedProtocolMessageType('Issued', (_message.Message,), {'DESCRIPTOR': _ISSUED,
 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'})
_sym_db.RegisterMessage(Issued)
ReceiptIssued = _reflection.GeneratedProtocolMessageType('ReceiptIssued', (_message.Message,), {'DESCRIPTOR': _RECEIPTISSUED,
 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'})
_sym_db.RegisterMessage(ReceiptIssued)
Revoked = _reflection.GeneratedProtocolMessageType('Revoked', (_message.Message,), {'CharacterAction': _reflection.GeneratedProtocolMessageType('CharacterAction', (_message.Message,), {'DESCRIPTOR': _REVOKED_CHARACTERACTION,
                     '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'AdminAction': _reflection.GeneratedProtocolMessageType('AdminAction', (_message.Message,), {'DESCRIPTOR': _REVOKED_ADMINACTION,
                 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'Expired': _reflection.GeneratedProtocolMessageType('Expired', (_message.Message,), {'DESCRIPTOR': _REVOKED_EXPIRED,
             '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'UpkeepLowPower': _reflection.GeneratedProtocolMessageType('UpkeepLowPower', (_message.Message,), {'DESCRIPTOR': _REVOKED_UPKEEPLOWPOWER,
                    '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'UpkeepAbandoned': _reflection.GeneratedProtocolMessageType('UpkeepAbandoned', (_message.Message,), {'DESCRIPTOR': _REVOKED_UPKEEPABANDONED,
                     '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'OwnershipTransferred': _reflection.GeneratedProtocolMessageType('OwnershipTransferred', (_message.Message,), {'DESCRIPTOR': _REVOKED_OWNERSHIPTRANSFERRED,
                          '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'NewerLicenseIssued': _reflection.GeneratedProtocolMessageType('NewerLicenseIssued', (_message.Message,), {'DESCRIPTOR': _REVOKED_NEWERLICENSEISSUED,
                        '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'StructureDestroyed': _reflection.GeneratedProtocolMessageType('StructureDestroyed', (_message.Message,), {'DESCRIPTOR': _REVOKED_STRUCTUREDESTROYED,
                        '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'StructureUnanchored': _reflection.GeneratedProtocolMessageType('StructureUnanchored', (_message.Message,), {'DESCRIPTOR': _REVOKED_STRUCTUREUNANCHORED,
                         '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'DESCRIPTOR': _REVOKED,
 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'})
_sym_db.RegisterMessage(Revoked)
_sym_db.RegisterMessage(Revoked.CharacterAction)
_sym_db.RegisterMessage(Revoked.AdminAction)
_sym_db.RegisterMessage(Revoked.Expired)
_sym_db.RegisterMessage(Revoked.UpkeepLowPower)
_sym_db.RegisterMessage(Revoked.UpkeepAbandoned)
_sym_db.RegisterMessage(Revoked.OwnershipTransferred)
_sym_db.RegisterMessage(Revoked.NewerLicenseIssued)
_sym_db.RegisterMessage(Revoked.StructureDestroyed)
_sym_db.RegisterMessage(Revoked.StructureUnanchored)
GetAllOwnedByCorporationRequest = _reflection.GeneratedProtocolMessageType('GetAllOwnedByCorporationRequest', (_message.Message,), {'DESCRIPTOR': _GETALLOWNEDBYCORPORATIONREQUEST,
 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'})
_sym_db.RegisterMessage(GetAllOwnedByCorporationRequest)
GetAllOwnedByCorporationResponse = _reflection.GeneratedProtocolMessageType('GetAllOwnedByCorporationResponse', (_message.Message,), {'License': _reflection.GeneratedProtocolMessageType('License', (_message.Message,), {'DESCRIPTOR': _GETALLOWNEDBYCORPORATIONRESPONSE_LICENSE,
             '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'}),
 'DESCRIPTOR': _GETALLOWNEDBYCORPORATIONRESPONSE,
 '__module__': 'eve.cosmetic.structure.paintwork.license.api.api_pb2'})
_sym_db.RegisterMessage(GetAllOwnedByCorporationResponse)
_sym_db.RegisterMessage(GetAllOwnedByCorporationResponse.License)
DESCRIPTOR._options = None
_ISSUED.fields_by_name['structure']._options = None
_RECEIPTISSUED._options = None
