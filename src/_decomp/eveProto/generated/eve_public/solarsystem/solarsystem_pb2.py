#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\solarsystem\solarsystem_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.securitystatus import securitystatus_pb2 as eve__public_dot_securitystatus_dot_securitystatus__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/solarsystem/solarsystem.proto', package='eve_public.solarsystem', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/solarsystem', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve_public/solarsystem/solarsystem.proto\x12\x16eve_public.solarsystem\x1a.eve_public/securitystatus/securitystatus.proto" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04"N\n\nAttributes\x12\x0c\n\x04name\x18\x01 \x01(\t\x122\n\x08security\x18\x02 \x01(\x0b2 .eve_public.securitystatus.ValueBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/solarsystemb\x06proto3', dependencies=[eve__public_dot_securitystatus_dot_securitystatus__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.solarsystem.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve_public.solarsystem.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=116, serialized_end=148)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve_public.solarsystem.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='name', full_name='eve_public.solarsystem.Attributes.name', index=0, number=1, type=9, cpp_type=9, label=1, has_default_value=False, default_value=''.decode('utf-8'), message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='security', full_name='eve_public.solarsystem.Attributes.security', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=150, serialized_end=228)
_ATTRIBUTES.fields_by_name['security'].message_type = eve__public_dot_securitystatus_dot_securitystatus__pb2._VALUE
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.solarsystem.solarsystem_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve_public.solarsystem.solarsystem_pb2'})
_sym_db.RegisterMessage(Attributes)
DESCRIPTOR._options = None
