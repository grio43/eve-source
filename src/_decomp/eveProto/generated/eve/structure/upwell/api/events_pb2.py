#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\structure\upwell\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
from eveProto.generated.eve.solarsystem import solarsystem_pb2 as eve_dot_solarsystem_dot_solarsystem__pb2
from eveProto.generated.eve.structure import structure_pb2 as eve_dot_structure_dot_structure__pb2
from eveProto.generated.eve.structure import structure_type_pb2 as eve_dot_structure_dot_structure__type__pb2
from eveProto.generated.eve.structure.upwell import state_pb2 as eve_dot_structure_dot_upwell_dot_state__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/structure/upwell/api/events.proto', package='eve.structure.upwell.api', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/structure/upwell/api', create_key=_descriptor._internal_create_key, serialized_pb='\n%eve/structure/upwell/api/events.proto\x12\x18eve.structure.upwell.api\x1a!eve/corporation/corporation.proto\x1a!eve/solarsystem/solarsystem.proto\x1a\x1deve/structure/structure.proto\x1a"eve/structure/structure_type.proto\x1a eve/structure/upwell/state.proto"\xb6\x02\n\x11StateTransitioned\x12,\n\tstructure\x18\x01 \x01(\x0b2\x19.eve.structure.Identifier\x122\n\x0bupwell_type\x18\x02 \x01(\x0b2\x1d.eve.structuretype.Identifier\x120\n\x0bsolarsystem\x18\x03 \x01(\x0b2\x1b.eve.solarsystem.Identifier\x120\n\x0bcorporation\x18\x04 \x01(\x0b2\x1b.eve.corporation.Identifier\x12-\n\x08previous\x18\x05 \x01(\x0e2\x1b.eve.structure.upwell.State\x12,\n\x07current\x18\x06 \x01(\x0e2\x1b.eve.structure.upwell.StateBEZCgithub.com/ccpgames/eve-proto-go/generated/eve/structure/upwell/apib\x06proto3', dependencies=[eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR,
 eve_dot_solarsystem_dot_solarsystem__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__pb2.DESCRIPTOR,
 eve_dot_structure_dot_structure__type__pb2.DESCRIPTOR,
 eve_dot_structure_dot_upwell_dot_state__pb2.DESCRIPTOR])
_STATETRANSITIONED = _descriptor.Descriptor(name='StateTransitioned', full_name='eve.structure.upwell.api.StateTransitioned', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='structure', full_name='eve.structure.upwell.api.StateTransitioned.structure', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='upwell_type', full_name='eve.structure.upwell.api.StateTransitioned.upwell_type', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='solarsystem', full_name='eve.structure.upwell.api.StateTransitioned.solarsystem', index=2, number=3, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='corporation', full_name='eve.structure.upwell.api.StateTransitioned.corporation', index=3, number=4, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='previous', full_name='eve.structure.upwell.api.StateTransitioned.previous', index=4, number=5, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
 _descriptor.FieldDescriptor(name='current', full_name='eve.structure.upwell.api.StateTransitioned.current', index=5, number=6, type=14, cpp_type=8, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=239, serialized_end=549)
_STATETRANSITIONED.fields_by_name['structure'].message_type = eve_dot_structure_dot_structure__pb2._IDENTIFIER
_STATETRANSITIONED.fields_by_name['upwell_type'].message_type = eve_dot_structure_dot_structure__type__pb2._IDENTIFIER
_STATETRANSITIONED.fields_by_name['solarsystem'].message_type = eve_dot_solarsystem_dot_solarsystem__pb2._IDENTIFIER
_STATETRANSITIONED.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_STATETRANSITIONED.fields_by_name['previous'].enum_type = eve_dot_structure_dot_upwell_dot_state__pb2._STATE
_STATETRANSITIONED.fields_by_name['current'].enum_type = eve_dot_structure_dot_upwell_dot_state__pb2._STATE
DESCRIPTOR.message_types_by_name['StateTransitioned'] = _STATETRANSITIONED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
StateTransitioned = _reflection.GeneratedProtocolMessageType('StateTransitioned', (_message.Message,), {'DESCRIPTOR': _STATETRANSITIONED,
 '__module__': 'eve.structure.upwell.api.events_pb2'})
_sym_db.RegisterMessage(StateTransitioned)
DESCRIPTOR._options = None
