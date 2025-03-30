#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\character_pb2.py
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.bloodline import bloodline_pb2 as eve_dot_bloodline_dot_bloodline__pb2
from eveProto.generated.eve.race import race_pb2 as eve_dot_race_dot_race__pb2
from eveProto.generated.eve.school import school_pb2 as eve_dot_school_dot_school__pb2
from eveProto.generated.eve import search_pb2 as eve_dot_search__pb2
from eveProto.generated.eve.securitystatus import securitystatus_pb2 as eve_dot_securitystatus_dot_securitystatus__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/character.proto', package='eve.character', syntax='proto3', serialized_options='Z8github.com/ccpgames/eve-proto-go/generated/eve/character', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/character/character.proto\x12\reve.character\x1a\x1deve/bloodline/bloodline.proto\x1a\x13eve/race/race.proto\x1a\x17eve/school/school.proto\x1a\x10eve/search.proto\x1a\'eve/securitystatus/securitystatus.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1fgoogle/protobuf/timestamp.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\r"\xeb\x02\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x12%\n\x06gender\x18\x02 \x01(\x0e2\x15.eve.character.Gender\x12\x11\n\tbiography\x18\x03 \x01(\t\x12,\n\x08birthday\x18\x04 \x01(\x0b2\x1a.google.protobuf.Timestamp\x122\n\x0fsecurity_status\x18\x0c \x01(\x0b2\x19.eve.securitystatus.Value\x12&\n\x06school\x18\x0e \x01(\x0b2\x16.eve.school.Identifier\x12"\n\x04race\x18\x0f \x01(\x0b2\x14.eve.race.Identifier\x12,\n\tbloodline\x18\x10 \x01(\x0b2\x19.eve.bloodline.Identifier\x12!\n\x15security_status_float\x18\n \x01(\x02B\x02\x18\x01J\x04\x08\x05\x10\x08J\x04\x08\x08\x10\nJ\x04\x08\x0b\x10\x0cJ\x04\x08\r\x10\x0e":\n\nGetRequest\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier";\n\x0bGetResponse\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Attributes"0\n\rSearchRequest\x12\x1f\n\x05query\x18\x01 \x01(\x0b2\x10.eve.SearchQuery"?\n\x0eSearchResponse\x12-\n\ncharacters\x18\x01 \x03(\x0b2\x19.eve.character.Identifier"_\n\x0bNameChanged\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12\x10\n\x08old_name\x18\x02 \x01(\t\x12\x10\n\x08new_name\x18\x03 \x01(\t"@\n\x0cIdleDetected\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"C\n\x0fActivityResumed\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier:\x02\x18\x01"t\n\x07Onlined\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier:\x02\x18\x01J\x04\x08\x03\x10\x04"o\n\x08Offlined\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier:\x02\x18\x01*\x1e\n\x06Gender\x12\n\n\x06FEMALE\x10\x00\x12\x08\n\x04MALE\x10\x01B:Z8github.com/ccpgames/eve-proto-go/generated/eve/characterb\x06proto3', dependencies=[eve_dot_bloodline_dot_bloodline__pb2.DESCRIPTOR,
 eve_dot_race_dot_race__pb2.DESCRIPTOR,
 eve_dot_school_dot_school__pb2.DESCRIPTOR,
 eve_dot_search__pb2.DESCRIPTOR,
 eve_dot_securitystatus_dot_securitystatus__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_GENDER = _descriptor.EnumDescriptor(name='Gender', full_name='eve.character.Gender', filename=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key, values=[_descriptor.EnumValueDescriptor(name='FEMALE', index=0, number=0, serialized_options=None, type=None, create_key=_descriptor._internal_create_key), _descriptor.EnumValueDescriptor(name='MALE', index=1, number=1, serialized_options=None, type=None, create_key=_descriptor._internal_create_key)], containing_type=None, serialized_options=None, serialized_start=1351, serialized_end=1381)
_sym_db.RegisterEnumDescriptor(_GENDER)
Gender = enum_type_wrapper.EnumTypeWrapper(_GENDER)
FEMALE = 0
MALE = 1
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.character.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.character.Identifier.sequential', index=0, number=1, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=252, serialized_end=284)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.character.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve.character.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='gender', full_name='eve.character.Attributes.gender', index=1, number=2, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='biography', full_name='eve.character.Attributes.biography', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='birthday', full_name='eve.character.Attributes.birthday', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='security_status', full_name='eve.character.Attributes.security_status', index=4, number=12, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='school', full_name='eve.character.Attributes.school', index=5, number=14, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='race', full_name='eve.character.Attributes.race', index=6, number=15, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='bloodline', full_name='eve.character.Attributes.bloodline', index=7, number=16, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='security_status_float', full_name='eve.character.Attributes.security_status_float', index=8, number=10, type=2, cpp_type=6, label=1, has_default_value=False, default_value=float(0), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options='\x18\x01', file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=287, serialized_end=650)
_GETREQUEST = _descriptor.Descriptor(name='GetRequest', full_name='eve.character.GetRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.GetRequest.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=652, serialized_end=710)
_GETRESPONSE = _descriptor.Descriptor(name='GetResponse', full_name='eve.character.GetResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.GetResponse.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=712, serialized_end=771)
_SEARCHREQUEST = _descriptor.Descriptor(name='SearchRequest', full_name='eve.character.SearchRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='query', full_name='eve.character.SearchRequest.query', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=773, serialized_end=821)
_SEARCHRESPONSE = _descriptor.Descriptor(name='SearchResponse', full_name='eve.character.SearchResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='characters', full_name='eve.character.SearchResponse.characters', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=823, serialized_end=886)
_NAMECHANGED = _descriptor.Descriptor(name='NameChanged', full_name='eve.character.NameChanged', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.NameChanged.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='old_name', full_name='eve.character.NameChanged.old_name', index=1, number=2, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='new_name', full_name='eve.character.NameChanged.new_name', index=2, number=3, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=888, serialized_end=983)
_IDLEDETECTED = _descriptor.Descriptor(name='IdleDetected', full_name='eve.character.IdleDetected', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.IdleDetected.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=985, serialized_end=1049)
_ACTIVITYRESUMED = _descriptor.Descriptor(name='ActivityResumed', full_name='eve.character.ActivityResumed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.ActivityResumed.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1051, serialized_end=1118)
_ONLINED = _descriptor.Descriptor(name='Onlined', full_name='eve.character.Onlined', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.Onlined.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.character.Onlined.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1120, serialized_end=1236)
_OFFLINED = _descriptor.Descriptor(name='Offlined', full_name='eve.character.Offlined', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.character.Offlined.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='solar_system', full_name='eve.character.Offlined.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options='\x18\x01', is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=1238, serialized_end=1349)
_ATTRIBUTES.fields_by_name['gender'].enum_type = _GENDER
_ATTRIBUTES.fields_by_name['birthday'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_ATTRIBUTES.fields_by_name['security_status'].message_type = eve_dot_securitystatus_dot_securitystatus__pb2._VALUE
_ATTRIBUTES.fields_by_name['school'].message_type = eve_dot_school_dot_school__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['race'].message_type = eve_dot_race_dot_race__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['bloodline'].message_type = eve_dot_bloodline_dot_bloodline__pb2._IDENTIFIER
_GETREQUEST.fields_by_name['character'].message_type = _IDENTIFIER
_GETRESPONSE.fields_by_name['character'].message_type = _ATTRIBUTES
_SEARCHREQUEST.fields_by_name['query'].message_type = eve_dot_search__pb2._SEARCHQUERY
_SEARCHRESPONSE.fields_by_name['characters'].message_type = _IDENTIFIER
_NAMECHANGED.fields_by_name['character'].message_type = _IDENTIFIER
_IDLEDETECTED.fields_by_name['character'].message_type = _IDENTIFIER
_ACTIVITYRESUMED.fields_by_name['character'].message_type = _IDENTIFIER
_ONLINED.fields_by_name['character'].message_type = _IDENTIFIER
_ONLINED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_OFFLINED.fields_by_name['character'].message_type = _IDENTIFIER
_OFFLINED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['GetRequest'] = _GETREQUEST
DESCRIPTOR.message_types_by_name['GetResponse'] = _GETRESPONSE
DESCRIPTOR.message_types_by_name['SearchRequest'] = _SEARCHREQUEST
DESCRIPTOR.message_types_by_name['SearchResponse'] = _SEARCHRESPONSE
DESCRIPTOR.message_types_by_name['NameChanged'] = _NAMECHANGED
DESCRIPTOR.message_types_by_name['IdleDetected'] = _IDLEDETECTED
DESCRIPTOR.message_types_by_name['ActivityResumed'] = _ACTIVITYRESUMED
DESCRIPTOR.message_types_by_name['Onlined'] = _ONLINED
DESCRIPTOR.message_types_by_name['Offlined'] = _OFFLINED
DESCRIPTOR.enum_types_by_name['Gender'] = _GENDER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(Attributes)
GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {'DESCRIPTOR': _GETREQUEST,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(GetRequest)
GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {'DESCRIPTOR': _GETRESPONSE,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(GetResponse)
SearchRequest = _reflection.GeneratedProtocolMessageType('SearchRequest', (_message.Message,), {'DESCRIPTOR': _SEARCHREQUEST,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(SearchRequest)
SearchResponse = _reflection.GeneratedProtocolMessageType('SearchResponse', (_message.Message,), {'DESCRIPTOR': _SEARCHRESPONSE,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(SearchResponse)
NameChanged = _reflection.GeneratedProtocolMessageType('NameChanged', (_message.Message,), {'DESCRIPTOR': _NAMECHANGED,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(NameChanged)
IdleDetected = _reflection.GeneratedProtocolMessageType('IdleDetected', (_message.Message,), {'DESCRIPTOR': _IDLEDETECTED,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(IdleDetected)
ActivityResumed = _reflection.GeneratedProtocolMessageType('ActivityResumed', (_message.Message,), {'DESCRIPTOR': _ACTIVITYRESUMED,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(ActivityResumed)
Onlined = _reflection.GeneratedProtocolMessageType('Onlined', (_message.Message,), {'DESCRIPTOR': _ONLINED,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(Onlined)
Offlined = _reflection.GeneratedProtocolMessageType('Offlined', (_message.Message,), {'DESCRIPTOR': _OFFLINED,
 '__module__': 'eve.character.character_pb2'})
_sym_db.RegisterMessage(Offlined)
DESCRIPTOR._options = None
_ATTRIBUTES.fields_by_name['security_status_float']._options = None
_IDLEDETECTED._options = None
_ACTIVITYRESUMED._options = None
_ONLINED._options = None
_OFFLINED._options = None
