#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve_public\cosmetic\ship\logo\logo_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve_public.ship import ship_pb2 as eve__public_dot_ship_dot_ship__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve_public/cosmetic/ship/logo/logo.proto', package='eve_public.cosmetic.ship.logo', syntax='proto3', serialized_options='ZHgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/logo', create_key=_descriptor._internal_create_key, serialized_pb='\n(eve_public/cosmetic/ship/logo/logo.proto\x12\x1deve_public.cosmetic.ship.logo\x1a\x1aeve_public/ship/ship.proto"F\n\nIdentifier\x12)\n\x04ship\x18\x01 \x01(\x0b2\x1b.eve_public.ship.Identifier\x12\r\n\x05index\x18\x02 \x01(\x05"\x99\x01\n\nAttributes\x12;\n\x08alliance\x18\x01 \x01(\x0b2\'.eve_public.cosmetic.ship.logo.AllianceH\x00\x12A\n\x0bcorporation\x18\x02 \x01(\x0b2*.eve_public.cosmetic.ship.logo.CorporationH\x00B\x0b\n\tlogo_type"\n\n\x08Alliance"\r\n\x0bCorporation"G\n\x0cClearRequest\x127\n\x04logo\x18\x01 \x01(\x0b2).eve_public.cosmetic.ship.logo.Identifier"\x0f\n\rClearResponse"\x80\x01\n\x0eDisplayRequest\x125\n\x02id\x18\x01 \x01(\x0b2).eve_public.cosmetic.ship.logo.Identifier\x127\n\x04attr\x18\x02 \x01(\x0b2).eve_public.cosmetic.ship.logo.Attributes"\x11\n\x0fDisplayResponseBJZHgithub.com/ccpgames/eve-proto-go/generated/eve_public/cosmetic/ship/logob\x06proto3', dependencies=[eve__public_dot_ship_dot_ship__pb2.DESCRIPTOR])
_IDENTIFIER = _descriptor.Descriptor(name='Identifier', full_name='eve_public.cosmetic.ship.logo.Identifier', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='ship', full_name='eve_public.cosmetic.ship.logo.Identifier.ship', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='index', full_name='eve_public.cosmetic.ship.logo.Identifier.index', index=1, number=2, type=5, cpp_type=1, label=1, has_default_value=False, default_value=0, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=103, serialized_end=173)
_ATTRIBUTES = _descriptor.Descriptor(name='Attributes', full_name='eve_public.cosmetic.ship.logo.Attributes', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='alliance', full_name='eve_public.cosmetic.ship.logo.Attributes.alliance', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='corporation', full_name='eve_public.cosmetic.ship.logo.Attributes.corporation', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[_descriptor.OneofDescriptor(name='logo_type', full_name='eve_public.cosmetic.ship.logo.Attributes.logo_type', index=0, containing_type=None, create_key=_descriptor._internal_create_key, fields=[])], serialized_start=176, serialized_end=329)
_ALLIANCE = _descriptor.Descriptor(name='Alliance', full_name='eve_public.cosmetic.ship.logo.Alliance', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=331, serialized_end=341)
_CORPORATION = _descriptor.Descriptor(name='Corporation', full_name='eve_public.cosmetic.ship.logo.Corporation', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=343, serialized_end=356)
_CLEARREQUEST = _descriptor.Descriptor(name='ClearRequest', full_name='eve_public.cosmetic.ship.logo.ClearRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='logo', full_name='eve_public.cosmetic.ship.logo.ClearRequest.logo', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=358, serialized_end=429)
_CLEARRESPONSE = _descriptor.Descriptor(name='ClearResponse', full_name='eve_public.cosmetic.ship.logo.ClearResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=431, serialized_end=446)
_DISPLAYREQUEST = _descriptor.Descriptor(name='DisplayRequest', full_name='eve_public.cosmetic.ship.logo.DisplayRequest', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve_public.cosmetic.ship.logo.DisplayRequest.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attr', full_name='eve_public.cosmetic.ship.logo.DisplayRequest.attr', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=449, serialized_end=577)
_DISPLAYRESPONSE = _descriptor.Descriptor(name='DisplayResponse', full_name='eve_public.cosmetic.ship.logo.DisplayResponse', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=579, serialized_end=596)
_IDENTIFIER.fields_by_name['ship'].message_type = eve__public_dot_ship_dot_ship__pb2._IDENTIFIER
_ATTRIBUTES.fields_by_name['alliance'].message_type = _ALLIANCE
_ATTRIBUTES.fields_by_name['corporation'].message_type = _CORPORATION
_ATTRIBUTES.oneofs_by_name['logo_type'].fields.append(_ATTRIBUTES.fields_by_name['alliance'])
_ATTRIBUTES.fields_by_name['alliance'].containing_oneof = _ATTRIBUTES.oneofs_by_name['logo_type']
_ATTRIBUTES.oneofs_by_name['logo_type'].fields.append(_ATTRIBUTES.fields_by_name['corporation'])
_ATTRIBUTES.fields_by_name['corporation'].containing_oneof = _ATTRIBUTES.oneofs_by_name['logo_type']
_CLEARREQUEST.fields_by_name['logo'].message_type = _IDENTIFIER
_DISPLAYREQUEST.fields_by_name['id'].message_type = _IDENTIFIER
_DISPLAYREQUEST.fields_by_name['attr'].message_type = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Identifier'] = _IDENTIFIER
DESCRIPTOR.message_types_by_name['Attributes'] = _ATTRIBUTES
DESCRIPTOR.message_types_by_name['Alliance'] = _ALLIANCE
DESCRIPTOR.message_types_by_name['Corporation'] = _CORPORATION
DESCRIPTOR.message_types_by_name['ClearRequest'] = _CLEARREQUEST
DESCRIPTOR.message_types_by_name['ClearResponse'] = _CLEARRESPONSE
DESCRIPTOR.message_types_by_name['DisplayRequest'] = _DISPLAYREQUEST
DESCRIPTOR.message_types_by_name['DisplayResponse'] = _DISPLAYRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Identifier = _reflection.GeneratedProtocolMessageType('Identifier', (_message.Message,), {'DESCRIPTOR': _IDENTIFIER,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Identifier)
Attributes = _reflection.GeneratedProtocolMessageType('Attributes', (_message.Message,), {'DESCRIPTOR': _ATTRIBUTES,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Attributes)
Alliance = _reflection.GeneratedProtocolMessageType('Alliance', (_message.Message,), {'DESCRIPTOR': _ALLIANCE,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Alliance)
Corporation = _reflection.GeneratedProtocolMessageType('Corporation', (_message.Message,), {'DESCRIPTOR': _CORPORATION,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(Corporation)
ClearRequest = _reflection.GeneratedProtocolMessageType('ClearRequest', (_message.Message,), {'DESCRIPTOR': _CLEARREQUEST,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(ClearRequest)
ClearResponse = _reflection.GeneratedProtocolMessageType('ClearResponse', (_message.Message,), {'DESCRIPTOR': _CLEARRESPONSE,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(ClearResponse)
DisplayRequest = _reflection.GeneratedProtocolMessageType('DisplayRequest', (_message.Message,), {'DESCRIPTOR': _DISPLAYREQUEST,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(DisplayRequest)
DisplayResponse = _reflection.GeneratedProtocolMessageType('DisplayResponse', (_message.Message,), {'DESCRIPTOR': _DISPLAYRESPONSE,
 '__module__': 'eve_public.cosmetic.ship.logo.logo_pb2'})
_sym_db.RegisterMessage(DisplayResponse)
DESCRIPTOR._options = None
