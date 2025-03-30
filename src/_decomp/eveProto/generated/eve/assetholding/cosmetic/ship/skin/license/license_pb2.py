#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\assetholding\cosmetic\ship\skin\license\license_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty import thirdparty_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/assetholding/cosmetic/ship/skin/license/license.proto', package='eve.assetholding.cosmetic.ship.skin.license', syntax='proto3', serialized_options='ZVgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/cosmetic/ship/skin/license', create_key=_descriptor._internal_create_key, serialized_pb='\n9eve/assetholding/cosmetic/ship/skin/license/license.proto\x12+eve.assetholding.cosmetic.ship.skin.license\x1a2eve/cosmetic/ship/skin/thirdparty/thirdparty.proto"C\n\x04Unit\x12;\n\x04skin\x18\x01 \x01(\x0b2-.eve.cosmetic.ship.skin.thirdparty.Identifier"f\n\x0eHoldParameters\x12B\n\x07license\x18\x01 \x01(\x0b21.eve.assetholding.cosmetic.ship.skin.license.Unit\x12\x10\n\x08capacity\x18\x02 \x01(\x04"\x12\n\x10RedeemParametersBXZVgithub.com/ccpgames/eve-proto-go/generated/eve/assetholding/cosmetic/ship/skin/licenseb\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2.DESCRIPTOR])
_UNIT = _descriptor.Descriptor(name='Unit', full_name='eve.assetholding.cosmetic.ship.skin.license.Unit', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='skin', full_name='eve.assetholding.cosmetic.ship.skin.license.Unit.skin', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=158, serialized_end=225)
_HOLDPARAMETERS = _descriptor.Descriptor(name='HoldParameters', full_name='eve.assetholding.cosmetic.ship.skin.license.HoldParameters', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.assetholding.cosmetic.ship.skin.license.HoldParameters.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='capacity', full_name='eve.assetholding.cosmetic.ship.skin.license.HoldParameters.capacity', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=227, serialized_end=329)
_REDEEMPARAMETERS = _descriptor.Descriptor(name='RedeemParameters', full_name='eve.assetholding.cosmetic.ship.skin.license.RedeemParameters', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=331, serialized_end=349)
_UNIT.fields_by_name['skin'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_thirdparty__pb2._IDENTIFIER
_HOLDPARAMETERS.fields_by_name['license'].message_type = _UNIT
DESCRIPTOR.message_types_by_name['Unit'] = _UNIT
DESCRIPTOR.message_types_by_name['HoldParameters'] = _HOLDPARAMETERS
DESCRIPTOR.message_types_by_name['RedeemParameters'] = _REDEEMPARAMETERS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Unit = _reflection.GeneratedProtocolMessageType('Unit', (_message.Message,), {'DESCRIPTOR': _UNIT,
 '__module__': 'eve.assetholding.cosmetic.ship.skin.license.license_pb2'})
_sym_db.RegisterMessage(Unit)
HoldParameters = _reflection.GeneratedProtocolMessageType('HoldParameters', (_message.Message,), {'DESCRIPTOR': _HOLDPARAMETERS,
 '__module__': 'eve.assetholding.cosmetic.ship.skin.license.license_pb2'})
_sym_db.RegisterMessage(HoldParameters)
RedeemParameters = _reflection.GeneratedProtocolMessageType('RedeemParameters', (_message.Message,), {'DESCRIPTOR': _REDEEMPARAMETERS,
 '__module__': 'eve.assetholding.cosmetic.ship.skin.license.license_pb2'})
_sym_db.RegisterMessage(RedeemParameters)
DESCRIPTOR._options = None
