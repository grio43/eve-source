#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\dogma\modifier\dbuff_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/dogma/modifier/dbuff.proto', package='eve.dogma.modifier.dbuff', syntax='proto3', serialized_options='ZCgithub.com/ccpgames/eve-proto-go/generated/eve/dogma/modifier/dbuff', create_key=_descriptor._internal_create_key, serialized_pb='\n\x1eeve/dogma/modifier/dbuff.proto\x12\x18eve.dogma.modifier.dbuff" \n\nIdentifier\x12\x12\n\nsequential\x18\x01 \x01(\x04")\n\tMagnitude\x12\r\n\x05units\x18\x01 \x01(\x11\x12\r\n\x05nanos\x18\x02 \x01(\x11BEZCgithub.com/ccpgames/eve-proto-go/generated/eve/dogma/modifier/dbuffb\x06proto3')
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve.dogma.modifier.dbuff.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='sequential', full_name='eve.dogma.modifier.dbuff.Identifier.sequential', index=0, number=1, type=4, cpp_type=4, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=60, serialized_end=92)
_MAGNITUDE = _descriptor.Descriptor(name='Magnitude', full_name='eve.dogma.modifier.dbuff.Magnitude', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='units', full_name='eve.dogma.modifier.dbuff.Magnitude.units', index=0, number=1, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='nanos', full_name='eve.dogma.modifier.dbuff.Magnitude.nanos', index=1, number=2, type=17, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=94, serialized_end=135)
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Magnitude'] = _MAGNITUDE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve.dogma.modifier.dbuff_pb2'})
_sym_db.RegisterMessage(Identifier)
Magnitude = _reflection.GeneratedProtocolMessageType('Magnitude', (_message.Message,), {'DESCRIPTOR': _MAGNITUDE,
 '__module__': 'eve.dogma.modifier.dbuff_pb2'})
_sym_db.RegisterMessage(Magnitude)
DESCRIPTOR._options = None
