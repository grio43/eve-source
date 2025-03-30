#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\corporation\titles_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.corporation import title_pb2 as eve_dot_corporation_dot_title__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/corporation/titles.proto', package='eve.character.corporation.titles', syntax='proto3', serialized_options='ZKgithub.com/ccpgames/eve-proto-go/generated/eve/character/corporation/titles', create_key=_descriptor._internal_create_key, serialized_pb='\n&eve/character/corporation/titles.proto\x12 eve.character.corporation.titles\x1a\x1deve/character/character.proto\x1a\x1beve/corporation/title.proto"@\n\rGetAllRequest\x12/\n\x0ccharacter_id\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"\xcd\x01\n\x0eGetAllResponse\x12F\n\x06titles\x18\x01 \x03(\x0b26.eve.character.corporation.titles.GetAllResponse.Title\x1as\n\x05Title\x123\n\x08title_id\x18\x01 \x01(\x0b2!.eve.corporation.title.Identifier\x125\n\nattributes\x18\x02 \x01(\x0b2!.eve.corporation.title.AttributesBMZKgithub.com/ccpgames/eve-proto-go/generated/eve/character/corporation/titlesb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR, eve_dot_corporation_dot_title__pb2.DESCRIPTOR])
_GETALLREQUEST = _descriptor.Descriptor(name='GetAllRequest', full_name='eve.character.corporation.titles.GetAllRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character_id', full_name='eve.character.corporation.titles.GetAllRequest.character_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=136, serialized_end=200)
_GETALLRESPONSE_TITLE = _descriptor.Descriptor(name='Title', full_name='eve.character.corporation.titles.GetAllResponse.Title', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='title_id', full_name='eve.character.corporation.titles.GetAllResponse.Title.title_id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.character.corporation.titles.GetAllResponse.Title.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=293, serialized_end=408)
_GETALLRESPONSE = _descriptor.Descriptor(name='GetAllResponse', full_name='eve.character.corporation.titles.GetAllResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='titles', full_name='eve.character.corporation.titles.GetAllResponse.titles', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_GETALLRESPONSE_TITLE], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=203, serialized_end=408)
_GETALLREQUEST.fields_by_name['character_id'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETALLRESPONSE_TITLE.fields_by_name['title_id'].message_type = eve_dot_corporation_dot_title__pb2._IDENTIFIER
_GETALLRESPONSE_TITLE.fields_by_name['attributes'].message_type = eve_dot_corporation_dot_title__pb2._ATTRIBUTES
_GETALLRESPONSE_TITLE.containing_type = _GETALLRESPONSE
_GETALLRESPONSE.fields_by_name['titles'].message_type = _GETALLRESPONSE_TITLE
DESCRIPTOR.message_types_by_name['GetAllRequest'] = _GETALLREQUEST
DESCRIPTOR.message_types_by_name['GetAllResponse'] = _GETALLRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
GetAllRequest = _reflection.GeneratedProtocolMessageType('GetAllRequest', (_message.Message,), {'DESCRIPTOR': _GETALLREQUEST,
 '__module__': 'eve.character.corporation.titles_pb2'})
_sym_db.RegisterMessage(GetAllRequest)
GetAllResponse = _reflection.GeneratedProtocolMessageType('GetAllResponse', (_message.Message,), {'Title': _reflection.GeneratedProtocolMessageType('Title', (_message.Message,), {'DESCRIPTOR': _GETALLRESPONSE_TITLE,
           '__module__': 'eve.character.corporation.titles_pb2'}),
 'DESCRIPTOR': _GETALLRESPONSE,
 '__module__': 'eve.character.corporation.titles_pb2'})
_sym_db.RegisterMessage(GetAllResponse)
_sym_db.RegisterMessage(GetAllResponse.Title)
DESCRIPTOR._options = None
