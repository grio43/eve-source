#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\implant\implant_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/implant/implant.proto', package='eve.character.implant', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/character/implant', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/character/implant/implant.proto\x12\x15eve.character.implant\x1a\x1deve/character/character.proto"\x1a\n\x04Type\x12\x12\n\nsequential\x18\x01 \x01(\r" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"7\n\nAttributes\x12)\n\x04type\x18\x01 \x01(\x0b2\x1b.eve.character.implant.Type"S\n#GetActiveImplantsByCharacterRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier"[\n$GetActiveImplantsByCharacterResponse\x123\n\x08implants\x18\x01 \x03(\x0b2!.eve.character.implant.AttributesBBZ@github.com/ccpgames/eve-proto-go/generated/eve/character/implantb\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR])
_TYPE = _descriptor.Descriptor(name='Type', full_name='eve.character.implant.Type', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.implant.Type.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=119)
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.implant.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.implant.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=121, serialized_end=153)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.implant.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='type', full_name='eve.character.implant.Attributes.type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=155, serialized_end=210)
_GETACTIVEIMPLANTSBYCHARACTERREQUEST = _descriptor.Descriptor(name='GetActiveImplantsByCharacterRequest', full_name='eve.character.implant.GetActiveImplantsByCharacterRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.implant.GetActiveImplantsByCharacterRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=212, serialized_end=295)
_GETACTIVEIMPLANTSBYCHARACTERRESPONSE = _descriptor.Descriptor(name='GetActiveImplantsByCharacterResponse', full_name='eve.character.implant.GetActiveImplantsByCharacterResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='implants', full_name='eve.character.implant.GetActiveImplantsByCharacterResponse.implants', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=297, serialized_end=388)
_ATTRIBUTES.fields_by_name['type'].message_type = _TYPE
_GETACTIVEIMPLANTSBYCHARACTERREQUEST.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_GETACTIVEIMPLANTSBYCHARACTERRESPONSE.fields_by_name['implants'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Type'] = _TYPE
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetActiveImplantsByCharacterRequest'] = _GETACTIVEIMPLANTSBYCHARACTERREQUEST
DESCRIPTOR.message_types_by_name['GetActiveImplantsByCharacterResponse'] = _GETACTIVEIMPLANTSBYCHARACTERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Type = _reflection.GeneratedProtocolMessageType('Type', (_message.Message,), {'DESCRIPTOR': _TYPE,
 '__module__': 'eve.character.implant.implant_pb2'})
_sym_db.RegisterMessage(Type)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.implant.implant_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.implant.implant_pb2'})
_sym_db.RegisterMessage(Attributes)
GetActiveImplantsByCharacterRequest = _reflection.GeneratedProtocolMessageType('GetActiveImplantsByCharacterRequest', (_message.Message,), {'DESCRIPTOR': _GETACTIVEIMPLANTSBYCHARACTERREQUEST,
 '__module__': 'eve.character.implant.implant_pb2'})
_sym_db.RegisterMessage(GetActiveImplantsByCharacterRequest)
GetActiveImplantsByCharacterResponse = _reflection.GeneratedProtocolMessageType('GetActiveImplantsByCharacterResponse', (_message.Message,), {'DESCRIPTOR': _GETACTIVEIMPLANTSBYCHARACTERRESPONSE,
 '__module__': 'eve.character.implant.implant_pb2'})
_sym_db.RegisterMessage(GetActiveImplantsByCharacterResponse)
DESCRIPTOR._options = None
