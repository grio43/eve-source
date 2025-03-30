#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\tale\api\requests_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.tale import spawntemplate_pb2 as eve_dot_tale_dot_spawntemplate__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/tale/api/requests.proto', package='eve.tale.api', syntax='proto3', serialized_options='Z7github.com/ccpgames/eve-proto-go/generated/eve/tale/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1beve/tale/api/requests.proto\x12\x0ceve.tale.api\x1a!eve/solarsystem/solarsystem.proto\x1a\x1ceve/tale/spawntemplate.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\xd0\x02\n\x10StartTaleRequest\x12:\n\x0espawn_template\x18\x01 \x01(\x0b2".eve.tale.spawntemplate.Identifier\x121\n\x0csolar_system\x18\x02 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x12\x17\n\rdefault_start\x18\x03 \x01(\x08H\x00\x12\x19\n\x0fimmediate_start\x18\x04 \x01(\x08H\x00\x129\n\x13specific_start_time\x18\x05 \x01(\x0b2\x1a.google.protobuf.TimestampH\x00\x12\x15\n\x0bdefault_end\x18\x06 \x01(\x08H\x01\x127\n\x11specific_end_time\x18\x07 \x01(\x0b2\x1a.google.protobuf.TimestampH\x01B\x07\n\x05startB\x05\n\x03end"\x13\n\x11StartTaleResponseB9Z7github.com/ccpgames/eve-proto-go/generated/eve/tale/apib\x06proto3', dependencies=[eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR, eve_dot_tale_dot_spawntemplate__pb2.DESCRIPTOR, google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR])
_STARTTALEREQUEST = _descriptor.Descriptor(name='StartTaleRequest', full_name='eve.tale.api.StartTaleRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='spawn_template', full_name='eve.tale.api.StartTaleRequest.spawn_template', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solar_system', full_name='eve.tale.api.StartTaleRequest.solar_system', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='default_start', full_name='eve.tale.api.StartTaleRequest.default_start', index=2, number=3, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='immediate_start', full_name='eve.tale.api.StartTaleRequest.immediate_start', index=3, number=4, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='specific_start_time', full_name='eve.tale.api.StartTaleRequest.specific_start_time', index=4, number=5, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='default_end', full_name='eve.tale.api.StartTaleRequest.default_end', index=5, number=6, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='specific_end_time', full_name='eve.tale.api.StartTaleRequest.specific_end_time', index=6, number=7, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='start', full_name='eve.tale.api.StartTaleRequest.start', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[]), _descriptor.OneofDescriptor(name='end', full_name='eve.tale.api.StartTaleRequest.end', index=1, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=144, serialized_end=480)
_STARTTALERESPONSE = _descriptor.Descriptor(name='StartTaleResponse', full_name='eve.tale.api.StartTaleResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=482, serialized_end=501)
_STARTTALEREQUEST.fields_by_name['spawn_template'].message_type = eve_dot_tale_dot_spawntemplate__pb2._IDENTIFIER
_STARTTALEREQUEST.fields_by_name['solar_system'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_STARTTALEREQUEST.fields_by_name['specific_start_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_STARTTALEREQUEST.fields_by_name['specific_end_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_STARTTALEREQUEST.oneofs_by_name['start'].fields.append(_STARTTALEREQUEST.fields_by_name['default_start'])
_STARTTALEREQUEST.fields_by_name['default_start'].containing_oneof = _STARTTALEREQUEST.oneofs_by_name['start']
_STARTTALEREQUEST.oneofs_by_name['start'].fields.append(_STARTTALEREQUEST.fields_by_name['immediate_start'])
_STARTTALEREQUEST.fields_by_name['immediate_start'].containing_oneof = _STARTTALEREQUEST.oneofs_by_name['start']
_STARTTALEREQUEST.oneofs_by_name['start'].fields.append(_STARTTALEREQUEST.fields_by_name['specific_start_time'])
_STARTTALEREQUEST.fields_by_name['specific_start_time'].containing_oneof = _STARTTALEREQUEST.oneofs_by_name['start']
_STARTTALEREQUEST.oneofs_by_name['end'].fields.append(_STARTTALEREQUEST.fields_by_name['default_end'])
_STARTTALEREQUEST.fields_by_name['default_end'].containing_oneof = _STARTTALEREQUEST.oneofs_by_name['end']
_STARTTALEREQUEST.oneofs_by_name['end'].fields.append(_STARTTALEREQUEST.fields_by_name['specific_end_time'])
_STARTTALEREQUEST.fields_by_name['specific_end_time'].containing_oneof = _STARTTALEREQUEST.oneofs_by_name['end']
DESCRIPTOR.message_types_by_name['StartTaleRequest'] = _STARTTALEREQUEST
DESCRIPTOR.message_types_by_name['StartTaleResponse'] = _STARTTALERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
StartTaleRequest = _reflection.GeneratedProtocolMessageType('StartTaleRequest', (_message.Message,), {'DESCRIPTOR': _STARTTALEREQUEST,
 '__module__': 'eve.tale.api.requests_pb2'})
_sym_db.RegisterMessage(StartTaleRequest)
StartTaleResponse = _reflection.GeneratedProtocolMessageType('StartTaleResponse', (_message.Message,), {'DESCRIPTOR': _STARTTALERESPONSE,
 '__module__': 'eve.tale.api.requests_pb2'})
_sym_db.RegisterMessage(StartTaleResponse)
DESCRIPTOR._options = None
