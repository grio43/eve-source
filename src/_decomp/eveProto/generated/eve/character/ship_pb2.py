#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\ship_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.ship import ship_pb2 as eve_dot_ship_dot_ship__pb2
from eveProto.generated.eve.ship import ship_type_pb2 as eve_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/ship.proto', package='eve.character.ship', syntax='proto3', serialized_options='Z=github.com/ccpgames/eve-proto-go/generated/eve/character/ship', create_key=_descriptor._internal_create_key, serialized_pb='\n\x18eve/character/ship.proto\x12\x12eve.character.ship\x1a\x1deve/character/character.proto\x1a\x13eve/ship/ship.proto\x1a\x18eve/ship/ship_type.proto"=\n\nGetRequest\x12/\n\x0ccharacter_id\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"w\n\x0bGetResponse\x12%\n\x07ship_id\x18\x01 \x01(\x0b2\x14.eve.ship.Identifier\x12.\n\x0cship_type_id\x18\x02 \x01(\x0b2\x18.eve.shiptype.Identifier\x12\x11\n\tship_name\x18\x03 \x01(\tB?Z=github.com/ccpgames/eve-proto-go/generated/eve/character/shipb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__pb2.DESCRIPTOR, eve_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.character.ship.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character_id', full_name='eve.character.ship.GetRequest.character_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=126, serialized_end=187)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.character.ship.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship_id', full_name='eve.character.ship.GetResponse.ship_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ship_type_id', full_name='eve.character.ship.GetResponse.ship_type_id', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='ship_name', full_name='eve.character.ship.GetResponse.ship_name', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=189, serialized_end=308)
_GETREQUEST.fields_by_name['character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['ship_id'].message_type = eve_dot_ship_dot_ship__pb2._IDENTIFIER
_GETRESPONSE.fields_by_name['ship_type_id'].message_type = eve_dot_ship_dot_ship__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.character.ship_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.character.ship_pb2'})
_sym_db.RegisterMessage(GetResponse)
DESCRIPTOR._options = None
