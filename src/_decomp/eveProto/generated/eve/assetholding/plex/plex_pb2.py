#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\assetholding\plex\plex_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.plex import plex_pb2 as eve_dot_plex_dot_plex__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/assetholding/plex/plex.proto', package='eve.assetholding.plex', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/assetholding/plex', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/assetholding/plex/plex.proto\x12\x15eve.assetholding.plex\x1a\x13eve/plex/plex.proto"(\n\x04Unit\x12 \n\x04plex\x18\x01 \x01(\x0b2\x12.eve.plex.Currency"M\n\x0eHoldParameters\x12)\n\x04unit\x18\x01 \x01(\x0b2\x1b.eve.assetholding.plex.Unit\x12\x10\n\x08capacity\x18\x02 \x01(\x04"n\n\x0fSpawnParameters\x12)\n\x04unit\x18\x01 \x01(\x0b2\x1b.eve.assetholding.plex.Unit\x12\x12\n\x08infinite\x18\x02 \x01(\x08H\x00\x12\x10\n\x06finite\x18\x03 \x01(\x04H\x00B\n\n\x08capacity"\x12\n\x10RedeemParametersBBZ@github.com/ccpgames/eve-proto-go/generated/eve/assetholding/plexb\x06proto3', dependencies=[eve_dot_plex_dot_plex__pb2.DESCRIPTOR])
_UNIT = _descriptor.Descriptor(name='Unit', full_name='eve.assetholding.plex.Unit', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='plex', full_name='eve.assetholding.plex.Unit.plex', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=80, serialized_end=120)
_HOLDPARAMETERS = _descriptor.Descriptor(name='HoldParameters', full_name='eve.assetholding.plex.HoldParameters', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unit', full_name='eve.assetholding.plex.HoldParameters.unit', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='capacity', full_name='eve.assetholding.plex.HoldParameters.capacity', index=1, number=2, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=122, serialized_end=199)
_SPAWNPARAMETERS = _descriptor.Descriptor(name='SpawnParameters', full_name='eve.assetholding.plex.SpawnParameters', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unit', full_name='eve.assetholding.plex.SpawnParameters.unit', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='infinite', full_name='eve.assetholding.plex.SpawnParameters.infinite', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='finite', full_name='eve.assetholding.plex.SpawnParameters.finite', index=2, number=3, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='capacity', full_name='eve.assetholding.plex.SpawnParameters.capacity', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=201, serialized_end=311)
_REDEEMPARAMETERS = _descriptor.Descriptor(name='RedeemParameters', full_name='eve.assetholding.plex.RedeemParameters', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=313, serialized_end=331)
_UNIT.fields_by_name['plex'].message_type = eve_dot_plex_dot_plex__pb2._CURRENCY
_HOLDPARAMETERS.fields_by_name['unit'].message_type = _UNIT
_SPAWNPARAMETERS.fields_by_name['unit'].message_type = _UNIT
_SPAWNPARAMETERS.oneofs_by_name['capacity'].fields.append(_SPAWNPARAMETERS.fields_by_name['infinite'])
_SPAWNPARAMETERS.fields_by_name['infinite'].containing_oneof = _SPAWNPARAMETERS.oneofs_by_name['capacity']
_SPAWNPARAMETERS.oneofs_by_name['capacity'].fields.append(_SPAWNPARAMETERS.fields_by_name['finite'])
_SPAWNPARAMETERS.fields_by_name['finite'].containing_oneof = _SPAWNPARAMETERS.oneofs_by_name['capacity']
DESCRIPTOR.message_types_by_name['Unit'] = _UNIT
DESCRIPTOR.message_types_by_name['HoldParameters'] = _HOLDPARAMETERS
DESCRIPTOR.message_types_by_name['SpawnParameters'] = _SPAWNPARAMETERS
DESCRIPTOR.message_types_by_name['RedeemParameters'] = _REDEEMPARAMETERS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Unit = _reflection.GeneratedProtocolMessageType('Unit', (_message.Message,), {'DESCRIPTOR': _UNIT,
 '__module__': 'eve.assetholding.plex.plex_pb2'})
_sym_db.RegisterMessage(Unit)
HoldParameters = _reflection.GeneratedProtocolMessageType('HoldParameters', (_message.Message,), {'DESCRIPTOR': _HOLDPARAMETERS,
 '__module__': 'eve.assetholding.plex.plex_pb2'})
_sym_db.RegisterMessage(HoldParameters)
SpawnParameters = _reflection.GeneratedProtocolMessageType('SpawnParameters', (_message.Message,), {'DESCRIPTOR': _SPAWNPARAMETERS,
 '__module__': 'eve.assetholding.plex.plex_pb2'})
_sym_db.RegisterMessage(SpawnParameters)
RedeemParameters = _reflection.GeneratedProtocolMessageType('RedeemParameters', (_message.Message,), {'DESCRIPTOR': _REDEEMPARAMETERS,
 '__module__': 'eve.assetholding.plex.plex_pb2'})
_sym_db.RegisterMessage(RedeemParameters)
DESCRIPTOR._options = None
