#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\clones\clone_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.character.implant import implant_pb2 as eve_dot_character_dot_implant_dot_implant__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/clones/clone.proto', package='eve.character.clone', syntax='proto3', serialized_options='Z>github.com/ccpgames/eve-proto-go/generated/eve/character/clone', create_key=_descriptor._internal_create_key, serialized_pb='\n eve/character/clones/clone.proto\x12\x13eve.character.clone\x1a\x1deve/character/character.proto\x1a#eve/character/implant/implant.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xdb\x01\n\nAttributes\x12-\n\x08implants\x18\x01 \x03(\x0b2\x1b.eve.character.implant.Type\x12*\n\x07station\x18\x02 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\x05 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x121\n\x08clone_id\x18\x04 \x01(\x0b2\x1f.eve.character.clone.IdentifierB\t\n\x07versionJ\x04\x08\x03\x10\x04"K\n\x1bGetClonesByCharacterRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"\xc4\x02\n\x1cGetClonesByCharacterResponse\x12/\n\x06clones\x18\x01 \x03(\x0b2\x1f.eve.character.clone.Attributes\x128\n\x14last_clone_jump_date\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12<\n\x18last_station_change_date\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12/\n\x0chome_station\x18\x04 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x123\n\x0ehome_structure\x18\x06 \x01(\x0b2\x19.eve.structure.IdentifierH\x00B\x0f\n\rhome_locationJ\x04\x08\x05\x10\x06B@Z>github.com/ccpgames/eve-proto-go/generated/eve/character/cloneb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_character_dot_implant_dot_implant__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.clone.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.clone.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=216, serialized_end=248)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.clone.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='implants', full_name='eve.character.clone.Attributes.implants', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.character.clone.Attributes.station', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.character.clone.Attributes.structure', index=2, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='clone_id', full_name='eve.character.clone.Attributes.clone_id', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='version', full_name='eve.character.clone.Attributes.version', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=251, serialized_end=470)
_GETCLONESBYCHARACTERREQUEST = _descriptor.Descriptor(name='GetClonesByCharacterRequest', full_name='eve.character.clone.GetClonesByCharacterRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.clone.GetClonesByCharacterRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=472, serialized_end=547)
_GETCLONESBYCHARACTERRESPONSE = _descriptor.Descriptor(name='GetClonesByCharacterResponse', full_name='eve.character.clone.GetClonesByCharacterResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='clones', full_name='eve.character.clone.GetClonesByCharacterResponse.clones', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_clone_jump_date', full_name='eve.character.clone.GetClonesByCharacterResponse.last_clone_jump_date', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='last_station_change_date', full_name='eve.character.clone.GetClonesByCharacterResponse.last_station_change_date', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='home_station', full_name='eve.character.clone.GetClonesByCharacterResponse.home_station', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='home_structure', full_name='eve.character.clone.GetClonesByCharacterResponse.home_structure', index=4, number=6, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='home_location', full_name='eve.character.clone.GetClonesByCharacterResponse.home_location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=550, serialized_end=874)
_ATTRIBUTES.fields_by_name['implants'].message_type = eve_dot_character_dot_implant_dot_implant__pb2._TYPE
_ATTRIBUTES.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['clone_id'].message_type = _IDENTIFIER
_ATTRIBUTES.oneofs_by_name['version'].fields.append(_ATTRIBUTES.fields_by_name['station'])
_ATTRIBUTES.fields_by_name['station'].containing_oneof = _ATTRIBUTES.oneofs_by_name['version']
_ATTRIBUTES.oneofs_by_name['version'].fields.append(_ATTRIBUTES.fields_by_name['structure'])
_ATTRIBUTES.fields_by_name['structure'].containing_oneof = _ATTRIBUTES.oneofs_by_name['version']
_GETCLONESBYCHARACTERREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['clones'].message_type = _ATTRIBUTES
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['last_clone_jump_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['last_station_change_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_GETCLONESBYCHARACTERRESPONSE.oneofs_by_name['home_location'].fields.append(_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_station'])
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_station'].containing_oneof = _GETCLONESBYCHARACTERRESPONSE.oneofs_by_name['home_location']
_GETCLONESBYCHARACTERRESPONSE.oneofs_by_name['home_location'].fields.append(_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_structure'])
_GETCLONESBYCHARACTERRESPONSE.fields_by_name['home_structure'].containing_oneof = _GETCLONESBYCHARACTERRESPONSE.oneofs_by_name['home_location']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetClonesByCharacterRequest'] = _GETCLONESBYCHARACTERREQUEST
DESCRIPTOR.message_types_by_name['GetClonesByCharacterResponse'] = _GETCLONESBYCHARACTERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.clones.clone_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.clones.clone_pb2'})
_sym_db.RegisterMessage(Attributes)
GetClonesByCharacterRequest = _reflection.GeneratedProtocolMessageType('GetClonesByCharacterRequest', (_message.Message,), {'DESCRIPTOR': _GETCLONESBYCHARACTERREQUEST,
 '__module__': 'eve.character.clones.clone_pb2'})
_sym_db.RegisterMessage(GetClonesByCharacterRequest)
GetClonesByCharacterResponse = _reflection.GeneratedProtocolMessageType('GetClonesByCharacterResponse', (_message.Message,), {'DESCRIPTOR': _GETCLONESBYCHARACTERRESPONSE,
 '__module__': 'eve.character.clones.clone_pb2'})
_sym_db.RegisterMessage(GetClonesByCharacterResponse)
DESCRIPTOR._options = None
