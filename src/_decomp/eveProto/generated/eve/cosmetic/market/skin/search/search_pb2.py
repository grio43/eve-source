#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\market\skin\search\search_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/market/skin/search/search.proto', package='eve.cosmetic.market.skin.search', syntax='proto3', serialized_options='ZJgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/skin/search', create_key=_descriptor._internal_create_key, serialized_pb='\n,eve/cosmetic/market/skin/search/search.proto\x12\x1feve.cosmetic.market.skin.search\x1a\x18eve/ship/ship_type.proto">\n\x0eShipTypeFilter\x12,\n\nship_types\x18\x01 \x03(\x0b2\x18.eve.shiptype.Identifier"_\n\x06Filter\x12K\n\x10ship_type_filter\x18\x01 \x01(\x0b2/.eve.cosmetic.market.skin.search.ShipTypeFilterH\x00B\x08\n\x06filter"\x97\x01\n\x05Order\x12@\n\x05field\x18\x01 \x01(\x0e21.eve.cosmetic.market.skin.search.Order.OrderField\x12\x11\n\tascending\x18\x02 \x01(\x08"9\n\nOrderField\x12\x1b\n\x17ORDER_FIELD_UNSPECIFIED\x10\x00\x12\x0e\n\nEXPIRES_AT\x10\x01"\x0e\n\x0cTargetPublic"\x9c\x02\n\x13TargetMyCorporation\x12b\n\x13required_membership\x18\x01 \x01(\x0e2E.eve.cosmetic.market.skin.search.TargetMyCorporation.SellerMembership"\xa0\x01\n\x10SellerMembership\x12!\n\x1dSELLER_MEMBERSHIP_UNSPECIFIED\x10\x00\x12#\n\x1fSELLER_MEMBERSHIP_BRAND_MANAGER\x10\x01\x12(\n$SELLER_MEMBERSHIP_CORPORATION_MEMBER\x10\x02\x12\x1a\n\x16SELLER_MEMBERSHIP_NONE\x10\x03"\x93\x02\n\x10TargetMyAlliance\x12_\n\x13required_membership\x18\x01 \x01(\x0e2B.eve.cosmetic.market.skin.search.TargetMyAlliance.SellerMembership"\x9d\x01\n\x10SellerMembership\x12!\n\x1dSELLER_MEMBERSHIP_UNSPECIFIED\x10\x00\x12#\n\x1fSELLER_MEMBERSHIP_BRAND_MANAGER\x10\x01\x12%\n!SELLER_MEMBERSHIP_ALLIANCE_MEMBER\x10\x02\x12\x1a\n\x16SELLER_MEMBERSHIP_NONE\x10\x03"\x13\n\x11TargetMyCharacter"\x0b\n\tTargetAll"\xfb\x02\n\rListingTarget\x12?\n\x06public\x18\x01 \x01(\x0b2-.eve.cosmetic.market.skin.search.TargetPublicH\x00\x12N\n\x0emy_corporation\x18\x02 \x01(\x0b24.eve.cosmetic.market.skin.search.TargetMyCorporationH\x00\x12H\n\x0bmy_alliance\x18\x03 \x01(\x0b21.eve.cosmetic.market.skin.search.TargetMyAllianceH\x00\x12J\n\x0cmy_character\x18\x04 \x01(\x0b22.eve.cosmetic.market.skin.search.TargetMyCharacterH\x00\x129\n\x03all\x18\x05 \x01(\x0b2*.eve.cosmetic.market.skin.search.TargetAllH\x00B\x08\n\x06targetBLZJgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/market/skin/searchb\x06proto3', dependencies=[eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_ORDER_ORDERFIELD = _descriptor.EnumDescriptor(name='OrderField', full_name='eve.cosmetic.market.skin.search.Order.OrderField', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='ORDER_FIELD_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='EXPIRES_AT', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=363, serialized_end=420)
_sym_db.RegisterEnumDescriptor(_ORDER_ORDERFIELD)
_TARGETMYCORPORATION_SELLERMEMBERSHIP = _descriptor.EnumDescriptor(name='SellerMembership', full_name='eve.cosmetic.market.skin.search.TargetMyCorporation.SellerMembership', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_BRAND_MANAGER', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_CORPORATION_MEMBER', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_NONE', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=563, serialized_end=723)
_sym_db.RegisterEnumDescriptor(_TARGETMYCORPORATION_SELLERMEMBERSHIP)
_TARGETMYALLIANCE_SELLERMEMBERSHIP = _descriptor.EnumDescriptor(name='SellerMembership', full_name='eve.cosmetic.market.skin.search.TargetMyAlliance.SellerMembership', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_BRAND_MANAGER', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_ALLIANCE_MEMBER', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='SELLER_MEMBERSHIP_NONE', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=844, serialized_end=1001)
_sym_db.RegisterEnumDescriptor(_TARGETMYALLIANCE_SELLERMEMBERSHIP)
_SHIPTYPEFILTER = _descriptor.Descriptor(name='ShipTypeFilter', full_name='eve.cosmetic.market.skin.search.ShipTypeFilter', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship_types', full_name='eve.cosmetic.market.skin.search.ShipTypeFilter.ship_types', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=107, serialized_end=169)
_FILTER = _descriptor.Descriptor(name='Filter', full_name='eve.cosmetic.market.skin.search.Filter', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship_type_filter', full_name='eve.cosmetic.market.skin.search.Filter.ship_type_filter', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='filter', full_name='eve.cosmetic.market.skin.search.Filter.filter', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=171, serialized_end=266)
_ORDER = _descriptor.Descriptor(name='Order', full_name='eve.cosmetic.market.skin.search.Order', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='field', full_name='eve.cosmetic.market.skin.search.Order.field', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ascending', full_name='eve.cosmetic.market.skin.search.Order.ascending', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_ORDER_ORDERFIELD], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=269, serialized_end=420)
_TARGETPUBLIC = _descriptor.Descriptor(name='TargetPublic', full_name='eve.cosmetic.market.skin.search.TargetPublic', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=422, serialized_end=436)
_TARGETMYCORPORATION = _descriptor.Descriptor(name='TargetMyCorporation', full_name='eve.cosmetic.market.skin.search.TargetMyCorporation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='required_membership', full_name='eve.cosmetic.market.skin.search.TargetMyCorporation.required_membership', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_TARGETMYCORPORATION_SELLERMEMBERSHIP], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=439, serialized_end=723)
_TARGETMYALLIANCE = _descriptor.Descriptor(name='TargetMyAlliance', full_name='eve.cosmetic.market.skin.search.TargetMyAlliance', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='required_membership', full_name='eve.cosmetic.market.skin.search.TargetMyAlliance.required_membership', index=0, number=1, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_TARGETMYALLIANCE_SELLERMEMBERSHIP], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=726, serialized_end=1001)
_TARGETMYCHARACTER = _descriptor.Descriptor(name='TargetMyCharacter', full_name='eve.cosmetic.market.skin.search.TargetMyCharacter', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1003, serialized_end=1022)
_TARGETALL = _descriptor.Descriptor(name='TargetAll', full_name='eve.cosmetic.market.skin.search.TargetAll', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1024, serialized_end=1035)
_LISTINGTARGET = _descriptor.Descriptor(name='ListingTarget', full_name='eve.cosmetic.market.skin.search.ListingTarget', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='public', full_name='eve.cosmetic.market.skin.search.ListingTarget.public', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='my_corporation', full_name='eve.cosmetic.market.skin.search.ListingTarget.my_corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='my_alliance', full_name='eve.cosmetic.market.skin.search.ListingTarget.my_alliance', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='my_character', full_name='eve.cosmetic.market.skin.search.ListingTarget.my_character', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='all', full_name='eve.cosmetic.market.skin.search.ListingTarget.all', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='target', full_name='eve.cosmetic.market.skin.search.ListingTarget.target', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=1038, serialized_end=1417)
_SHIPTYPEFILTER.fields_by_name['ship_types'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
_FILTER.fields_by_name['ship_type_filter'].message_type = _SHIPTYPEFILTER
_FILTER.oneofs_by_name['filter'].fields.append(_FILTER.fields_by_name['ship_type_filter'])
_FILTER.fields_by_name['ship_type_filter'].containing_oneof = _FILTER.oneofs_by_name['filter']
_ORDER.fields_by_name['field'].enum_type = _ORDER_ORDERFIELD
_ORDER_ORDERFIELD.containing_type = _ORDER
_TARGETMYCORPORATION.fields_by_name['required_membership'].enum_type = _TARGETMYCORPORATION_SELLERMEMBERSHIP
_TARGETMYCORPORATION_SELLERMEMBERSHIP.containing_type = _TARGETMYCORPORATION
_TARGETMYALLIANCE.fields_by_name['required_membership'].enum_type = _TARGETMYALLIANCE_SELLERMEMBERSHIP
_TARGETMYALLIANCE_SELLERMEMBERSHIP.containing_type = _TARGETMYALLIANCE
_LISTINGTARGET.fields_by_name['public'].message_type = _TARGETPUBLIC
_LISTINGTARGET.fields_by_name['my_corporation'].message_type = _TARGETMYCORPORATION
_LISTINGTARGET.fields_by_name['my_alliance'].message_type = _TARGETMYALLIANCE
_LISTINGTARGET.fields_by_name['my_character'].message_type = _TARGETMYCHARACTER
_LISTINGTARGET.fields_by_name['all'].message_type = _TARGETALL
_LISTINGTARGET.oneofs_by_name['target'].fields.append(_LISTINGTARGET.fields_by_name['public'])
_LISTINGTARGET.fields_by_name['public'].containing_oneof = _LISTINGTARGET.oneofs_by_name['target']
_LISTINGTARGET.oneofs_by_name['target'].fields.append(_LISTINGTARGET.fields_by_name['my_corporation'])
_LISTINGTARGET.fields_by_name['my_corporation'].containing_oneof = _LISTINGTARGET.oneofs_by_name['target']
_LISTINGTARGET.oneofs_by_name['target'].fields.append(_LISTINGTARGET.fields_by_name['my_alliance'])
_LISTINGTARGET.fields_by_name['my_alliance'].containing_oneof = _LISTINGTARGET.oneofs_by_name['target']
_LISTINGTARGET.oneofs_by_name['target'].fields.append(_LISTINGTARGET.fields_by_name['my_character'])
_LISTINGTARGET.fields_by_name['my_character'].containing_oneof = _LISTINGTARGET.oneofs_by_name['target']
_LISTINGTARGET.oneofs_by_name['target'].fields.append(_LISTINGTARGET.fields_by_name['all'])
_LISTINGTARGET.fields_by_name['all'].containing_oneof = _LISTINGTARGET.oneofs_by_name['target']
DESCRIPTOR.message_types_by_name['ShipTypeFilter'] = _SHIPTYPEFILTER
DESCRIPTOR.message_types_by_name['Filter'] = _FILTER
DESCRIPTOR.message_types_by_name['Order'] = _ORDER
DESCRIPTOR.message_types_by_name['TargetPublic'] = _TARGETPUBLIC
DESCRIPTOR.message_types_by_name['TargetMyCorporation'] = _TARGETMYCORPORATION
DESCRIPTOR.message_types_by_name['TargetMyAlliance'] = _TARGETMYALLIANCE
DESCRIPTOR.message_types_by_name['TargetMyCharacter'] = _TARGETMYCHARACTER
DESCRIPTOR.message_types_by_name['TargetAll'] = _TARGETALL
DESCRIPTOR.message_types_by_name['ListingTarget'] = _LISTINGTARGET
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ShipTypeFilter = _reflection.GeneratedProtocolMessageType('ShipTypeFilter', (_message.Message,), {'DESCRIPTOR': _SHIPTYPEFILTER,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(ShipTypeFilter)
Filter = _reflection.GeneratedProtocolMessageType('Filter', (_message.Message,), {'DESCRIPTOR': _FILTER,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(Filter)
Order = _reflection.GeneratedProtocolMessageType('Order', (_message.Message,), {'DESCRIPTOR': _ORDER,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(Order)
TargetPublic = _reflection.GeneratedProtocolMessageType('TargetPublic', (_message.Message,), {'DESCRIPTOR': _TARGETPUBLIC,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(TargetPublic)
TargetMyCorporation = _reflection.GeneratedProtocolMessageType('TargetMyCorporation', (_message.Message,), {'DESCRIPTOR': _TARGETMYCORPORATION,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(TargetMyCorporation)
TargetMyAlliance = _reflection.GeneratedProtocolMessageType('TargetMyAlliance', (_message.Message,), {'DESCRIPTOR': _TARGETMYALLIANCE,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(TargetMyAlliance)
TargetMyCharacter = _reflection.GeneratedProtocolMessageType('TargetMyCharacter', (_message.Message,), {'DESCRIPTOR': _TARGETMYCHARACTER,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(TargetMyCharacter)
TargetAll = _reflection.GeneratedProtocolMessageType('TargetAll', (_message.Message,), {'DESCRIPTOR': _TARGETALL,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(TargetAll)
ListingTarget = _reflection.GeneratedProtocolMessageType('ListingTarget', (_message.Message,), {'DESCRIPTOR': _LISTINGTARGET,
 '__module__': 'eve.cosmetic.market.skin.search.search_pb2'})
_sym_db.RegisterMessage(ListingTarget)
DESCRIPTOR._options = None
