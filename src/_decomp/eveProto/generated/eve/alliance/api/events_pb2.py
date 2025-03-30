#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\alliance\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/alliance/api/events.proto', package='eve.alliance.api', syntax='proto3', serialized_options='Z;github.com/ccpgames/eve-proto-go/generated/eve/alliance/api', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1deve/alliance/api/events.proto\x12\x10eve.alliance.api\x1a\x1beve/alliance/alliance.proto\x1a!eve/corporation/corporation.proto"5\n\x07Created\x12*\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.Identifier"j\n\tDisbanded\x12*\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.Identifier\x121\n\x0ccorporations\x18\x02 \x03(\x0b2\x1b.eve.corporation.IdentifierB=Z;github.com/ccpgames/eve-proto-go/generated/eve/alliance/apib\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve.alliance.api.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.alliance.api.Created.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=115, serialized_end=168)
_DISBANDED = _descriptor.Descriptor(name='Disbanded', full_name='eve.alliance.api.Disbanded', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.alliance.api.Disbanded.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporations', full_name='eve.alliance.api.Disbanded.corporations', index=1, number=2, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=170, serialized_end=276)
_CREATED.fields_by_name['alliance'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_DISBANDED.fields_by_name['alliance'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_DISBANDED.fields_by_name['corporations'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
DESCRIPTOR.message_types_by_name['Disbanded'] = _DISBANDED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve.alliance.api.events_pb2'})
_sym_db.RegisterMessage(Created)
Disbanded = _reflection.GeneratedProtocolMessageType('Disbanded', (_message.Message,), {'DESCRIPTOR': _DISBANDED,
 '__module__': 'eve.alliance.api.events_pb2'})
_sym_db.RegisterMessage(Disbanded)
DESCRIPTOR._options = None
