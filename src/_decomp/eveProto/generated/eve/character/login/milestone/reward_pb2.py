#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\login\milestone\reward_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
from eveProto.generated.eve.login import milestone_pb2 as eve_dot_login_dot_milestone__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/login/milestone/reward.proto', package='eve.character.login.milestone.reward', syntax='proto3', serialized_options='ZOgithub.com/ccpgames/eve-proto-go/generated/eve/character/login/milestone/reward', create_key=_descriptor._internal_create_key, serialized_pb='\n*eve/character/login/milestone/reward.proto\x12$eve.character.login.milestone.reward\x1a\x1deve/character/character.proto\x1a\x11eve/isk/isk.proto\x1a\x19eve/login/milestone.proto"\xb2\x01\n\x07Claimed\x12/\n\x0ccharacter_id\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x122\n\tmilestone\x18\x02 \x01(\x0b2\x1f.eve.login.milestone.Identifier\x12\x13\n\tno_reward\x18\x03 \x01(\x08H\x00\x12#\n\x06amount\x18\x04 \x01(\x0b2\x11.eve.isk.CurrencyH\x00B\x08\n\x06rewardBQZOgithub.com/ccpgames/eve-proto-go/generated/eve/character/login/milestone/rewardb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR, eve_dot_login_dot_milestone__pb2.DESCRIPTOR])
_CLAIMED = _descriptor.Descriptor(name='Claimed', full_name='eve.character.login.milestone.reward.Claimed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character_id', full_name='eve.character.login.milestone.reward.Claimed.character_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='milestone', full_name='eve.character.login.milestone.reward.Claimed.milestone', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='no_reward', full_name='eve.character.login.milestone.reward.Claimed.no_reward', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='amount', full_name='eve.character.login.milestone.reward.Claimed.amount', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='reward', full_name='eve.character.login.milestone.reward.Claimed.reward', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=162, serialized_end=340)
_CLAIMED.fields_by_name['character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_CLAIMED.fields_by_name['milestone'].message_type = eve_dot_login_dot_milestone__pb2._IDENTIFIER
_CLAIMED.fields_by_name['amount'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
_CLAIMED.oneofs_by_name['reward'].fields.append(_CLAIMED.fields_by_name['no_reward'])
_CLAIMED.fields_by_name['no_reward'].containing_oneof = _CLAIMED.oneofs_by_name['reward']
_CLAIMED.oneofs_by_name['reward'].fields.append(_CLAIMED.fields_by_name['amount'])
_CLAIMED.fields_by_name['amount'].containing_oneof = _CLAIMED.oneofs_by_name['reward']
DESCRIPTOR.message_types_by_name['Claimed'] = _CLAIMED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Claimed = _reflection.GeneratedProtocolMessageType('Claimed', (_message.Message,), {'DESCRIPTOR': _CLAIMED,
 '__module__': 'eve.character.login.milestone.reward_pb2'})
_sym_db.RegisterMessage(Claimed)
DESCRIPTOR._options = None
