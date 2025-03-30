#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\war\entity_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.alliance import alliance_pb2 as eve_dot_alliance_dot_alliance__pb2
from eveProto.generated.eve.corporation import corporation_pb2 as eve_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/war/entity.proto', package='eve.war.entity', syntax='proto3', serialized_options='Z9github.com/ccpgames/eve-proto-go/generated/eve/war/entity', create_key=_descriptor._internal_create_key, serialized_pb='\n\x14eve/war/entity.proto\x12\x0eeve.war.entity\x1a\x1beve/alliance/alliance.proto\x1a!eve/corporation/corporation.proto"u\n\nIdentifier\x12,\n\x08alliance\x18\x01 \x01(\x0b2\x18.eve.alliance.IdentifierH\x00\x122\n\x0bcorporation\x18\x02 \x01(\x0b2\x1b.eve.corporation.IdentifierH\x00B\x05\n\x03ids"\x0c\n\nAttributesB;Z9github.com/ccpgames/eve-proto-go/generated/eve/war/entityb\x06proto3', dependencies=[eve_dot_alliance_dot_alliance__pb2.DESCRIPTOR, eve_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.war.entity.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve.war.entity.Identifier.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve.war.entity.Identifier.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='ids', full_name='eve.war.entity.Identifier.ids', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=104, serialized_end=221)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve.war.entity.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=223, serialized_end=235)
_IDENTIFIER.fields_by_name['alliance'].message_type = eve_dot_alliance_dot_alliance__pb2._IDENTIFIER
_IDENTIFIER.fields_by_name['corporation'].message_type = eve_dot_corporation_dot_corporation__pb2._IDENTIFIER
_IDENTIFIER.oneofs_by_name['ids'].fields.append(_IDENTIFIER.fields_by_name['alliance'])
_IDENTIFIER.fields_by_name['alliance'].containing_oneof = _IDENTIFIER.oneofs_by_name['ids']
_IDENTIFIER.oneofs_by_name['ids'].fields.append(_IDENTIFIER.fields_by_name['corporation'])
_IDENTIFIER.fields_by_name['corporation'].containing_oneof = _IDENTIFIER.oneofs_by_name['ids']
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.war.entity_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve.war.entity_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
