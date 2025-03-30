#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\vanguard\skirmish\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.pirate.insurgency import campaign_pb2 as eve_dot_pirate_dot_insurgency_dot_campaign__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/vanguard/skirmish/api/events.proto', package='eve.vanguard.insurgency.api', syntax='proto3', serialized_options='ZDgithub.com/ccpgames/eve-proto-go/generated/eve/vanguard/skirmish/api', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/vanguard/skirmish/api/events.proto\x12\x1beve.vanguard.insurgency.api\x1a$eve/pirate/insurgency/campaign.proto"\xf1\x01\n\x11SkirmishCompleted\x123\n\x08campaign\x18\x01 \x01(\x0b2!.eve.pirate.insurgency.Identifier\x12G\n\x07outcome\x18\x02 \x01(\x0e26.eve.vanguard.insurgency.api.SkirmishCompleted.Outcome"^\n\x07Outcome\x12\x17\n\x13OUTCOME_UNSPECIFIED\x10\x00\x12\x12\n\x0ePIRATE_VICTORY\x10\x01\x12\x17\n\x13ANTI_PIRATE_VICTORY\x10\x02\x12\r\n\tNO_WINNER\x10\x03BFZDgithub.com/ccpgames/eve-proto-go/generated/eve/vanguard/skirmish/apib\x06proto3', dependencies=[eve_dot_pirate_dot_insurgency_dot_campaign__pb2.DESCRIPTOR])
_SKIRMISHCOMPLETED_OUTCOME = _descriptor.EnumDescriptor(name='Outcome', full_name='eve.vanguard.insurgency.api.SkirmishCompleted.Outcome', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='OUTCOME_UNSPECIFIED', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='PIRATE_VICTORY', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='ANTI_PIRATE_VICTORY', index=2, number=2, serialized_options=None, type=None, create_key=_descriptor._internal_create_key),
 _descriptor.EnumValueDescriptor(name='NO_WINNER', index=3, number=3, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=257, serialized_end=351)
_sym_db.RegisterEnumDescriptor(_SKIRMISHCOMPLETED_OUTCOME)
_SKIRMISHCOMPLETED = _descriptor.Descriptor(name='SkirmishCompleted', full_name='eve.vanguard.insurgency.api.SkirmishCompleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='campaign', full_name='eve.vanguard.insurgency.api.SkirmishCompleted.campaign', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='outcome', full_name='eve.vanguard.insurgency.api.SkirmishCompleted.outcome', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[_SKIRMISHCOMPLETED_OUTCOME], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=110, serialized_end=351)
_SKIRMISHCOMPLETED.fields_by_name['campaign'].message_type = eve_dot_pirate_dot_insurgency_dot_campaign__pb2._IDENTIFIER
_SKIRMISHCOMPLETED.fields_by_name['outcome'].enum_type = _SKIRMISHCOMPLETED_OUTCOME
_SKIRMISHCOMPLETED_OUTCOME.containing_type = _SKIRMISHCOMPLETED
DESCRIPTOR.message_types_by_name['SkirmishCompleted'] = _SKIRMISHCOMPLETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SkirmishCompleted = _reflection.GeneratedProtocolMessageType('SkirmishCompleted', (_message.Message,), {'DESCRIPTOR': _SKIRMISHCOMPLETED,
 '__module__': 'eve.vanguard.skirmish.api.events_pb2'})
_sym_db.RegisterMessage(SkirmishCompleted)
DESCRIPTOR._options = None
