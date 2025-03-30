#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\tale\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.tale import spawntemplate_pb2 as eve_dot_tale_dot_spawntemplate__pb2
from eveProto.generated.eve.tale import tale_pb2 as eve_dot_tale_dot_tale__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/tale/api/events.proto', package='eve.tale.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/tale/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x19eve/tale/api/events.proto\x12\x0ceve.tale.api\x1a!eve/solarsystem/solarsystem.proto\x1a\x1ceve/tale/spawntemplate.proto\x1a\x13eve/tale/tale.proto\x1a\x1egoogle/protobuf/duration.proto"\xdc\x01\n\x07Started\x12(\n\nidentifier\x18\x01 \x01(\x0b2\x14.eve.tale.Identifier\x12?\n\x13template_identifier\x18\x02 \x01(\x0b2".eve.tale.spawntemplate.Identifier\x121\n\x0csolar_system\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x123\n\x10planned_duration\x18\x04 \x01(\x0b2\x19.google.protobuf.Duration"1\n\x05Ended\x12(\n\nidentifier\x18\x01 \x01(\x0b2\x14.eve.tale.IdentifierB9Z7github.com/ccpgames/eve-proto-go/generated/eve/tale/apib\x06proto3', dependencies=[eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_tale_dot_spawntemplate__pb2.DESCRIPTOR,
 eve_dot_tale_dot_tale__pb2.DESCRIPTOR,
 google_dot_protobuf_dot_duration__pb2.DESCRIPTOR])
_STARTED = _descriptor.Descriptor(name='Started', full_name='eve.tale.api.Started', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.tale.api.Started.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='template_identifier', full_name='eve.tale.api.Started.template_identifier', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.tale.api.Started.solar_system', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='planned_duration', full_name='eve.tale.api.Started.planned_duration', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=162, serialized_end=382)
_ENDED = _descriptor.Descriptor(name='Ended', full_name='eve.tale.api.Ended', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='identifier', full_name='eve.tale.api.Ended.identifier', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=384, serialized_end=433)
_STARTED.fields_by_name['identifier'].message_type = eve_dot_tale_dot_tale__pb2._IDENTIFIER
_STARTED.fields_by_name['template_identifier'].message_type = eve_dot_tale_dot_spawntemplate__pb2._IDENTIFIER
_STARTED.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_STARTED.fields_by_name['planned_duration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_ENDED.fields_by_name['identifier'].message_type = eve_dot_tale_dot_tale__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Started'] = _STARTED
DESCRIPTOR.message_types_by_name['Ended'] = _ENDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Started = _reflection.GeneratedProtocolMessageType('Started', (_message.Message,), {'DESCRIPTOR': _STARTED,
 '__module__': 'eve.tale.api.events_pb2'})
_sym_db.RegisterMessage(Started)
Ended = _reflection.GeneratedProtocolMessageType('Ended', (_message.Message,), {'DESCRIPTOR': _ENDED,
 '__module__': 'eve.tale.api.events_pb2'})
_sym_db.RegisterMessage(Ended)
DESCRIPTOR._options = None
