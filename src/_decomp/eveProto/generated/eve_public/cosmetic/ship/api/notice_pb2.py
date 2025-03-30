#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\ship\api\notice_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.cosmetic.ship import ship_pb2 as eve__public_dot_cosmetic_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/ship/api/notice.proto', package='eve_public.cosmetic.ship.api', syntax='proto3', serialized_options='ZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/api', create_key=_descriptor._internal_create_key, serialized_pb='\n)eve_public/cosmetic/ship/api/notice.proto\x12\x1ceve_public.cosmetic.ship.api\x1a#eve_public/cosmetic/ship/ship.proto";\n\tSetNotice\x12.\n\x05state\x18\x01 \x01(\x0b2\x1f.eve_public.cosmetic.ship.State"F\n\x14SetAllInBubbleNotice\x12.\n\x05state\x18\x01 \x03(\x0b2\x1f.eve_public.cosmetic.ship.StateBIZGgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/apib\x06proto3', dependencies=[eve__public_dot_cosmetic_dot_ship_dot_ship__pb2.DESCRIPTOR])
_SETNOTICE = _descriptor.Descriptor(name='SetNotice', full_name='eve_public.cosmetic.ship.api.SetNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='state', full_name='eve_public.cosmetic.ship.api.SetNotice.state', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=112, serialized_end=171)
_SETALLINBUBBLENOTICE = _descriptor.Descriptor(name='SetAllInBubbleNotice', full_name='eve_public.cosmetic.ship.api.SetAllInBubbleNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='state', full_name='eve_public.cosmetic.ship.api.SetAllInBubbleNotice.state', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=173, serialized_end=243)
_SETNOTICE.fields_by_name['state'].message_type = eve__public_dot_cosmetic_dot_ship_dot_ship__pb2._STATE
_SETALLINBUBBLENOTICE.fields_by_name['state'].message_type = eve__public_dot_cosmetic_dot_ship_dot_ship__pb2._STATE
DESCRIPTOR.message_types_by_name['SetNotice'] = _SETNOTICE
DESCRIPTOR.message_types_by_name['SetAllInBubbleNotice'] = _SETALLINBUBBLENOTICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
SetNotice = _reflection.GeneratedProtocolMessageType('SetNotice', (_message.Message,), {'DESCRIPTOR': _SETNOTICE,
 '__module__': 'eve_public.cosmetic.ship.api.notice_pb2'})
_sym_db.RegisterMessage(SetNotice)
SetAllInBubbleNotice = _reflection.GeneratedProtocolMessageType('SetAllInBubbleNotice', (_message.Message,), {'DESCRIPTOR': _SETALLINBUBBLENOTICE,
 '__module__': 'eve_public.cosmetic.ship.api.notice_pb2'})
_sym_db.RegisterMessage(SetAllInBubbleNotice)
DESCRIPTOR._options = None
