#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\line\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.line import line_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/line/api/events.proto', package='eve.cosmetic.ship.skin.thirdparty.line.api', syntax='proto3', serialized_options='ZUgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/line/api', create_key=_descriptor._internal_create_key, serialized_pb='\n7eve/cosmetic/ship/skin/thirdparty/line/api/events.proto\x12*eve.cosmetic.ship.skin.thirdparty.line.api\x1a1eve/cosmetic/ship/skin/thirdparty/line/line.proto"\x91\x01\n\x07Created\x12>\n\x02id\x18\x01 \x01(\x0b22.eve.cosmetic.ship.skin.thirdparty.line.Identifier\x12F\n\nattributes\x18\x02 \x01(\x0b22.eve.cosmetic.ship.skin.thirdparty.line.AttributesBWZUgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/line/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2.DESCRIPTOR])
_CREATED = _descriptor.Descriptor(name='Created', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.Created', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.Created.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.cosmetic.ship.skin.thirdparty.line.api.Created.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=155, serialized_end=300)
_CREATED.fields_by_name['id'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2._IDENTIFIER
_CREATED.fields_by_name['attributes'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_line_dot_line__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Created'] = _CREATED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Created = _reflection.GeneratedProtocolMessageType('Created', (_message.Message,), {'DESCRIPTOR': _CREATED,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.line.api.events_pb2'})
_sym_db.RegisterMessage(Created)
DESCRIPTOR._options = None
