#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\assets\networth_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.isk import isk_pb2 as eve_dot_isk_dot_isk__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/assets/networth.proto', package='eve.character.assets.networth', syntax='proto3', serialized_options='ZHgithub.com/ccpgames/eve-proto-go/generated/eve/character/assets/networth', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/character/assets/networth.proto\x12\x1deve.character.assets.networth\x1a\x1deve/character/character.proto\x1a\x11eve/isk/isk.proto":\n\nGetRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"P\n\x0bGetResponse\x12A\n\x13character_net_worth\x18\x01 \x01(\x0b2$.eve.character.assets.networth.Value"3\n\x05Value\x12*\n\x0ftotal_net_worth\x18\x01 \x01(\x0b2\x11.eve.isk.CurrencyBJZHgithub.com/ccpgames/eve-proto-go/generated/eve/character/assets/networthb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_isk_dot_isk__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.character.assets.networth.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.assets.networth.GetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=120, serialized_end=178)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.character.assets.networth.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character_net_worth', full_name='eve.character.assets.networth.GetResponse.character_net_worth', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=180, serialized_end=260)
_VALUE = _descriptor.Descriptor(name='Value', full_name='eve.character.assets.networth.Value', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='total_net_worth', full_name='eve.character.assets.networth.Value.total_net_worth', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=262, serialized_end=313)
_GETREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['character_net_worth'].message_type = _VALUE
_VALUE.fields_by_name['total_net_worth'].message_type = eve_dot_isk_dot_isk__pb2._CURRENCY
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['Value'] = _VALUE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.character.assets.networth_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.character.assets.networth_pb2'})
_sym_db.RegisterMessage(GetResponse)
Value = _reflection.GeneratedProtocolMessageType('Value', (_message.Message,), {'DESCRIPTOR': _VALUE,
 '__module__': 'eve.character.assets.networth_pb2'})
_sym_db.RegisterMessage(Value)
DESCRIPTOR._options = None
