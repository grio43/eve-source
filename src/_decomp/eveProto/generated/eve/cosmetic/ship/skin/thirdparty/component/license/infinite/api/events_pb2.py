#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\cosmetic\ship\skin\thirdparty\component\license\infinite\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.cosmetic.ship.skin.thirdparty.component.license.infinite import infinite_pb2 as eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_infinite_dot_infinite__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/cosmetic/ship/skin/thirdparty/component/license/infinite/api/events.proto', package='eve.cosmetic.ship.skin.thirdparty.component.license.infinite.api', syntax='proto3', serialized_options='Zkgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/infinite/api', create_key=_descriptor._internal_create_key, serialized_pb='\nMeve/cosmetic/ship/skin/thirdparty/component/license/infinite/api/events.proto\x12@eve.cosmetic.ship.skin.thirdparty.component.license.infinite.api\x1aKeve/cosmetic/ship/skin/thirdparty/component/license/infinite/infinite.proto"a\n\x04Used\x12Y\n\x07license\x18\x01 \x01(\x0b2H.eve.cosmetic.ship.skin.thirdparty.component.license.infinite.IdentifierBmZkgithub.com/ccpgames/eve-proto-go/generated/eve/cosmetic/ship/skin/thirdparty/component/license/infinite/apib\x06proto3', dependencies=[eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_infinite_dot_infinite__pb2.DESCRIPTOR])
_USED = _descriptor.Descriptor(name='Used', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.infinite.api.Used', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='license', full_name='eve.cosmetic.ship.skin.thirdparty.component.license.infinite.api.Used.license', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=224, serialized_end=321)
_USED.fields_by_name['license'].message_type = eve_dot_cosmetic_dot_ship_dot_skin_dot_thirdparty_dot_component_dot_license_dot_infinite_dot_infinite__pb2._IDENTIFIER
DESCRIPTOR.message_types_by_name['Used'] = _USED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Used = _reflection.GeneratedProtocolMessageType('Used', (_message.Message,), {'DESCRIPTOR': _USED,
 '__module__': 'eve.cosmetic.ship.skin.thirdparty.component.license.infinite.api.events_pb2'})
_sym_db.RegisterMessage(Used)
DESCRIPTOR._options = None
