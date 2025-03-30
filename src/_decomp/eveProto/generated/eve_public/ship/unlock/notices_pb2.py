#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\ship\unlock\notices_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.ship import ship_type_pb2 as eve__public_dot_ship_dot_ship__type__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/ship/unlock/notices.proto', package='eve_public.ship.unlock', syntax='proto3', serialized_options='ZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/ship/unlock', create_key=_descriptor._internal_create_key, serialized_pb='\n$eve_public/ship/unlock/notices.proto\x12\x16eve_public.ship.unlock\x1a\x1feve_public/ship/ship_type.proto"S\n\x13ShipsUnlockedNotice\x12<\n\x13unlocked_ship_types\x18\x01 \x03(\x0b2\x1f.eve_public.shiptype.IdentifierBCZAgithub.com/ccpgames/eve-proto-go/generated/eve_public/ship/unlockb\x06proto3', dependencies=[eve__public_dot_ship_dot_ship__type__pb2.DESCRIPTOR])
_SHIPSUNLOCKEDNOTICE = _descriptor.Descriptor(name='ShipsUnlockedNotice', full_name='eve_public.ship.unlock.ShipsUnlockedNotice', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='unlocked_ship_types', full_name='eve_public.ship.unlock.ShipsUnlockedNotice.unlocked_ship_types', index=0, number=1, type=11, cpp_type=10, label=3, has_default_value=False, default_value=[], message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=97, serialized_end=180)
_SHIPSUNLOCKEDNOTICE.fields_by_name['unlocked_ship_types'].message_type = eve__public_dot_ship_dot_ship__type__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['ShipsUnlockedNotice'] = _SHIPSUNLOCKEDNOTICE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
ShipsUnlockedNotice = _reflection.GeneratedProtocolMessageType('ShipsUnlockedNotice', (_message.Message,), {'DESCRIPTOR': _SHIPSUNLOCKEDNOTICE,
 '__module__': 'eve_public.ship.unlock.notices_pb2'})
_sym_db.RegisterMessage(ShipsUnlockedNotice)
DESCRIPTOR._options = None
