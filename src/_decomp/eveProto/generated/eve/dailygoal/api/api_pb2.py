#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\dailygoal\api\api_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.assetholding.entitlement import entitlement_pb2 as eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.dailygoal import goal_pb2 as eve_dot_dailygoal_dot_goal__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/dailygoal/api/api.proto', package='eve.dailygoal.api', syntax='proto3', serialized_options='Z<github.com/ccpgames/eve-proto-go/generated/eve/dailygoal/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/dailygoal/api/api.proto\x12\x11eve.dailygoal.api\x1a.eve/assetholding/entitlement/entitlement.proto\x1a\x1deve/character/character.proto\x1a\x18eve/dailygoal/goal.proto\x1a\x1fgoogle/protobuf/timestamp.proto"5\n\nGetRequest\x12\'\n\x04goal\x18\x01 \x01(\x0b2\x19.eve.dailygoal.Identifier"6\n\x0bGetResponse\x12\'\n\x04goal\x18\x01 \x01(\x0b2\x19.eve.dailygoal.Attributes"\x0f\n\rGetAllRequest":\n\x0eGetAllResponse\x12(\n\x05goals\x18\x01 \x03(\x0b2\x19.eve.dailygoal.Identifier"k\n\x12GetProgressRequest\x12\'\n\x04goal\x18\x01 \x01(\x0b2\x19.eve.dailygoal.Identifier\x12,\n\tcharacter\x18\x02 \x01(\x0b2\x19.eve.character.Identifier"\xf0\x01\n\x13GetProgressResponse\x12\x0f\n\x07current\x18\x01 \x01(\x04\x12B\n\x0centitlements\x18\x02 \x03(\x0b2(.eve.assetholding.entitlement.IdentifierB\x02\x18\x01\x12\x17\n\rnot_completed\x18\x03 \x01(\x08H\x00\x12/\n\tcompleted\x18\x04 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12,\n\x08earnings\x18\x05 \x03(\x0b2\x1a.eve.dailygoal.api.EarningB\x0c\n\ncompletion"D\n\x07Earning\x12!\n\x04unit\x18\x01 \x01(\x0b2\x13.eve.dailygoal.Unit\x12\x16\n\x0eomega_required\x18\x02 \x01(\x08B>Z<github.com/ccpgames/eve-proto-go/generated/eve/dailygoal/apib\x06proto3', dependencies=[eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2.DESCRIPTOR,
 eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_dailygoal_dot_goal__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.dailygoal.api.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve.dailygoal.api.GetRequest.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=188, serialized_end=241)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.dailygoal.api.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve.dailygoal.api.GetResponse.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=243, serialized_end=297)
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.dailygoal.api.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=299, serialized_end=314)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.dailygoal.api.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goals', full_name='eve.dailygoal.api.GetAllResponse.goals', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=316, serialized_end=374)
_GETPROGRESSREQUEST = _descriptor.Descriptor(name='GetProgressRequest', full_name='eve.dailygoal.api.GetProgressRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='goal', full_name='eve.dailygoal.api.GetProgressRequest.goal', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='character', full_name='eve.dailygoal.api.GetProgressRequest.character', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=376, serialized_end=483)
_GETPROGRESSRESPONSE = _descriptor.Descriptor(name='GetProgressResponse', full_name='eve.dailygoal.api.GetProgressResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='current', full_name='eve.dailygoal.api.GetProgressResponse.current', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='entitlements', full_name='eve.dailygoal.api.GetProgressResponse.entitlements', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='not_completed', full_name='eve.dailygoal.api.GetProgressResponse.not_completed', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='completed', full_name='eve.dailygoal.api.GetProgressResponse.completed', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='earnings', full_name='eve.dailygoal.api.GetProgressResponse.earnings', index=4, number=5, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='completion', full_name='eve.dailygoal.api.GetProgressResponse.completion', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=486, serialized_end=726)
_EARNING = _descriptor.Descriptor(name='Earning', full_name='eve.dailygoal.api.Earning', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unit', full_name='eve.dailygoal.api.Earning.unit', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='omega_required', full_name='eve.dailygoal.api.Earning.omega_required', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=728, serialized_end=796)
_GETREQUEST.fields_by_name['goal'].message_type = eve_dot_dailygoal_dot_goal__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['goal'].message_type = eve_dot_dailygoal_dot_goal__pb2._ATTRIBUTES
_GETALLRESPONSE.fields_by_name['goals'].message_type = eve_dot_dailygoal_dot_goal__pb2._IDENTIFIER
_GETPROGRESSREQUEST.fields_by_name['goal'].message_type = eve_dot_dailygoal_dot_goal__pb2._IDENTIFIER
_GETPROGRESSREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETPROGRESSRESPONSE.fields_by_name['entitlements'].message_type = eve_dot_assetholding_dot_entitlement_dot_entitlement__pb2._IDENTIFIER
_GETPROGRESSRESPONSE.fields_by_name['completed'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETPROGRESSRESPONSE.fields_by_name['earnings'].message_type = _EARNING
_GETPROGRESSRESPONSE.oneofs_by_name['completion'].fields.append(_GETPROGRESSRESPONSE.fields_by_name['not_completed'])
_GETPROGRESSRESPONSE.fields_by_name['not_completed'].containing_oneof = _GETPROGRESSRESPONSE.oneofs_by_name['completion']
_GETPROGRESSRESPONSE.oneofs_by_name['completion'].fields.append(_GETPROGRESSRESPONSE.fields_by_name['completed'])
_GETPROGRESSRESPONSE.fields_by_name['completed'].containing_oneof = _GETPROGRESSRESPONSE.oneofs_by_name['completion']
_EARNING.fields_by_name['unit'].message_type = eve_dot_dailygoal_dot_goal__pb2._UNIT
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
DESCRIPTOR.message_types_by_name['GetProgressRequest'] = _GETPROGRESSREQUEST
DESCRIPTOR.message_types_by_name['GetProgressResponse'] = _GETPROGRESSRESPONSE
DESCRIPTOR.message_types_by_name['Earning'] = _EARNING
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetResponse)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
GetProgressRequest = _reflection.GeneratedProtocolMessageType('GetProgressRequest', (_message.Message,), {'DESCRIPTOR': _GETPROGRESSREQUEST,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetProgressRequest)
GetProgressResponse = _reflection.GeneratedProtocolMessageType('GetProgressResponse', (_message.Message,), {'DESCRIPTOR': _GETPROGRESSRESPONSE,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(GetProgressResponse)
Earning = _reflection.GeneratedProtocolMessageType('Earning', (_message.Message,), {'DESCRIPTOR': _EARNING,
 '__module__': 'eve.dailygoal.api.api_pb2'})
_sym_db.RegisterMessage(Earning)
DESCRIPTOR._options = None
_GETPROGRESSRESPONSE.fields_by_name['entitlements']._options = None
