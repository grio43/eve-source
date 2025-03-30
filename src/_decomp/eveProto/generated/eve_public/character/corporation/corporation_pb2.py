#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\character\corporation\corporation_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.corporation import corporation_pb2 as eve__public_dot_corporation_dot_corporation__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/character/corporation/corporation.proto', package='eve_public.character.corporation', syntax='proto3', serialized_options='ZKgithub.com/ccpgames/eve-proto-go/generated/eve_public/character/corporation', create_key=_descriptor._internal_create_key, serialized_pb='\n2eve_public/character/corporation/corporation.proto\x12 eve_public.character.corporation\x1a(eve_public/corporation/corporation.proto"\x91\x01\n\x11TransferredNotice\x12<\n\x10corporation_left\x18\x01 \x01(\x0b2".eve_public.corporation.Identifier\x12>\n\x12corporation_joined\x18\x02 \x01(\x0b2".eve_public.corporation.IdentifierBMZKgithub.com/ccpgames/eve-proto-go/generated/eve_public/character/corporationb\x06proto3', dependencies=[eve__public_dot_corporation_dot_corporation__pb2.DESCRIPTOR])
_TRANSFERREDNOTICE = _descriptor.Descriptor(name='TransferredNotice', full_name='eve_public.character.corporation.TransferredNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='corporation_left', full_name='eve_public.character.corporation.TransferredNotice.corporation_left', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation_joined', full_name='eve_public.character.corporation.TransferredNotice.corporation_joined', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=131, serialized_end=276)
_TRANSFERREDNOTICE.fields_by_name['corporation_left'].message_type = eve__public_dot_corporation_dot_corporation__pb2._IDENTIFIER
_TRANSFERREDNOTICE.fields_by_name['corporation_joined'].message_type = eve__public_dot_corporation_dot_corporation__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['TransferredNotice'] = _TRANSFERREDNOTICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
TransferredNotice = _reflection.GeneratedProtocolMessageType('TransferredNotice', (_message.Message,), {'DESCRIPTOR': _TRANSFERREDNOTICE,
 '__module__': 'eve_public.character.corporation.corporation_pb2'})
_sym_db.RegisterMessage(TransferredNotice)
DESCRIPTOR._options = None
