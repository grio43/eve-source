#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\legacy_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.inventory import generic_item_pb2 as eve_dot_inventory_dot_generic__item__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/legacy.proto', package='eve.legacy', syntax='proto3', serialized_options='Z5github.com/ccpgames/eve-proto-go/generated/eve/legacy', create_key=_descriptor._internal_create_key, serialized_pb='\n\x10eve/legacy.proto\x12\neve.legacy\x1a eve/inventory/generic_item.proto"\x88\x01\n\x05Owner\x12\n\n\x02id\x18\x01 \x01(\x05\x12,\n\x08category\x18\x02 \x01(\x0e2\x1a.eve.legacy.Owner.Category"E\n\x08Category\x12\r\n\tCHARACTER\x10\x00\x12\x0f\n\x0bCORPORATION\x10\x01\x12\x0c\n\x08ALLIANCE\x10\x02\x12\x0b\n\x07FACTION\x10\x03"N\n\x14ResolveOwnersRequest\x126\n\x07item_id\x18\x01 \x03(\x0b2%.eve.inventory.genericitem.Identifier"C\n\x15ResolveOwnersResponse\x12*\n\x0fresolved_owners\x18\x01 \x03(\x0b2\x11.eve.legacy.Owner2d\n\x0cLegacyOwners\x12T\n\rResolveOwners\x12 .eve.legacy.ResolveOwnersRequest\x1a!.eve.legacy.ResolveOwnersResponseB7Z5github.com/ccpgames/eve-proto-go/generated/eve/legacyb\x06proto3', dependencies=[eve_dot_inventory_dot_generic__item__pb2.DESCRIPTOR])
_OWNER_CATEGORY = _descriptor.EnumDescriptor(name='Category', full_name='eve.legacy.Owner.Category', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='CHARACTER', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CORPORATION', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ALLIANCE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FACTION', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=134, serialized_end=203)
_sym_db.RegisterEnumDescriptor(_OWNER_CATEGORY)
_OWNER = _descriptor.Descriptor(name='Owner', full_name='eve.legacy.Owner', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.legacy.Owner.id', index=0, number=1, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='category', full_name='eve.legacy.Owner.category', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_OWNER_CATEGORY], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=67, serialized_end=203)
_RESOLVEOWNERSREQUEST = _descriptor.Descriptor(name='ResolveOwnersRequest', full_name='eve.legacy.ResolveOwnersRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='item_id', full_name='eve.legacy.ResolveOwnersRequest.item_id', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=205, serialized_end=283)
_RESOLVEOWNERSRESPONSE = _descriptor.Descriptor(name='ResolveOwnersResponse', full_name='eve.legacy.ResolveOwnersResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='resolved_owners', full_name='eve.legacy.ResolveOwnersResponse.resolved_owners', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=285, serialized_end=352)
_OWNER.fields_by_name['category'].enum_type = _OWNER_CATEGORY
_OWNER_CATEGORY.containing_type = _OWNER
_RESOLVEOWNERSREQUEST.fields_by_name['item_id'].message_type = eve_dot_inventory_dot_generic__item__pb2._IDENTIFIER
_RESOLVEOWNERSRESPONSE.fields_by_name['resolved_owners'].message_type = _OWNER
DESCRIPTOR.message_types_by_name['Owner'] = _OWNER
DESCRIPTOR.message_types_by_name['ResolveOwnersRequest'] = _RESOLVEOWNERSREQUEST
DESCRIPTOR.message_types_by_name['ResolveOwnersResponse'] = _RESOLVEOWNERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Owner = _reflection.GeneratedProtocolMessageType('Owner', (_message.Message,), {'DESCRIPTOR': _OWNER,
 '__module__': 'eve.legacy_pb2'})
_sym_db.RegisterMessage(Owner)
ResolveOwnersRequest = _reflection.GeneratedProtocolMessageType('ResolveOwnersRequest', (_message.Message,), {'DESCRIPTOR': _RESOLVEOWNERSREQUEST,
 '__module__': 'eve.legacy_pb2'})
_sym_db.RegisterMessage(ResolveOwnersRequest)
ResolveOwnersResponse = _reflection.GeneratedProtocolMessageType('ResolveOwnersResponse', (_message.Message,), {'DESCRIPTOR': _RESOLVEOWNERSRESPONSE,
 '__module__': 'eve.legacy_pb2'})
_sym_db.RegisterMessage(ResolveOwnersResponse)
DESCRIPTOR._options = None
_LEGACYOWNERS = _descriptor.ServiceDescriptor(name='LegacyOwners', full_name='eve.legacy.LegacyOwners', file=DESCRIPTOR, index=0, serialized_options=None, create_key=_descriptor._internal_create_key, serialized_start=354, serialized_end=454, methods=[_descriptor.MethodDescriptor(name='ResolveOwners', full_name='eve.legacy.LegacyOwners.ResolveOwners', index=0, containing_service=None, input_type=_RESOLVEOWNERSREQUEST, output_type=_RESOLVEOWNERSRESPONSE, serialized_options=None, create_key=_descriptor._internal_create_key)])
_sym_db.RegisterServiceDescriptor(_LEGACYOWNERS)
DESCRIPTOR.services_by_name['LegacyOwners'] = _LEGACYOWNERS
