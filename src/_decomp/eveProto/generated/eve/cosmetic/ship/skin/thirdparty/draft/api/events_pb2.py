#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\draft\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.draft import draft_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_draft_dot_draft__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/draft/api/events.proto', package='eve.cosmetic.ship.skin.thirdparty.draft.api', syntax='proto3', serialized_options='ZVgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/draft/api', create_key=_descriptor._internal_create_key, serialized_pb='\n8eve/cosmetic/ship/skin/thirdparty/draft/api/events.proto\x12+eve.cosmetic.ship.skin.thirdparty.draft.api\x1a3eve/cosmetic/ship/skin/thirdparty/draft/draft.proto"\x94\x01\n\x05Saved\x12B\n\x05draft\x18\x01 \x01(\x0b23.eve.cosmetic.ship.skin.thirdparty.draft.Identifier\x12G\n\nattributes\x18\x02 \x01(\x0b23.eve.cosmetic.ship.skin.thirdparty.draft.Attributes"M\n\x07Deleted\x12B\n\x05draft\x18\x01 \x01(\x0b23.eve.cosmetic.ship.skin.thirdparty.draft.IdentifierBXZVgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/draft/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_draft_dot_draft__pb2.DESCRIPTOR])
_SAVED = _descriptor.Descriptor(name='Saved', full_name='eve.cosmetic.ship.skin.thirdparty.draft.api.Saved', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='draft', full_name='eve.cosmetic.ship.skin.thirdparty.draft.api.Saved.draft', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.ship.skin.thirdparty.draft.api.Saved.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=159, serialized_end=307)
_DELETED = _descriptor.Descriptor(name='Deleted', full_name='eve.cosmetic.ship.skin.thirdparty.draft.api.Deleted', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='draft', full_name='eve.cosmetic.ship.skin.thirdparty.draft.api.Deleted.draft', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=309, serialized_end=386)
_SAVED.fields_by_name['draft'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_draft_dot_draft__pb2._IDENTIFIER
_SAVED.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_draft_dot_draft__pb2._ATTRIBUTES
_DELETED.fields_by_name['draft'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_draft_dot_draft__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Saved'] = _SAVED
DESCRIPTOR.message_types_by_name['Deleted'] = _DELETED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Saved = _reflection.GeneratedProtocolMessageType('Saved', (_message.Message,), {'DESCRIPTOR': _SAVED,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.draft.api.events_pb2'})
_sym_db.RegisterMessage(Saved)
Deleted = _reflection.GeneratedProtocolMessageType('Deleted', (_message.Message,), {'DESCRIPTOR': _DELETED,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.draft.api.events_pb2'})
_sym_db.RegisterMessage(Deleted)
DESCRIPTOR._options = None
