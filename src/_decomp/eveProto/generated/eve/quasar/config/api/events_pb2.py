#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\generated\eve\quasar\config\api\events_pb2.py
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from eveProto.generated.eve.quasar.config import config_pb2 as eve_dot_quasar_dot_config_dot_config__pb2
DESCRIPTOR = _descriptor.FileDescriptor(name='eve/quasar/config/api/events.proto', package='eve.quasar.config.api', syntax='proto3', serialized_options='Z@github.com/ccpgames/eve-proto-go/generated/eve/quasar/config/api', create_key=_descriptor._internal_create_key, serialized_pb='\n"eve/quasar/config/api/events.proto\x12\x15eve.quasar.config.api\x1a\x1eeve/quasar/config/config.proto"g\n\x07Changed\x12)\n\x02id\x18\x01 \x01(\x0b2\x1d.eve.quasar.config.Identifier\x121\n\nattributes\x18\x02 \x01(\x0b2\x1d.eve.quasar.config.AttributesBBZ@github.com/ccpgames/eve-proto-go/generated/eve/quasar/config/apib\x06proto3', dependencies=[eve_dot_quasar_dot_config_dot_config__pb2.DESCRIPTOR])
_CHANGED = _descriptor.Descriptor(name='Changed', full_name='eve.quasar.config.api.Changed', filename=None, file=DESCRIPTOR, containing_type=None, create_key=_descriptor._internal_create_key, fields=[_descriptor.FieldDescriptor(name='id', full_name='eve.quasar.config.api.Changed.id', index=0, number=1, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key), _descriptor.FieldDescriptor(name='attributes', full_name='eve.quasar.config.api.Changed.attributes', index=1, number=2, type=11, cpp_type=10, label=1, has_default_value=False, default_value=None, message_type=None, enum_type=None, containing_type=None, is_extension=False, extension_scope=None, serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key)], extensions=[], nested_types=[], enum_types=[], serialized_options=None, is_extendable=False, syntax='proto3', extension_ranges=[], oneofs=[], serialized_start=93, serialized_end=196)
_CHANGED.fields_by_name['id'].message_type = eve_dot_quasar_dot_config_dot_config__pb2._IDENTIFIER
_CHANGED.fields_by_name['attributes'].message_type = eve_dot_quasar_dot_config_dot_config__pb2._ATTRIBUTES
DESCRIPTOR.message_types_by_name['Changed'] = _CHANGED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)
Changed = _reflection.GeneratedProtocolMessageType('Changed', (_message.Message,), {'DESCRIPTOR': _CHANGED,
 '__module__': 'eve.quasar.config.api.events_pb2'})
_sym_db.RegisterMessage(Changed)
DESCRIPTOR._options = None
