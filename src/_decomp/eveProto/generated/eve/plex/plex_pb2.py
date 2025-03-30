#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\plex\plex_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/plex/plex.proto', package='eve.plex', syntax='proto3', serialized_options='Z3github.com/ccpgames/eve-proto-go/generated/eve/plex', create_key=_descriptor._internal_create_key, serialized_pb='\n\x13eve/plex/plex.proto\x12\x08eve.plex""\n\x08Currency\x12\x16\n\x0etotal_in_cents\x18\x01 \x01(\x12B5Z3github.com/ccpgames/eve-proto-go/generated/eve/plexb\x06proto3')
_CURRENCY = _descriptor.Descriptor(name='Currency', full_name='eve.plex.Currency', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='total_in_cents', full_name='eve.plex.Currency.total_in_cents', index=0, number=1, type=18, cpp_type=2, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=33, serialized_end=67)
DESCRIPTOR.message_types_by_name['Currency'] = _CURRENCY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Currency = _reflection.GeneratedProtocolMessageType('Currency', (_message.Message,), {'DESCRIPTOR': _CURRENCY,
 '__module__': 'eve.plex.plex_pb2'})
_sym_db.RegisterMessage(Currency)
DESCRIPTOR._options = None
