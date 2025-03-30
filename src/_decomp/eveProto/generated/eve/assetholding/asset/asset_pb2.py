#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\assetholding\asset\asset_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.accounting import entrytype_pb2 as eve_dot_accounting_dot_entrytype__pb2
from eveProto.generated.eve.accounting import transaction_pb2 as eve_dot_accounting_dot_transaction__pb2
from eveProto.generated.eve.assetholding.cosmetic.ship.skin.license import license_pb2 as eve_dot_assetholding_dot_cosmetic_dot_ship_dot_skin_dot_license_dot_license__pb2
from eveProto.generated.eve.assetholding.inventory.itemstack import itemstack_pb2 as eve_dot_assetholding_dot_inventory_dot_itemstack_dot_itemstack__pb2
from eveProto.generated.eve.assetholding.inventory.itemtype import itemtype_pb2 as eve_dot_assetholding_dot_inventory_dot_itemtype_dot_itemtype__pb2
from eveProto.generated.eve.assetholding.isk import isk_pb2 as eve_dot_assetholding_dot_isk_dot_isk__pb2
from eveProto.generated.eve.assetholding.loyaltypoints import loyaltypoints_pb2 as eve_dot_assetholding_dot_loyaltypoints_dot_loyaltypoints__pb2
from eveProto.generated.eve.assetholding.plex import plex_pb2 as eve_dot_assetholding_dot_plex_dot_plex__pb2
from eveProto.generated.eve.assetholding.skillpoints import skillpoints_pb2 as eve_dot_assetholding_dot_skillpoints_dot_skillpoints__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.loyaltypoints import loyaltypoints_pb2 as eve_dot_loyaltypoints_dot_loyaltypoints__pb2
from eveProto.generated.eve.skill.points import transaction_pb2 as eve_dot_skill_dot_points_dot_transaction__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/assetholding/asset/asset.proto', package='eve.assetholding.asset', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/asset', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/assetholding/asset/asset.proto\x12\x16eve.assetholding.asset\x1a\x1eeve/accounting/entrytype.proto\x1a eve/accounting/transaction.proto\x1a9eve/assetholding/cosmetic/ship/skin/license/license.proto\x1a4eve/assetholding/inventory/itemstack/itemstack.proto\x1a2eve/assetholding/inventory/itemtype/itemtype.proto\x1a\x1eeve/assetholding/isk/isk.proto\x1a2eve/assetholding/loyaltypoints/loyaltypoints.proto\x1a eve/assetholding/plex/plex.proto\x1a.eve/assetholding/skillpoints/skillpoints.proto\x1a\x1deve/character/character.proto\x1a!eve/corporation/corporation.proto\x1a\x11eve/isk/isk.proto\x1a%eve/loyaltypoints/loyaltypoints.proto\x1a"eve/skill/points/transaction.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\x1a\n\nIdentifier\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c"\xb7\x02\n\nAttributes\x12\x15\n\rinternal_name\x18\x01 \x01(\t\x12\x1c\n\x14internal_description\x18\x02 \x01(\t\x126\n\nbenefactor\x18\x03 \x01(\x0b2".eve.assetholding.asset.Benefactor\x12*\n\x04unit\x18\x04 \x01(\x0b2\x1c.eve.assetholding.asset.Unit\x122\n\x08capacity\x18\x05 \x01(\x0b2 .eve.assetholding.asset.Capacity\x122\n\x0crelease_time\x18\x06 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12\x19\n\x0fno_auto_release\x18\x07 \x01(\x08H\x00B\r\n\x0bautorelease"\x90\x01\n\nBenefactor\x12.\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00\x12\x11\n\x07spawned\x18\x03 \x01(\x08H\x00B\x0b\n\tdepositor"\\\n\x08Capacity\x120\n\x06finite\x18\x01 \x01(\x0b2\x1e.eve.assetholding.asset.FiniteH\x00\x12\x12\n\x08infinite\x18\x02 \x01(\x08H\x00B\n\n\x08capacity"-\n\x06Finite\x12\x10\n\x08original\x18\x01 \x01(\x04\x12\x11\n\tremaining\x18\x02 \x01(\x04"\xdd\x05\n\x04Unit\x12>\n\x03isk\x18\x01 \x01(\x0b2+.eve.assetholding.asset.InterStellarKreditsB\x02\x18\x01H\x00\x12C\n\x0eloyalty_points\x18\x02 \x01(\x0b2%.eve.assetholding.asset.LoyaltyPointsB\x02\x18\x01H\x00\x12?\n\x0cskill_points\x18\x03 \x01(\x0b2#.eve.assetholding.asset.SkillPointsB\x02\x18\x01H\x00\x12\x1c\n\x0enew_definition\x18\x0b \x01(\x08B\x02\x18\x01H\x00\x12.\n\x08unit_isk\x18\x04 \x01(\x0b2\x1a.eve.assetholding.isk.UnitH\x01\x12C\n\x13unit_loyalty_points\x18\x05 \x01(\x0b2$.eve.assetholding.loyaltypoints.UnitH\x01\x12?\n\x11unit_skill_points\x18\x06 \x01(\x0b2".eve.assetholding.skillpoints.UnitH\x01\x120\n\tunit_plex\x18\x07 \x01(\x0b2\x1b.eve.assetholding.plex.UnitH\x01\x12J\n\x14unit_inventory_stack\x18\x08 \x01(\x0b2*.eve.assetholding.inventory.itemstack.UnitH\x01\x12L\n\x17unit_inventory_itemtype\x18\t \x01(\x0b2).eve.assetholding.inventory.itemtype.UnitH\x01\x12S\n\x16unit_ship_skin_license\x18\n \x01(\x0b21.eve.assetholding.cosmetic.ship.skin.license.UnitH\x01B\x0c\n\ndeprecatedB\x0c\n\ndefinition"\x9f\x02\n\x13InterStellarKredits\x12!\n\x06amount\x18\x01 \x01(\x0b2\x11.eve.isk.Currency\x12 \n\x16entry_type_unspecified\x18\x02 \x01(\x08H\x00\x12:\n\nentry_type\x18\x03 \x01(\x0b2$.eve.accounting.entrytype.IdentifierH\x00\x12@\n\treference\x18\x04 \x01(\x0b2-.eve.accounting.transaction.ExternalReference\x12-\n\x08rewarder\x18\x05 \x01(\x0b2\x1b.eve.corporation.Identifier:\x02\x18\x01B\x12\n\x10transaction_type"~\n\rLoyaltyPoints\x12+\n\x06amount\x18\x01 \x01(\x0b2\x1b.eve.loyaltypoints.Currency\x12<\n\x10transaction_type\x18\x02 \x01(\x0e2".eve.loyaltypoints.TransactionType:\x02\x18\x01"^\n\x0bSkillPoints\x12\x0e\n\x06amount\x18\x01 \x01(\r\x12;\n\x10transaction_type\x18\x02 \x01(\x0e2!.eve.skill.points.TransactionType:\x02\x18\x01BCZAgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/assetb\x06proto3', dependencies=[eve_dot_accounting_dot_entrytype__pb2.DESCRIPTOR,
 eve_dot_accounting_dot_transaction__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_cosmetic_dot_ship_dot_skin_dot_license_dot_license__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_inventory_dot_itemstack_dot_itemstack__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_inventory_dot_itemtype_dot_itemtype__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_loyaltypoints_dot_loyaltypoints__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_plex_dot_plex__pb2.DESCRIPTOR,
 eve_dot_assetholding_dot_skillpoints_dot_skillpoints__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_isk_dot_isk__pb2.DESCRIPTOR,
 eve_dot_loyaltypoints_dot_loyaltypoints__pb2.DESCRIPTOR,
 eve_dot_skill_dot_points_dot_transaction__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.assetholding.asset.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='uuid', full_name='eve.assetholding.asset.Identifier.uuid', index=0, number=1, type=12, cpp_type=9, label=1, has_default_value=False, default_value='', message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=652, serialized_end=678)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.assetholding.asset.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='internal_name', full_name='eve.assetholding.asset.Attributes.internal_name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='internal_description', full_name='eve.assetholding.asset.Attributes.internal_description', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='benefactor', full_name='eve.assetholding.asset.Attributes.benefactor', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit', full_name='eve.assetholding.asset.Attributes.unit', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='capacity', full_name='eve.assetholding.asset.Attributes.capacity', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='release_time', full_name='eve.assetholding.asset.Attributes.release_time', index=5, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_auto_release', full_name='eve.assetholding.asset.Attributes.no_auto_release', index=6, number=7, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='autorelease', full_name='eve.assetholding.asset.Attributes.autorelease', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=681, serialized_end=992)
_BENEFACTOR = _descriptor.Descriptor(name='Benefactor', full_name='eve.assetholding.asset.Benefactor', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.assetholding.asset.Benefactor.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.assetholding.asset.Benefactor.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='spawned', full_name='eve.assetholding.asset.Benefactor.spawned', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='depositor', full_name='eve.assetholding.asset.Benefactor.depositor', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=995, serialized_end=1139)
_CAPACITY = _descriptor.Descriptor(name='Capacity', full_name='eve.assetholding.asset.Capacity', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='finite', full_name='eve.assetholding.asset.Capacity.finite', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='infinite', full_name='eve.assetholding.asset.Capacity.infinite', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='capacity', full_name='eve.assetholding.asset.Capacity.capacity', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1141, serialized_end=1233)
_FINITE = _descriptor.Descriptor(name='Finite', full_name='eve.assetholding.asset.Finite', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='original', full_name='eve.assetholding.asset.Finite.original', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='remaining', full_name='eve.assetholding.asset.Finite.remaining', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1235, serialized_end=1280)
_UNIT = _descriptor.Descriptor(name='Unit', full_name='eve.assetholding.asset.Unit', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='isk', full_name='eve.assetholding.asset.Unit.isk', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='loyalty_points', full_name='eve.assetholding.asset.Unit.loyalty_points', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='skill_points', full_name='eve.assetholding.asset.Unit.skill_points', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='new_definition', full_name='eve.assetholding.asset.Unit.new_definition', index=3, number=11, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_isk', full_name='eve.assetholding.asset.Unit.unit_isk', index=4, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_loyalty_points', full_name='eve.assetholding.asset.Unit.unit_loyalty_points', index=5, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_skill_points', full_name='eve.assetholding.asset.Unit.unit_skill_points', index=6, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_plex', full_name='eve.assetholding.asset.Unit.unit_plex', index=7, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_inventory_stack', full_name='eve.assetholding.asset.Unit.unit_inventory_stack', index=8, number=8, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_inventory_itemtype', full_name='eve.assetholding.asset.Unit.unit_inventory_itemtype', index=9, number=9, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='unit_ship_skin_license', full_name='eve.assetholding.asset.Unit.unit_ship_skin_license', index=10, number=10, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='deprecated', full_name='eve.assetholding.asset.Unit.deprecated', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='definition', full_name='eve.assetholding.asset.Unit.definition', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1283, serialized_end=2016)
_INTERSTELLARKREDITS = _descriptor.Descriptor(name='InterStellarKredits', full_name='eve.assetholding.asset.InterStellarKredits', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.assetholding.asset.InterStellarKredits.amount', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='entry_type_unspecified', full_name='eve.assetholding.asset.InterStellarKredits.entry_type_unspecified', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='entry_type', full_name='eve.assetholding.asset.InterStellarKredits.entry_type', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='reference', full_name='eve.assetholding.asset.InterStellarKredits.reference', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='rewarder', full_name='eve.assetholding.asset.InterStellarKredits.rewarder', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='transaction_type', full_name='eve.assetholding.asset.InterStellarKredits.transaction_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=2019, serialized_end=2306)
_LOYALTYPOINTS = _descriptor.Descriptor(name='LoyaltyPoints', full_name='eve.assetholding.asset.LoyaltyPoints', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.assetholding.asset.LoyaltyPoints.amount', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='transaction_type', full_name='eve.assetholding.asset.LoyaltyPoints.transaction_type', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2308, serialized_end=2434)
_SKILLPOINTS = _descriptor.Descriptor(name='SkillPoints', full_name='eve.assetholding.asset.SkillPoints', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='amount', full_name='eve.assetholding.asset.SkillPoints.amount', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='transaction_type', full_name='eve.assetholding.asset.SkillPoints.transaction_type', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=2436, serialized_end=2530)
_ATTRIBUTES.fields_by_name['benefactor'].message_type = _BENEFACTOR
_ATTRIBUTES.fields_by_name['unit'].message_type = _UNIT
_ATTRIBUTES.fields_by_name['capacity'].message_type = _CAPACITY
_ATTRIBUTES.fields_by_name['release_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.oneofs_by_name['autorelease'].fields.append(_ATTRIBUTES.fields_by_name['release_time'])
_ATTRIBUTES.fields_by_name['release_time'].containing_oneof = _ATTRIBUTES.oneofs_by_name['autorelease']
_ATTRIBUTES.oneofs_by_name['autorelease'].fields.append(_ATTRIBUTES.fields_by_name['no_auto_release'])
_ATTRIBUTES.fields_by_name['no_auto_release'].containing_oneof = _ATTRIBUTES.oneofs_by_name['autorelease']
_BENEFACTOR.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_BENEFACTOR.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_BENEFACTOR.oneofs_by_name['depositor'].fields.append(_BENEFACTOR.fields_by_name['character'])
_BENEFACTOR.fields_by_name['character'].containing_oneof = _BENEFACTOR.oneofs_by_name['depositor']
_BENEFACTOR.oneofs_by_name['depositor'].fields.append(_BENEFACTOR.fields_by_name['corporation'])
_BENEFACTOR.fields_by_name['corporation'].containing_oneof = _BENEFACTOR.oneofs_by_name['depositor']
_BENEFACTOR.oneofs_by_name['depositor'].fields.append(_BENEFACTOR.fields_by_name['spawned'])
_BENEFACTOR.fields_by_name['spawned'].containing_oneof = _BENEFACTOR.oneofs_by_name['depositor']
_CAPACITY.fields_by_name['finite'].message_type = _FINITE
_CAPACITY.oneofs_by_name['capacity'].fields.append(_CAPACITY.fields_by_name['finite'])
_CAPACITY.fields_by_name['finite'].containing_oneof = _CAPACITY.oneofs_by_name['capacity']
_CAPACITY.oneofs_by_name['capacity'].fields.append(_CAPACITY.fields_by_name['infinite'])
_CAPACITY.fields_by_name['infinite'].containing_oneof = _CAPACITY.oneofs_by_name['capacity']
_UNIT.fields_by_name['isk'].message_type = _INTERSTELLARKREDITS
_UNIT.fields_by_name['loyalty_points'].message_type = _LOYALTYPOINTS
_UNIT.fields_by_name['skill_points'].message_type = _SKILLPOINTS
_UNIT.fields_by_name['unit_isk'].message_type = eve_dot_assetholding_dot_isk_dot_isk__pb2._UNIT
_UNIT.fields_by_name['unit_loyalty_points'].message_type = eve_dot_assetholding_dot_loyaltypoints_dot_loyaltypoints__pb2._UNIT
_UNIT.fields_by_name['unit_skill_points'].message_type = eve_dot_assetholding_dot_skillpoints_dot_skillpoints__pb2._UNIT
_UNIT.fields_by_name['unit_plex'].message_type = eve_dot_assetholding_dot_plex_dot_plex__pb2._UNIT
_UNIT.fields_by_name['unit_inventory_stack'].message_type = eve_dot_assetholding_dot_inventory_dot_itemstack_dot_itemstack__pb2._UNIT
_UNIT.fields_by_name['unit_inventory_itemtype'].message_type = eve_dot_assetholding_dot_inventory_dot_itemtype_dot_itemtype__pb2._UNIT
_UNIT.fields_by_name['unit_ship_skin_license'].message_type = eve_dot_assetholding_dot_cosmetic_dot_ship_dot_skin_dot_license_dot_license__pb2._UNIT
_UNIT.oneofs_by_name['deprecated'].fields.append(_UNIT.fields_by_name['isk'])
_UNIT.fields_by_name['isk'].containing_oneof = _UNIT.oneofs_by_name['deprecated']
_UNIT.oneofs_by_name['deprecated'].fields.append(_UNIT.fields_by_name['loyalty_points'])
_UNIT.fields_by_name['loyalty_points'].containing_oneof = _UNIT.oneofs_by_name['deprecated']
_UNIT.oneofs_by_name['deprecated'].fields.append(_UNIT.fields_by_name['skill_points'])
_UNIT.fields_by_name['skill_points'].containing_oneof = _UNIT.oneofs_by_name['deprecated']
_UNIT.oneofs_by_name['deprecated'].fields.append(_UNIT.fields_by_name['new_definition'])
_UNIT.fields_by_name['new_definition'].containing_oneof = _UNIT.oneofs_by_name['deprecated']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_isk'])
_UNIT.fields_by_name['unit_isk'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_loyalty_points'])
_UNIT.fields_by_name['unit_loyalty_points'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_skill_points'])
_UNIT.fields_by_name['unit_skill_points'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_plex'])
_UNIT.fields_by_name['unit_plex'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_inventory_stack'])
_UNIT.fields_by_name['unit_inventory_stack'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_inventory_itemtype'])
_UNIT.fields_by_name['unit_inventory_itemtype'].containing_oneof = _UNIT.oneofs_by_name['definition']
_UNIT.oneofs_by_name['definition'].fields.append(_UNIT.fields_by_name['unit_ship_skin_license'])
_UNIT.fields_by_name['unit_ship_skin_license'].containing_oneof = _UNIT.oneofs_by_name['definition']
_INTERSTELLARKREDITS.fields_by_name['amount'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_INTERSTELLARKREDITS.fields_by_name['entry_type'].message_type = eve_dot_accounting_dot_entrytype__pb2._IDENTIFIER
_INTERSTELLARKREDITS.fields_by_name['reference'].message_type = eve_dot_accounting_dot_transaction__pb2._EXTERNALREFERENCE
_INTERSTELLARKREDITS.fields_by_name['rewarder'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_INTERSTELLARKREDITS.oneofs_by_name['transaction_type'].fields.append(_INTERSTELLARKREDITS.fields_by_name['entry_type_unspecified'])
_INTERSTELLARKREDITS.fields_by_name['entry_type_unspecified'].containing_oneof = _INTERSTELLARKREDITS.oneofs_by_name['transaction_type']
_INTERSTELLARKREDITS.oneofs_by_name['transaction_type'].fields.append(_INTERSTELLARKREDITS.fields_by_name['entry_type'])
_INTERSTELLARKREDITS.fields_by_name['entry_type'].containing_oneof = _INTERSTELLARKREDITS.oneofs_by_name['transaction_type']
_LOYALTYPOINTS.fields_by_name['amount'].message_type = eve_dot_loyaltypoints_dot_loyaltypoints__pb2._CURRENCY
_LOYALTYPOINTS.fields_by_name['transaction_type'].enum_type = eve_dot_loyaltypoints_dot_loyaltypoints__pb2._TRANSACTIONTYPE
_SKILLPOINTS.fields_by_name['transaction_type'].enum_type = eve_dot_skill_dot_points_dot_transaction__pb2._TRANSACTIONTYPE
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Benefactor'] = _BENEFACTOR
DESCRIPTOR.message_types_by_name['Capacity'] = _CAPACITY
DESCRIPTOR.message_types_by_name['Finite'] = _FINITE
DESCRIPTOR.message_types_by_name['Unit'] = _UNIT
DESCRIPTOR.message_types_by_name['InterStellarKredits'] = _INTERSTELLARKREDITS
DESCRIPTOR.message_types_by_name['LoyaltyPoints'] = _LOYALTYPOINTS
DESCRIPTOR.message_types_by_name['SkillPoints'] = _SKILLPOINTS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Attributes)
Benefactor = _reflection.GeneratedProtocolMessageType('Benefactor', (_message.Message,), {'DESCRIPTOR': _BENEFACTOR,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Benefactor)
Capacity = _reflection.GeneratedProtocolMessageType('Capacity', (_message.Message,), {'DESCRIPTOR': _CAPACITY,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Capacity)
Finite = _reflection.GeneratedProtocolMessageType('Finite', (_message.Message,), {'DESCRIPTOR': _FINITE,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Finite)
Unit = _reflection.GeneratedProtocolMessageType('Unit', (_message.Message,), {'DESCRIPTOR': _UNIT,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(Unit)
InterStellarKredits = _reflection.GeneratedProtocolMessageType('InterStellarKredits', (_message.Message,), {'DESCRIPTOR': _INTERSTELLARKREDITS,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(InterStellarKredits)
LoyaltyPoints = _reflection.GeneratedProtocolMessageType('LoyaltyPoints', (_message.Message,), {'DESCRIPTOR': _LOYALTYPOINTS,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(LoyaltyPoints)
SkillPoints = _reflection.GeneratedProtocolMessageType('SkillPoints', (_message.Message,), {'DESCRIPTOR': _SKILLPOINTS,
 '__module__': 'eve.assetholding.asset.asset_pb2'})
_sym_db.RegisterMessage(SkillPoints)
DESCRIPTOR._options = None
_UNIT.fields_by_name['isk']._options = None
_UNIT.fields_by_name['loyalty_points']._options = None
_UNIT.fields_by_name['skill_points']._options = None
_UNIT.fields_by_name['new_definition']._options = None
_INTERSTELLARKREDITS._options = None
_LOYALTYPOINTS._options = None
_SKILLPOINTS._options = None
