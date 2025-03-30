#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\structure\upwell\state_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/structure/upwell/state.proto', package='eve.structure.upwell', syntax='proto3', serialized_options='Z?github.com/ccpgames/eve-proto-go/generated/eve/structure/upwell', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/structure/upwell/state.proto\x12\x14eve.structure.upwell*\xe7\x02\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x14\n\x10STATE_UNANCHORED\x10\x01\x12\x13\n\x0fSTATE_ANCHORING\x10\x02\x12\x1e\n\x1aSTATE_FITTING_INVULNERABLE\x10\x03\x12\x1d\n\x19STATE_ONLINING_VULNERABLE\x10\x04\x12\x1b\n\x17STATE_SHIELD_VULNERABLE\x10\x05\x12\x19\n\x15STATE_ARMOR_REINFORCE\x10\x06\x12\x1a\n\x16STATE_ARMOR_VULNERABLE\x10\x07\x12\x18\n\x14STATE_HULL_REINFORCE\x10\x08\x12\x19\n\x15STATE_HULL_VULNERABLE\x10\t\x12\x1b\n\x17STATE_ANCHOR_VULNERABLE\x10\n\x12\x1b\n\x17STATE_DEPLOY_VULNERABLE\x10\x0b\x12\x1a\n\x16STATE_FOB_INVULNERABLE\x10\x0cBAZ?github.com/ccpgames/eve-proto-go/generated/eve/structure/upwellb\x06proto3')
_STATE = _descriptor.EnumDescriptor(name='State', full_name='eve.structure.upwell.State', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='STATE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_UNANCHORED', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_ANCHORING', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_FITTING_INVULNERABLE', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_ONLINING_VULNERABLE', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_SHIELD_VULNERABLE', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_ARMOR_REINFORCE', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_ARMOR_VULNERABLE', index=7, number=7, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_HULL_REINFORCE', index=8, number=8, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_HULL_VULNERABLE', index=9, number=9, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_ANCHOR_VULNERABLE', index=10, number=10, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_DEPLOY_VULNERABLE', index=11, number=11, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='STATE_FOB_INVULNERABLE', index=12, number=12, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=59, serialized_end=418)
_sym_db.RegisterEnumDescriptor(_STATE)
State = enum_type_wrapper.EnumTypeWrapper(_STATE)
STATE_UNSPECIFIED = 0
STATE_UNANCHORED = 1
STATE_ANCHORING = 2
STATE_FITTING_INVULNERABLE = 3
STATE_ONLINING_VULNERABLE = 4
STATE_SHIELD_VULNERABLE = 5
STATE_ARMOR_REINFORCE = 6
STATE_ARMOR_VULNERABLE = 7
STATE_HULL_REINFORCE = 8
STATE_HULL_VULNERABLE = 9
STATE_ANCHOR_VULNERABLE = 10
STATE_DEPLOY_VULNERABLE = 11
STATE_FOB_INVULNERABLE = 12
DESCRIPTOR.enum_types_by_name['State'] = _STATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
DESCRIPTOR._options = None
