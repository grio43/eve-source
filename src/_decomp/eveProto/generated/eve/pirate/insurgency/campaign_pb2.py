#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\pirate\insurgency\campaign_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/pirate/insurgency/campaign.proto', package='eve.pirate.insurgency', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/pirate/insurgency', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve/pirate/insurgency/campaign.proto\x12\x15eve.pirate.insurgency" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04*\x81\x01\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\x0c\n\x08FORECAST\x10\x01\x12\n\n\x06ACTIVE\x10\x02\x12\x12\n\x0ePIRATE_VICTORY\x10\x03\x12\x17\n\x13ANTI_PIRATE_VICTORY\x10\x04\x12\r\n\tNO_WINNER\x10\x05\x12\x0b\n\x07CLEANUP\x10\x06BBZ@github.com/ccpgames/eve-proto-go/generated/eve/pirate/insurgencyb\x06proto3')
_STATE = _descriptor.EnumDescriptor(name='State', full_name='eve.pirate.insurgency.State', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='STATE_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='FORECAST', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ACTIVE', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PIRATE_VICTORY', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ANTI_PIRATE_VICTORY', index=4, number=4, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='NO_WINNER', index=5, number=5, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='CLEANUP', index=6, number=6, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=98, serialized_end=227)
_sym_db.RegisterEnumDescriptor(_STATE)
State = enum_type_wrapper.EnumTypeWrapper(_STATE)
STATE_UNSPECIFIED = 0
FORECAST = 1
ACTIVE = 2
PIRATE_VICTORY = 3
ANTI_PIRATE_VICTORY = 4
NO_WINNER = 5
CLEANUP = 6
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.pirate.insurgency.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.pirate.insurgency.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=63, serialized_end=95)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.enum_types_by_name['State'] = _STATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.pirate.insurgency.campaign_pb2'})
_sym_db.RegisterMessage(Identifier)
DESCRIPTOR._options = None
