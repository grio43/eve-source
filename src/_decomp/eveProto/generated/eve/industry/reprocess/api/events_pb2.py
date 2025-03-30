#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\industry\reprocess\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.character import character_pb2 as eve_dot_character_dot_character__pb2
from eveProto.generated.eve.industry.reprocess import input_type_pb2 as eve_dot_industry_dot_reprocess_dot_input__type__pb2
from eveProto.generated.eve.industry.reprocess import output_type_pb2 as eve_dot_industry_dot_reprocess_dot_output__type__pb2
from eveProto.generated.eve.station import station_pb2 as eve_dot_station_dot_station__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/industry/reprocess/api/events.proto', package='eve.industry.reprocess.api', syntax='proto3', serialized_options='ZEgithub.com/ccpgames/eve-proto-go/generated/eve/industry/reprocess/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\'eve/industry/reprocess/api/events.proto\x12\x1aeve.industry.reprocess.api\x1a\x1deve/character/character.proto\x1a\'eve/industry/reprocess/input_type.proto\x1a(eve/industry/reprocess/output_type.proto\x1a\x19eve/station/station.proto\x1a\x1deve/structure/structure.proto"\x9a\x03\n\x0bReprocessed\x12,\n\tcharacter\x18\x01 \x01(\x0b2\x19.eve.character.Identifier\x12*\n\x07station\x18\x02 \x01(\x0b2\x17.eve.station.IdentifierH\x00\x12.\n\tstructure\x18\x03 \x01(\x0b2\x19.eve.structure.IdentifierH\x00\x12A\n\ninput_type\x18\x04 \x01(\x0b2-.eve.industry.reprocess.input_type.Identifier\x12\x10\n\x08quantity\x18\x05 \x01(\r\x12?\n\x07outputs\x18\x06 \x03(\x0b2..eve.industry.reprocess.api.Reprocessed.Output\x1a_\n\x06Output\x12C\n\x0boutput_type\x18\x01 \x01(\x0b2..eve.industry.reprocess.output_type.Identifier\x12\x10\n\x08quantity\x18\x02 \x01(\rB\n\n\x08locationBGZEgithub.com/ccpgames/eve-proto-go/generated/eve/industry/reprocess/apib\x06proto3', dependencies=[eve_dot_character_dot_character__pb2.DESCRIPTOR,
 eve_dot_industry_dot_reprocess_dot_input__type__pb2.DESCRIPTOR,
 eve_dot_industry_dot_reprocess_dot_output__type__pb2.DESCRIPTOR,
 eve_dot_station_dot_station__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR])
_REPROCESSED_OUTPUT = _descriptor.Descriptor(name='Output', full_name='eve.industry.reprocess.api.Reprocessed.Output', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='output_type', full_name='eve.industry.reprocess.api.Reprocessed.Output.output_type', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='quantity', full_name='eve.industry.reprocess.api.Reprocessed.Output.quantity', index=1, number=2, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=547, serialized_end=642)
_REPROCESSED = _descriptor.Descriptor(name='Reprocessed', full_name='eve.industry.reprocess.api.Reprocessed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='character', full_name='eve.industry.reprocess.api.Reprocessed.character', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='station', full_name='eve.industry.reprocess.api.Reprocessed.station', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='structure', full_name='eve.industry.reprocess.api.Reprocessed.structure', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='input_type', full_name='eve.industry.reprocess.api.Reprocessed.input_type', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='quantity', full_name='eve.industry.reprocess.api.Reprocessed.quantity', index=4, number=5, type=13, cpp_type=3, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='outputs', full_name='eve.industry.reprocess.api.Reprocessed.outputs', index=5, number=6, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[_REPROCESSED_OUTPUT], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='location', full_name='eve.industry.reprocess.api.Reprocessed.location', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=244, serialized_end=654)
_REPROCESSED_OUTPUT.fields_by_name['output_type'].message_type = eve_dot_industry_dot_reprocess_dot_output__type__pb2._IDENTIFIER
_REPROCESSED_OUTPUT.containing_type = _REPROCESSED
_REPROCESSED.fields_by_name['character'].message_type = eve_dot_character_dot_character__pb2._IDENTIFIER
_REPROCESSED.fields_by_name['station'].message_type = eve_dot_station_dot_station__pb2._IDENTIFIER
_REPROCESSED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_REPROCESSED.fields_by_name['input_type'].message_type = eve_dot_industry_dot_reprocess_dot_input__type__pb2._IDENTIFIER
_REPROCESSED.fields_by_name['outputs'].message_type = _REPROCESSED_OUTPUT
_REPROCESSED.oneofs_by_name['location'].fields.append(_REPROCESSED.fields_by_name['station'])
_REPROCESSED.fields_by_name['station'].containing_oneof = _REPROCESSED.oneofs_by_name['location']
_REPROCESSED.oneofs_by_name['location'].fields.append(_REPROCESSED.fields_by_name['structure'])
_REPROCESSED.fields_by_name['structure'].containing_oneof = _REPROCESSED.oneofs_by_name['location']
DESCRIPTOR.message_types_by_name['Reprocessed'] = _REPROCESSED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Reprocessed = _reflection.GeneratedProtocolMessageType('Reprocessed', (_message.Message,), {'Output': _reflection.GeneratedProtocolMessageType('Output', (_message.Message,), {'DESCRIPTOR': _REPROCESSED_OUTPUT,
            '__module__': 'eve.industry.reprocess.api.events_pb2'}),
 'DESCRIPTOR': _REPROCESSED,
 '__module__': 'eve.industry.reprocess.api.events_pb2'})
_sym_db.RegisterMessage(Reprocessed)
_sym_db.RegisterMessage(Reprocessed.Output)
DESCRIPTOR._options = None
