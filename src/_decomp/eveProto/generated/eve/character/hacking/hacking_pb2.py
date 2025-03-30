#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\character\hacking\hacking_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/character/hacking/hacking.proto', package='eve.character.hacking', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/character/hacking', create_key=_descriptor._internal_create_key, serialized_pb='\n#eve/character/hacking/hacking.proto\x12\x15eve.character.hacking"4\n\x08Analyzer\x12\x0e\n\x04data\x18\x01 \x01(\x08H\x00\x12\x0f\n\x05relic\x18\x02 \x01(\x08H\x00B\x07\n\x05groupBBZ@github.com/ccpgames/eve-proto-go/generated/eve/character/hackingb\x06proto3')
_ANALYZER = _descriptor.Descriptor(name='Analyzer', full_name='eve.character.hacking.Analyzer', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='data', full_name='eve.character.hacking.Analyzer.data', index=0, number=1, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='relic', full_name='eve.character.hacking.Analyzer.relic', index=1, number=2, type=8, cpp_type=7, label=1, has_default_value=False, default_value=False, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='group', full_name='eve.character.hacking.Analyzer.group', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=62, serialized_end=114)
_ANALYZER.oneofs_by_name['group'].fields.append(_ANALYZER.fields_by_name['data'])
_ANALYZER.fields_by_name['data'].containing_oneof = _ANALYZER.oneofs_by_name['group']
_ANALYZER.oneofs_by_name['group'].fields.append(_ANALYZER.fields_by_name['relic'])
_ANALYZER.fields_by_name['relic'].containing_oneof = _ANALYZER.oneofs_by_name['group']
DESCRIPTOR.message_types_by_name['Analyzer'] = _ANALYZER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Analyzer = _reflection.GeneratedProtocolMessageType('Analyzer', (_message.Message,), {'DESCRIPTOR': _ANALYZER,
 '__module__': 'eve.character.hacking.hacking_pb2'})
_sym_db.RegisterMessage(Analyzer)
DESCRIPTOR._options = None
